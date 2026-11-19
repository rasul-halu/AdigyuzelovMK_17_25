"""Тесты загрузки данных из npm-репозитория."""

import functools
import json
import os
import shutil
import tempfile
import threading
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler

from tests.helpers import FAKE_PACKAGES, fake_fetch
from npm_registry import (
    NpmRegistry, RepoError, http_get_json, package_url, split_alias,
    split_node,
)


class QuietHandler(SimpleHTTPRequestHandler):
    """Раздаёт файлы каталога без вывода журнала запросов."""

    def log_message(self, *args):
        """Не печатает журнал запросов."""


def fake_registry():
    """Репозиторий с подменённой загрузкой данных."""
    return NpmRegistry("https://registry.example", fetch=fake_fetch)


def start_server(folder):
    """Запускает HTTP-сервер, раздающий файлы folder, и возвращает его."""
    handler = functools.partial(QuietHandler, directory=folder)
    server = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class RegistryTest(unittest.TestCase):
    """Разбор метаданных и выбор версий."""

    def test_direct_dependencies(self):
        """Прямые зависимости точной версии и метки latest."""
        registry = fake_registry()
        version, deps = registry.direct_dependencies("app", "1.0.0")
        self.assertEqual((version, deps), ("1.0.0", {"lib-a": "^1.0.0"}))
        version, deps = registry.direct_dependencies("app", "latest")
        self.assertEqual(version, "2.0.0")
        self.assertEqual(list(deps), ["lib-a", "lib-b"])

    def test_resolve_prefers_latest_tag(self):
        """Метка latest берётся, если входит в диапазон."""
        registry = fake_registry()
        self.assertEqual(registry.resolve("lib-c", "*"), "2.1.0")
        self.assertEqual(registry.resolve("lib-c", "^1.0.0"), "1.0.0")
        self.assertEqual(registry.resolve("lib-b", "~2.0.0"), "2.0.5")

    def test_errors(self):
        """Нет пакета, нет версии, нет подходящей версии."""
        registry = fake_registry()
        with self.assertRaises(RepoError):
            registry.direct_dependencies("no-such", "1.0.0")
        with self.assertRaises(RepoError):
            registry.direct_dependencies("app", "9.9.9")
        with self.assertRaises(RepoError):
            registry.resolve("lib-c", "^9")

    def test_children(self):
        """Зависимости узла как узлы имя@версия."""
        children, warnings = fake_registry().children("app@2.0.0")
        self.assertEqual(children, ["lib-a@1.2.0", "lib-b@2.0.5"])
        self.assertEqual(warnings, [])

    def test_helpers(self):
        """URL пакета с областью, псевдонимы и разбор узла."""
        self.assertEqual(package_url("https://r.org/", "@types/node"),
                         "https://r.org/@types%2Fnode")
        self.assertEqual(split_alias("x", "npm:lib-a@^1"), ("lib-a", "^1"))
        self.assertEqual(split_node("@s/p@1.0.0"), ("@s/p", "1.0.0"))


class HttpTest(unittest.TestCase):
    """Загрузка по HTTP с локального сервера."""

    def test_http(self):
        """Успешный ответ, 404, не-JSON и недоступный адрес."""
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        for name, data in FAKE_PACKAGES.items():
            with open(os.path.join(folder, name), "w",
                      encoding="utf-8") as file:
                json.dump(data, file)
        with open(os.path.join(folder, "broken"), "w",
                  encoding="utf-8") as file:
            file.write("not json")
        server = start_server(folder)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = f"http://127.0.0.1:{server.server_port}"
        deps = NpmRegistry(url).direct_dependencies("app", "1.0.0")[1]
        self.assertEqual(deps, {"lib-a": "^1.0.0"})
        with self.assertRaises(RepoError) as context:
            http_get_json(url + "/missing")
        self.assertIn("404", str(context.exception))
        with self.assertRaises(RepoError):
            http_get_json(url + "/broken")
        with self.assertRaises(RepoError):
            http_get_json("http://127.0.0.1:1/x")


if __name__ == "__main__":
    unittest.main()
