"""Тесты точки входа: коды возврата и сообщения об ошибках."""

import contextlib
import io
import unittest

from tests.helpers import data_path
import main


def run(*args):
    """Запускает main и возвращает (код, текст stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main.main(list(args))
    return code, err.getvalue()


class MainTest(unittest.TestCase):
    """Запуск приложения с ошибочной конфигурацией."""

    def test_config_error(self):
        """Ошибка в параметре — код 1 и сообщение."""
        code, err = run(data_path("configs", "errors", "depth_zero.xml"))
        self.assertEqual(code, 1)
        self.assertIn("Ошибка: <max_depth>", err)

    def test_missing_config(self):
        """Нет файла конфигурации — код 1."""
        code, err = run("no_such.xml")
        self.assertEqual(code, 1)
        self.assertIn("не найден", err)
