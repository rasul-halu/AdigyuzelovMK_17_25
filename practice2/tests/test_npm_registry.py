import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from tests.helpers import FAKE_PACKAGES, fake_fetch
from npm_registry import NpmRegistry, RepoError, http_get_json, package_url


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        name = self.path.lstrip("/")
        if name == "broken":
            body, code = b"not json", 200
        elif name in FAKE_PACKAGES:
            body, code = json.dumps(FAKE_PACKAGES[name]).encode(), 200
        else:
            body, code = b"{}", 404
        self.send_response(code)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = NpmRegistry("https://registry.example", fetch=fake_fetch)

    def test_direct_dependencies(self):
        version, deps = self.registry.direct_dependencies("app", "1.0.0")
        self.assertEqual((version, deps), ("1.0.0", {"lib-a": "^1.0.0"}))
        version, deps = self.registry.direct_dependencies("app", "latest")
        self.assertEqual(version, "2.0.0")
        self.assertEqual(list(deps), ["lib-a", "lib-b"])

    def test_errors(self):
        with self.assertRaises(RepoError):
            self.registry.direct_dependencies("no-such", "1.0.0")
        with self.assertRaises(RepoError):
            self.registry.direct_dependencies("app", "9.9.9")

    def test_helpers(self):
        self.assertEqual(package_url("https://r.org/", "@types/node"),
                         "https://r.org/@types%2Fnode")

    def test_http(self):
        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = f"http://127.0.0.1:{server.server_port}"
        registry = NpmRegistry(url)
        self.assertEqual(registry.direct_dependencies("app", "1.0.0")[1],
                         {"lib-a": "^1.0.0"})
        with self.assertRaises(RepoError) as context:
            http_get_json(url + "/missing")
        self.assertIn("404", str(context.exception))
        with self.assertRaises(RepoError):
            http_get_json(url + "/broken")
        with self.assertRaises(RepoError):
            http_get_json("http://127.0.0.1:1/x")


if __name__ == "__main__":
    unittest.main()
