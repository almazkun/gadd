from argparse import Namespace
from configparser import ConfigParser

CONFIG_FILE_NAME = ".gadd"
DEFAULT_SECTION = "GADD"


class Conf:
    def __init__(self, parse_args: Namespace, cnf_file: str = CONFIG_FILE_NAME):
        # {'exclude': None, 'ignore_decorators': None, 'ignore_names': None}
        parse_args = vars(parse_args)
        self.cnf_file = cnf_file
        self._exclude = parse_args.get("exclude")
        self._ignore_decorators = parse_args.get("ignore_decorators")
        self._ignore_names = parse_args.get("ignore_names")

    @property
    def read_form_file(self) -> dict:
        if os.path.exists(self.cnf_file):
            return ConfigParser().read(self.cnf_file)[DEFAULT_SECTION]

    @property
    def exclude_paths(self) -> list:
        return self.read_form_file.get("exclude")

    @property
    def ignore_decorators(self):
        return self.read_form_file.get("ignore_decorators")

    @property
    def ignore_names(self):
        return self.read_form_file.get("ignore_names")

    def combiner(one: str, two: str) -> str:
        return f"{one},{two}"
