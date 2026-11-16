import contextlib
import io
import unittest

from tests.helpers import data_path
import main


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main.main(list(args))
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    def test_config_error(self):
        code, _, err = run(data_path("configs", "errors", "depth_zero.xml"))
        self.assertEqual(code, 1)
        self.assertIn("Ошибка: <max_depth>", err)

    def test_missing_config(self):
        code, _, err = run("no_such.xml")
        self.assertEqual(code, 1)
        self.assertIn("не найден", err)
