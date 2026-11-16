"""Получение данных о пакетах из npm-репозитория по HTTP.

Используется только стандартная библиотека: метаданные пакета
(packument) скачиваются по адресу <репозиторий>/<имя пакета> и
разбираются как JSON. npm и сторонние библиотеки не используются.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

# Сокращённый формат метаданных: только то, что нужно для установки.
ACCEPT = "application/vnd.npm.install-v1+json; q=1.0, application/json; q=0.8"
TIMEOUT = 30



class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


def http_get_json(url):
    """Скачивает документ по URL и разбирает его как JSON."""
    request = Request(url, headers={"Accept": ACCEPT, "User-Agent": "dep-visual"})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            body = response.read()
    except HTTPError as error:
        if error.code == 404:
            raise RepoError(f"не найдено в репозитории (404): {url}") from error
        raise RepoError(f"ошибка HTTP {error.code} при запросе {url}") from error
    except URLError as error:
        raise RepoError(f"репозиторий недоступен: {url} ({error.reason})") from error
    except OSError as error:
        raise RepoError(f"ошибка сети при запросе {url}: {error}") from error
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepoError(f"ответ {url} — не JSON") from error


def package_url(repository, name):
    """URL метаданных пакета; '/' в имени с областью кодируется как %2f."""
    return repository.rstrip("/") + "/" + quote(name, safe="@")


class NpmRegistry:
    """Доступ к npm-репозиторию с кэшем метаданных пакетов."""

    def __init__(self, url, fetch=http_get_json):
        self.url = url
        self.fetch = fetch
        self.cache = {}

    def packument(self, name):
        """Метаданные пакета: все версии и метки dist-tags."""
        if name not in self.cache:
            data = self.fetch(package_url(self.url, name))
            if not isinstance(data, dict) or not isinstance(data.get("versions"), dict):
                raise RepoError(f"неверный формат метаданных пакета '{name}'")
            self.cache[name] = data
        return self.cache[name]

    def resolve(self, name, version):
        """Точная версия пакета: метка (latest) раскрывается по dist-tags."""
        data = self.packument(name)
        tags = data.get("dist-tags") or {}
        if version in tags:
            return tags[version]
        if version not in data["versions"]:
            raise RepoError(f"у пакета '{name}' нет версии {version}")
        return version

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
