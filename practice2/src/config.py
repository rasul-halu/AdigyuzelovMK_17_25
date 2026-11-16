"""Конфигурация приложения: чтение XML-файла и проверка параметров."""

import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urlparse

# Имя npm-пакета: строчные буквы, цифры, - . _ ~, возможно с областью @scope/.
NPM_NAME = re.compile(r"^(@[a-z0-9][a-z0-9._~-]*/)?[a-z0-9][a-z0-9._~-]*$")
# Имя пакета в тестовом репозитории: большие латинские буквы.
TEST_NAME = re.compile(r"^[A-Z]+$")
# Точная версия по SemVer: 1.2.3, 1.2.3-beta.1, 1.2.3+build.
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$"
)
NPM_NAME_MAX = 214
TRUE_VALUES = ("true", "1", "yes")
FALSE_VALUES = ("false", "0", "no")

# Порядок параметров в файле и при выводе.
FIELDS = (
    "package",
    "repository",
    "test_mode",
    "version",
    "output_file",
    "ascii_tree",
    "max_depth",
)


class ConfigError(Exception):
    """Ошибка в конфигурационном файле."""


@dataclass
class Config:
    """Параметры, которые настраивает пользователь."""

    package: str
    repository: str
    test_mode: bool
    version: str
    output_file: str
    ascii_tree: bool
    max_depth: int

    def items(self):
        """Пары (ключ, значение) в порядке описания параметров."""
        return [(name, getattr(self, name)) for name in FIELDS]


def read_xml(path):
    """Читает XML-файл и возвращает словарь тег -> текст."""
    if not os.path.isfile(path):
        raise ConfigError(f"конфигурационный файл не найден: '{path}'")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ConfigError(f"некорректный XML в '{path}': {error}") from error
    if root.tag != "config":
        raise ConfigError(f"корневой элемент должен быть <config>, а не <{root.tag}>")
    values = {}
    for child in root:
        if child.tag not in FIELDS:
            raise ConfigError(f"неизвестный параметр <{child.tag}>")
        if child.tag in values:
            raise ConfigError(f"параметр <{child.tag}> задан повторно")
        values[child.tag] = (child.text or "").strip()
    for name in FIELDS:
        if name not in values:
            raise ConfigError(f"не задан параметр <{name}>")
    return values


def parse_bool(name, text):
    """Переводит текст в bool или сообщает об ошибке."""
    lowered = text.lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    raise ConfigError(f"<{name}>: ожидается true или false, получено '{text}'")


def check_package(name, test_mode):
    """Проверяет имя пакета."""
    if not name:
        raise ConfigError("<package>: имя пакета не может быть пустым")
    if test_mode:
        if not TEST_NAME.match(name):
            raise ConfigError(
                f"<package>: в тестовом режиме имя пакета — большие "
                f"латинские буквы, получено '{name}'"
            )
        return
    if len(name) > NPM_NAME_MAX:
        raise ConfigError(f"<package>: имя длиннее {NPM_NAME_MAX} символов")
    if not NPM_NAME.match(name):
        raise ConfigError(
            f"<package>: недопустимое имя npm-пакета '{name}' (строчные "
            "латинские буквы, цифры, символы - . _ ~, область @scope/)"
        )


def check_repository(repository, test_mode):
    """Проверяет URL репозитория или путь к файлу тестового репозитория."""
    if not repository:
        raise ConfigError("<repository>: не задан URL или путь к файлу")
    if test_mode:
        if not os.path.exists(repository):
            raise ConfigError(f"<repository>: файл не найден: '{repository}'")
        if not os.path.isfile(repository):
            raise ConfigError(f"<repository>: '{repository}' — не файл")
        return
    parsed = urlparse(repository)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigError(
            f"<repository>: некорректный URL '{repository}' "
            "(нужен http:// или https://)"
        )


def check_version(version):
    """Проверяет версию: точная версия SemVer или метка latest."""
    if not version:
        raise ConfigError("<version>: версия не может быть пустой")
    if version != "latest" and not SEMVER.match(version):
        raise ConfigError(
            f"<version>: '{version}' — не версия SemVer (пример: 4.18.2) "
            "и не latest"
        )


def check_output_file(path):
    """Проверяет имя файла с изображением графа."""
    if not path:
        raise ConfigError("<output_file>: имя файла не может быть пустым")
    if not path.lower().endswith(".svg"):
        raise ConfigError(f"<output_file>: нужен файл .svg, получено '{path}'")
    if os.path.isdir(path):
        raise ConfigError(f"<output_file>: '{path}' — это каталог")
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        raise ConfigError(f"<output_file>: каталог '{folder}' не существует")


def parse_depth(text):
    """Переводит максимальную глубину в целое число >= 1."""
    try:
        depth = int(text)
    except ValueError:
        raise ConfigError(
            f"<max_depth>: ожидается целое число, получено '{text}'"
        ) from None
    if depth < 1:
        raise ConfigError(f"<max_depth>: глубина должна быть >= 1, получено {depth}")
    return depth


def load_config(path):
    """Читает и проверяет конфигурацию, возвращает Config."""
    values = read_xml(path)
    test_mode = parse_bool("test_mode", values["test_mode"])
    check_package(values["package"], test_mode)
    check_repository(values["repository"], test_mode)
    check_version(values["version"])
    check_output_file(values["output_file"])
    ascii_tree = parse_bool("ascii_tree", values["ascii_tree"])
    max_depth = parse_depth(values["max_depth"])
    return Config(
        package=values["package"],
        repository=values["repository"],
        test_mode=test_mode,
        version=values["version"],
        output_file=values["output_file"],
        ascii_tree=ascii_tree,
        max_depth=max_depth,
    )
