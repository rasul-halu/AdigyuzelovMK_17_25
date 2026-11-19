"""Тесты сравнения версий и диапазонов SemVer."""

import unittest

from semver import Range, RangeError, Version, max_satisfying

VERSIONS = ["0.0.1", "0.0.2", "0.1.0", "0.1.5", "0.2.0", "1.0.0", "1.2.3",
            "1.2.9", "1.3.0", "1.9.9", "2.0.0-beta.1", "2.0.0", "2.4.1",
            "3.0.0"]


class SemverTest(unittest.TestCase):
    """Сравнение версий и выбор версии по диапазону."""

    def best(self, text):
        """Наибольшая версия из VERSIONS для диапазона."""
        return max_satisfying(VERSIONS, text)

    def test_compare(self):
        """Порядок версий, включая prerelease."""
        parse = Version.parse
        self.assertLess(parse("1.0.0-alpha"), parse("1.0.0"))
        self.assertLess(parse("1.0.0-alpha"), parse("1.0.0-alpha.1"))
        self.assertLess(parse("1.0.0-2"), parse("1.0.0-10"))
        self.assertLess(parse("1.0.0-9"), parse("1.0.0-alpha"))
        self.assertIsNone(parse("1.0"))

    def test_ranges(self):
        """Операторы ^, ~, x, сравнения, дефис и ||."""
        cases = {
            "^1.2.3": "1.9.9", "^0.1.0": "0.1.5", "^0.0.1": "0.0.1",
            "~1.2.3": "1.2.9", "~1": "1.9.9", "1.x": "1.9.9", "1.2": "1.2.9",
            "*": "3.0.0", "": "3.0.0", ">=1.0.0 <2.0.0": "1.9.9",
            ">= 1 < 2": "1.9.9", "<=1.2": "1.2.9", ">1.2": "3.0.0",
            "<2": "1.9.9", "1.0.0 - 1.3": "1.3.0", "1.0.0 - 1.2.3": "1.2.3",
            "^0.1 || ^2.0.0": "2.4.1", "=1.2.3": "1.2.3", "v1.0.0": "1.0.0",
            "^2.0.0-beta.0": "2.4.1", "~2.0.0-beta.0": "2.0.0",
            "^5.0.0": None, "<0.0.1": None,
        }
        for text, expected in cases.items():
            with self.subTest(range=text):
                self.assertEqual(self.best(text), expected)

    def test_prerelease_only_when_asked(self):
        """Prerelease подходит только явно."""
        beta = Version.parse("2.0.0-beta.1")
        self.assertTrue(Range(">=2.0.0-beta.0 <2.0.0").test(beta))
        self.assertFalse(Range(">=1.0.0").test(beta))

    def test_bad_range(self):
        """Некорректный диапазон вызывает ошибку."""
        with self.assertRaises(RangeError):
            Range("abc")
        with self.assertRaises(RangeError):
            Range(">=")


if __name__ == "__main__":
    unittest.main()
