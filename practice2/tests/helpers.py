"""Общие функции для тестов: пути к файлам и фиктивный npm-репозиторий.

FAKE_PACKAGES — метаданные npm: имя -> {"dist-tags", "versions"}.
"""

import os

from npm_registry import RepoError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAKE_PACKAGES = {
    "app": {
        "dist-tags": {"latest": "2.0.0"},
        "versions": {
            "1.0.0": {"dependencies": {"lib-a": "^1.0.0"}},
            "2.0.0": {"dependencies": {"lib-a": "^1.1.0", "lib-b": "~2.0.0"}},
        },
    },
    "lib-a": {
        "dist-tags": {"latest": "1.2.0"},
        "versions": {
            "1.0.0": {},
            "1.1.0": {"dependencies": {"lib-c": "*"}},
            "1.2.0": {"dependencies": {"lib-c": ">=1 <3"}},
            "2.0.0": {},
        },
    },
    "lib-b": {
        "dist-tags": {"latest": "3.0.0"},
        "versions": {
            "2.0.0": {"dependencies": {"lib-c": "1.x"}},
            "2.0.5": {"dependencies": {"lib-c": "1.x", "app": "^2.0.0"}},
            "3.0.0": {},
        },
    },
    "lib-c": {
        "dist-tags": {"latest": "2.1.0"},
        "versions": {"1.0.0": {}, "2.1.0": {}, "3.0.0-beta.1": {}},
    },
}


def fake_fetch(url):
    """Подменяет HTTP-запрос: отдаёт метаданные из FAKE_PACKAGES."""
    name = url.rsplit("/", 1)[1].replace("%2f", "/").replace("%2F", "/")
    if name not in FAKE_PACKAGES:
        raise RepoError(f"не найдено в репозитории (404): {url}")
    return FAKE_PACKAGES[name]


def data_path(*parts):
    """Путь к файлу проекта."""
    return os.path.join(ROOT, *parts)
