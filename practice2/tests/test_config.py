import os
import tempfile
import unittest

from tests.helpers import data_path
from config import ConfigError, load_config

TEMPLATE = """<config>
    <package>{package}</package>
    <repository>{repository}</repository>
    <test_mode>{test_mode}</test_mode>
    <version>{version}</version>
    <output_file>{output_file}</output_file>
    <ascii_tree>{ascii_tree}</ascii_tree>
    <max_depth>{max_depth}</max_depth>
</config>"""

GOOD = dict(
    package="express", repository="https://registry.npmjs.org",
    test_mode="false", version="4.18.2", output_file="graph.svg",
    ascii_tree="true", max_depth="3",
)


class ConfigTest(unittest.TestCase):
    def load(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False,
                                         encoding="utf-8") as file:
            file.write(text)
        self.addCleanup(os.remove, file.name)
        return load_config(file.name)

    def load_values(self, **changes):
        return self.load(TEMPLATE.format(**{**GOOD, **changes}))

    def assert_error(self, fragment, **changes):
        with self.assertRaises(ConfigError) as context:
            self.load_values(**changes)
        self.assertIn(fragment, str(context.exception))

    def test_good_config(self):
        config = self.load_values()
        self.assertEqual(config.package, "express")
        self.assertFalse(config.test_mode)
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 3)
        self.assertEqual([key for key, _ in config.items()][0], "package")

    def test_scoped_name_and_latest(self):
        config = self.load_values(package="@types/node", version="latest")
        self.assertEqual(config.package, "@types/node")

    def test_test_mode(self):
        config = self.load_values(
            package="A", repository=data_path("tests", "helpers.py"),
            test_mode="true",
        )
        self.assertTrue(config.test_mode)

    def test_package_errors(self):
        self.assert_error("пустым", package="")
        self.assert_error("недопустимое имя", package="Express")
        self.assert_error("большие", package="a", test_mode="true",
                          repository=data_path("tests", "helpers.py"))

    def test_repository_errors(self):
        self.assert_error("некорректный URL", repository="registry.npmjs.org")
        self.assert_error("файл не найден", repository="nope.txt", package="A",
                          test_mode="true")
        self.assert_error("не файл", repository=data_path("tests"), package="A",
                          test_mode="true")

    def test_value_errors(self):
        self.assert_error("<test_mode>", test_mode="maybe")
        self.assert_error("<version>", version="4.x")
        self.assert_error(".svg", output_file="graph.png")
        self.assert_error("не существует", output_file="no_such_dir/graph.svg")
        self.assert_error("<ascii_tree>", ascii_tree="da")
        self.assert_error("целое число", max_depth="three")
        self.assert_error(">= 1", max_depth="0")

    def test_structure_errors(self):
        with self.assertRaises(ConfigError):
            load_config("no_such_config.xml")
        for text, fragment in [
            ("<config><package>x</config>", "некорректный XML"),
            ("<settings/>", "корневой элемент"),
            ("<config><color/></config>", "неизвестный"),
            ("<config><package>a</package><package>b</package></config>", "повторно"),
            ("<config><package>a</package></config>", "не задан"),
        ]:
            with self.assertRaises(ConfigError) as context:
                self.load(text)
            self.assertIn(fragment, str(context.exception))


if __name__ == "__main__":
    unittest.main()
