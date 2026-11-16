"""Минимальная реализация SemVer: сравнение версий и диапазоны npm.

Нужна, чтобы выбрать версию транзитивной зависимости по диапазону из
package.json (^1.2.0, ~2.0.1, >=1 <3, 1.x || 2.x, 1.0.0 - 2.0.0 и т. п.).
Сторонние библиотеки не используются.
"""

import re

VERSION = re.compile(
    r"^\s*v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?\s*$"
)
PARTIAL = re.compile(
    r"^v?(\d+|[xX*])?(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)
COMPARATOR = re.compile(r"^(<=|>=|<|>|=|\^|~>?)?\s*(.*)$")
WILDCARDS = (None, "x", "X", "*")


class RangeError(ValueError):
    """Строка не является диапазоном версий npm."""


class Version:
    """Версия SemVer с правилами сравнения из спецификации."""

    def __init__(self, major, minor, patch, prerelease=()):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = tuple(prerelease)

    @classmethod
    def parse(cls, text):
        """Разбирает строку '1.2.3-beta.1'; None, если формат неверный."""
        match = VERSION.match(text)
        if not match:
            return None
        pre = match.group(4)
        return cls(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            pre.split(".") if pre else (),
        )

    def core(self):
        """Тройка (major, minor, patch)."""
        return (self.major, self.minor, self.patch)

    def _pre_key(self):
        # Версия без prerelease старше любой prerelease-версии.
        if not self.prerelease:
            return (1,)
        parts = []
        for item in self.prerelease:
            if item.isdigit():
                parts.append((0, int(item), ""))
            else:
                parts.append((1, 0, item))
        return (0, tuple(parts))

    def key(self):
        """Ключ для сравнения версий."""
        return (self.core(), self._pre_key())

    def __eq__(self, other):
        return self.key() == other.key()

    def __lt__(self, other):
        return self.key() < other.key()

    def __le__(self, other):
        return self.key() <= other.key()

    def __gt__(self, other):
        return self.key() > other.key()

    def __ge__(self, other):
        return self.key() >= other.key()

    def __hash__(self):
        return hash(self.key())

    def __str__(self):
        text = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            text += "-" + ".".join(self.prerelease)
        return text


class Comparator:
    """Одно условие: оператор и версия, например >=1.2.0."""

    def __init__(self, operator, version, explicit_pre=False):
        self.operator = operator
        self.version = version
        # Prerelease указан пользователем (а не добавлен как '-0').
        self.explicit_pre = explicit_pre

    def test(self, version):
        """Проверяет, удовлетворяет ли версия условию."""
        if self.operator == "<":
            return version < self.version
        if self.operator == "<=":
            return version <= self.version
        if self.operator == ">":
            return version > self.version
        if self.operator == ">=":
            return version >= self.version
        return version == self.version


def lowest(major, minor=0, patch=0):
    """Самая младшая версия X.Y.Z-0 (ниже любых prerelease)."""
    return Version(major, minor, patch, ("0",))


def parse_partial(text):
    """Разбирает частичную версию '1', '1.2', '1.x', '*'.

    Возвращает (major, minor, patch, prerelease), где отсутствующие или
    подстановочные части равны None.
    """
    match = PARTIAL.match(text)
    if not match:
        raise RangeError(f"некорректная версия '{text}'")
    parts = []
    wildcard = False
    for item in match.group(1, 2, 3):
        if wildcard or item in WILDCARDS:
            wildcard = True
            parts.append(None)
        else:
            parts.append(int(item))
    pre = match.group(4)
    prerelease = tuple(pre.split(".")) if pre and parts[2] is not None else ()
    return parts[0], parts[1], parts[2], prerelease


def x_range(major, minor, patch, pre):
    """Условия для 'X', 'X.Y', 'X.Y.Z' без оператора."""
    if major is None:
        return [Comparator(">=", Version(0, 0, 0))]
    if minor is None:
        return [
            Comparator(">=", Version(major, 0, 0)),
            Comparator("<", lowest(major + 1)),
        ]
    if patch is None:
        return [
            Comparator(">=", Version(major, minor, 0)),
            Comparator("<", lowest(major, minor + 1)),
        ]
    return [Comparator("=", Version(major, minor, patch, pre), bool(pre))]


def tilde(major, minor, patch, pre):
    """~1.2.3 := >=1.2.3 <1.3.0-0; ~1.2 := >=1.2.0 <1.3.0-0; ~1 := 1.x."""
    if major is None or minor is None:
        return x_range(major, minor, patch, pre)
    start = Version(major, minor, patch or 0, pre)
    return [
        Comparator(">=", start, bool(pre)),
        Comparator("<", lowest(major, minor + 1)),
    ]


def caret(major, minor, patch, pre):
    """^ разрешает изменения, не трогающие первую ненулевую часть."""
    if major is None:
        return x_range(None, None, None, ())
    start = Version(major, minor or 0, patch or 0, pre)
    if major > 0 or minor is None:
        end = lowest(major + 1)
    elif minor > 0 or patch is None:
        end = lowest(0, minor + 1)
    else:
        end = lowest(0, 0, patch + 1)
    return [Comparator(">=", start, bool(pre)), Comparator("<", end)]


def compare_partial(operator, major, minor, patch, pre):
    """Условия для >, >=, <, <=, = с частичной версией."""
    if operator == "=":
        return x_range(major, minor, patch, pre)
    if major is None:
        if operator in ("<", ">"):
            # '<*' и '>*' не допускают ни одной версии.
            return [Comparator("<", lowest(0))]
        return [Comparator(">=", Version(0, 0, 0))]
    if patch is not None:
        return [Comparator(operator, Version(major, minor, patch, pre), bool(pre))]
    if operator == ">=":
        return [Comparator(">=", Version(major, minor or 0, 0))]
    if operator == "<":
        return [Comparator("<", lowest(major, minor or 0))]
    if operator == ">":
        if minor is None:
            return [Comparator(">=", Version(major + 1, 0, 0))]
        return [Comparator(">=", Version(major, minor + 1, 0))]
    # operator == "<="
    if minor is None:
        return [Comparator("<", lowest(major + 1))]
    return [Comparator("<", lowest(major, minor + 1))]


def parse_comparator(token):
    """Переводит одно условие ('^1.2', '>=2', '1.x') в список Comparator."""
    match = COMPARATOR.match(token)
    operator = match.group(1) or ""
    major, minor, patch, pre = parse_partial(match.group(2).strip())
    if operator == "":
        return x_range(major, minor, patch, pre)
    if operator.startswith("~"):
        return tilde(major, minor, patch, pre)
    if operator == "^":
        return caret(major, minor, patch, pre)
    return compare_partial(operator, major, minor, patch, pre)


def hyphen(left, right):
    """'1.2 - 2.3.4' := >=1.2.0 <=2.3.4; правая частичная — '<' следующей."""
    major, minor, patch, pre = parse_partial(left)
    result = []
    if major is not None:
        start = Version(major, minor or 0, patch or 0, pre)
        result.append(Comparator(">=", start, bool(pre)))
    major, minor, patch, pre = parse_partial(right)
    if major is None:
        pass
    elif minor is None:
        result.append(Comparator("<", lowest(major + 1)))
    elif patch is None:
        result.append(Comparator("<", lowest(major, minor + 1)))
    else:
        result.append(Comparator("<=", Version(major, minor, patch, pre), bool(pre)))
    return result or [Comparator(">=", Version(0, 0, 0))]


def tokenize(text):
    """Разбивает набор условий на элементы, склеивая '>= 1.2' в '>=1.2'."""
    tokens = []
    pending = ""
    for item in text.split():
        if item in ("<", "<=", ">", ">=", "=", "^", "~", "~>"):
            pending += item
            continue
        tokens.append(pending + item)
        pending = ""
    if pending:
        raise RangeError(f"оператор '{pending}' без версии")
    return tokens


class Range:
    """Диапазон версий npm: наборы условий, объединённые через ||."""

    def __init__(self, text):
        self.text = text
        self.sets = []
        for part in text.split("||"):
            part = part.strip()
            hyphen_match = re.match(r"^(\S+)\s+-\s+(\S+)$", part)
            if hyphen_match:
                self.sets.append(hyphen(*hyphen_match.groups()))
                continue
            comparators = []
            for token in tokenize(part) or ["*"]:
                comparators.extend(parse_comparator(token))
            self.sets.append(comparators)

    @staticmethod
    def _set_test(comparators, version):
        if not all(item.test(version) for item in comparators):
            return False
        if not version.prerelease:
            return True
        # Prerelease подходит, только если в наборе явно есть prerelease
        # той же тройки major.minor.patch.
        return any(
            item.explicit_pre and item.version.core() == version.core()
            for item in comparators
        )

    def test(self, version):
        """Проверяет, входит ли версия в диапазон."""
        return any(self._set_test(items, version) for items in self.sets)


def max_satisfying(versions, range_text):
    """Наибольшая версия из списка строк, входящая в диапазон, или None."""
    rng = Range(range_text)
    best = None
    for text in versions:
        version = Version.parse(text)
        if version and rng.test(version) and (best is None or version > best[0]):
            best = (version, text)
    return best[1] if best else None
