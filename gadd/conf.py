from argparse import Namespace
from configparser import ConfigParser
from os import path

CONFIG_FILE_NAME = ".gadd"
DEFAULT_SECTION = "GADD"


class Conf:
    def __init__(
        self,
        parse_args: Namespace,
        conf_file: str = CONFIG_FILE_NAME,
        default_section: str = DEFAULT_SECTION,
    ):
        parse_args = vars(parse_args)
        self.conf_file = conf_file
        self.default_section = default_section
        self._exclude = parse_args.get("exclude")
        self._ignore_decorators = parse_args.get("ignore_decorators")
        self._ignore_names = parse_args.get("ignore_names")

    @property
    def read_form_file(self) -> dict:
        if path.exists(self.conf_file):
            return ConfigParser().read(self.conf_file)[self.default_section]

    @property
    def exclude_paths(self) -> list:
        return self.read_form_file.get("exclude")

    @property
    def ignore_decorators(self):
        return self.read_form_file.get("ignore_decorators")

    @property
    def ignore_names(self):
        return self.read_form_file.get("ignore_names")

    @staticmethod
    def combiner(one: str, two: str) -> str:
        return f"{one},\n{two}"


def _parse_args():
    def csv(exclude):
        return exclude.split(",")

    usage = "%(prog)s command [options] PATH [PATH ...]"
    version = f"gadd {__version__}"
    glob_help = (
        "Patterns for `vulture` may contain glob wildcards (*, ?, [abc], [!abc])."
    )
    parser = ArgumentParser(prog="gadd", usage=usage)

    parser.add_argument(
        "--exclude",
        metavar="PATTERNS",
        type=csv,
        default=list(),
        help="Comma-separated list of paths to ignore (e.g.,"
        ' "*settings.py,docs/*.py"). {glob_help} A PATTERN without glob'
        " wildcards is treated as *PATTERN*.".format(**locals()),
    )
    parser.add_argument(
        "--ignore-decorators",
        metavar="PATTERNS",
        type=csv,
        default=list(),
        help="Comma-separated list of decorators. Functions and classes using"
        ' these decorators are ignored (e.g., "@app.route,@require_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--ignore-names",
        metavar="PATTERNS",
        type=csv,
        default=list(),
        help='Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument("--version", action="version", version=version)
    return parser.parse_args()
