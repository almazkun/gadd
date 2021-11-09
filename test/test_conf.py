from argparse import Namespace
from unittest import TestCase

from gadd.conf import Conf

TEST_CONFIG_FILE_NAME = ".test_gadd"
TEST_DEFAULT_SECTION = "TEST_GADD"


class TestConfigs(TestCase):
    def create_test_conf_file(self):
        with open("test.conf", "w") as f:
            f.write(content)

    def test_configs_init(self):
        t_kwargs = dict(
            exclude="test_exclude",
            ignore_decorators="test_ignore_decorators",
            ignore_names="test_ignore_names",
        )
        parse_args = Namespace(**t_kwargs)
        conf = Conf(parse_args=parse_args)

        self.assertIsInstance(conf, Conf)
