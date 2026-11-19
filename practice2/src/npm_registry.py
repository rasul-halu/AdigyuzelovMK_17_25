"""Получение данных о пакетах из npm-репозитория по HTTP.

Используется только стандартная библиотека: метаданные пакета
(packument) скачиваются по адресу <репозиторий>/<имя пакета> и
разбираются как JSON. npm и сторонние библиотеки не используются.

ACCEPT запрашивает сокращённый формат метаданных (только то, что нужно
для установки). NOT_REGISTRY — префиксы спецификаций зависимостей,
которые указывают не на версию из репозитория (git, файлы, ссылки).
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from semver import RangeError, max_satisfying

ACCEPT = "application/vnd.npm.install-v1+json; q=1.0, application/json; q=0.8"
TIMEOUT = 30
HTTP_NOT_FOUND = 404
NOT_REGISTRY = (
    "file:", "link:", "git:", "git+", "github:", "gitlab:", "bitbucket:",
    "http:", "https:", "workspace:", "portal:",
)


class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


def http_get_json(url):
    """Скачивает документ по URL и разбирает его как JSON."""
    headers = {"Accept": ACCEPT, "User-Agent": "dep-visual"}
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            body = response.read()
    except HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            message = f"не найдено в репозитории (404): {url}"
        else:
            message = f"ошибка HTTP {error.code} при запросе {url}"
        raise RepoError(message) from error
    except URLError as error:
        message = f"репозиторий недоступен: {url} ({error.reason})"
        raise RepoError(message) from error
    except OSError as error:
        raise RepoError(f"ошибка сети при запросе {url}: {error}") from error
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepoError(f"ответ {url} — не JSON") from error


def package_url(repository, name):
    """URL метаданных пакета; '/' в имени с областью кодируется как %2f."""
    return repository.rstrip("/") + "/" + quote(name, safe="@")


def split_alias(name, spec):
    """Разворачивает псевдоним 'npm:real-name@range' в (имя, диапазон)."""
    if not spec.startswith("npm:"):
        return name, spec
    target = spec[len("npm:"):]
    at = target.rfind("@")
    if at > 0:
        return target[:at], target[at + 1:]
    return target, "*"


class NpmRegistry:
    """Доступ к npm-репозиторию с кэшем метаданных пакетов."""

    def __init__(self, url, fetch=http_get_json):
        """Репозиторий по URL; fetch можно подменить в тестах."""
        self.url = url
        self.fetch = fetch
        self.cache = {}

    def packument(self, name):
        """Метаданные пакета: все версии и метки dist-tags."""
        if name not in self.cache:
            data = self.fetch(package_url(self.url, name))
            versions = data.get("versions") if isinstance(data, dict) else None
            if not isinstance(versions, dict):
                raise RepoError(
                    f"неверный формат метаданных пакета '{name}'"
                )
            self.cache[name] = data
        return self.cache[name]

    def resolve(self, name, spec):
        """Выбирает точную версию пакета по диапазону, как это делает npm.

        Если метка latest удовлетворяет диапазону, берётся она, иначе —
        наибольшая подходящая версия. Метка (latest, next) тоже допустима.
        """
        data = self.packument(name)
        versions = data["versions"]
        tags = data.get("dist-tags") or {}
        spec = spec.strip() or "*"
        if spec in tags:
            return tags[spec]
        if spec in versions:
            return spec
        latest = tags.get("latest")
        try:
            if latest in versions and max_satisfying([latest], spec):
                return latest
            found = max_satisfying(versions.keys(), spec)
        except RangeError as error:
            message = f"{name}: некорректный диапазон '{spec}': {error}"
            raise RepoError(message) from error
        if found is None:
            raise RepoError(f"{name}: нет версии, подходящей под '{spec}'")
        return found

    def dependencies(self, name, version):
        """Прямые зависимости точной версии: словарь имя -> диапазон."""
        versions = self.packument(name)["versions"]
        if version not in versions:
            raise RepoError(f"у пакета '{name}' нет версии {version}")
        deps = versions[version].get("dependencies") or {}
        if not isinstance(deps, dict):
            raise RepoError(f"{name}@{version}: неверный формат dependencies")
        return dict(deps)

    def direct_dependencies(self, name, version):
        """Версия пакета (latest раскрывается) и его прямые зависимости."""
        exact = self.resolve(name, version)
        return exact, self.dependencies(name, exact)

    def children(self, node):
        """Узлы-зависимости для узла 'имя@версия' и список предупреждений."""
        name, version = split_node(node)
        result = []
        warnings = []
        for dep_name, spec in self.dependencies(name, version).items():
            real_name, real_spec = split_alias(dep_name, str(spec))
            if real_spec.startswith(NOT_REGISTRY) or "/" in real_spec:
                warnings.append(
                    f"{node}: зависимость {dep_name}@{spec} "
                    "не из репозитория, пропущена"
                )
                continue
            try:
                exact = self.resolve(real_name, real_spec)
            except RepoError as error:
                warnings.append(f"{node}: {error}")
                continue
            result.append(f"{real_name}@{exact}")
        return result, warnings


def split_node(node):
    """'@scope/name@1.0.0' -> ('@scope/name', '1.0.0')."""
    at = node.rfind("@")
    return node[:at], node[at + 1:]
