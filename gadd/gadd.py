import os
import sys
from argparse import ArgumentParser
from argparse import Namespace
from configparser import ConfigParser
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO

import autoflake
import black
import isort
from flake8.api import legacy as flake8
from git import Repo
from pylint.lint import Run
from vulture import Vulture

__version__ = "0.1.0"

CONFIG_FILE_NAME = ".gadd"
DEFAULT_SECTION = "GADD"


class Configs:
    def __init__(self, parse_args: Namespace):
        # {'exclude': None, 'ignore_decorators': None, 'ignore_names': None}
        parse_args = vars(parse_args)
        self.cnf_file = CONFIG_FILE_NAME
        self._exclude = parse_args.get("exclude")
        self._ignore_decorators = parse_args.get("ignore_decorators")
        self._ignore_names = parse_args.get("ignore_names")

        self.save_to_file()

    @property
    def read_form_file(self) -> dict:
        if os.path.exists(self.cnf_file):
            return ConfigParser().read(self.cnf_file)[DEFAULT_SECTION]

    def save_to_file(self):

        if os.path.exists(self.cnf_file):
            configs = self.read_form_file
            if configs:
                kv = {
                    "exclude": set(self._exclude + configs.get("exclude", [])),
                    "ignore_decorators": set(
                        self._ignore_decorators + configs.get("ignore_decorators", [])
                    ),
                    "ignore_names": set(
                        self._ignore_names + configs.get("ignore_names", [])
                    ),
                }
                with open(self.cnf_file, "w") as f:
                    f.write(DEFAULT_SECTION)
                    for k, v in kv.items():
                        f.write(f"{k} = {', '.join(v)}\n")
        else:
            cnf = ConfigParser()
            cnf[DEFAULT_SECTION] = {
                "exclude": self._exclude,
                "ignore_decorators": self._ignore_decorators,
                "ignore_names": self._ignore_names,
            }
            with open(self.cnf_file, "w") as f:
                cnf.write(f)

    def remove_from_file(self):
        pass

    @property
    def exclude_paths(self) -> list:
        return self.read_form_file.get("exclude", [])

    @property
    def ignore_decorators(self):
        return self.read_form_file.get("ignore_decorators", [])

    @property
    def ignore_names(self):
        return self.read_form_file.get("ignore_names", [])


def remove_unused_imports(filename):
    """
    isort --recursive --force-single-line-imports --line-width 999 $LOC
    autoflake --recursive --ignore-init-module-imports --in-place --remove-all-unused-imports $LOC

    Args:
        filename ([type]): [description]
    """
    print("\tRemoving and sorting imports.")
    isort.file(
        filename,
        **{
            "force_single_line": True,
            "line_length": 999,
        },
    )
    autoflake._main(
        argv=[
            "my_fake_program",
            "--recursive",
            "--ignore-init-module-imports",
            "--in-place",
            "--remove-all-unused-imports",
            filename,
        ],
        standard_out=sys.stdout,
        standard_error=sys.stderr,
    )


def sort_imports(filename):
    """black filename

    Args:
        filename ([type]): [description]
    """
    print("\tApplying Black.")
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            black.main([filename])  # pylint: disable=no-value-for-parameter
        except SystemExit as e:
            print(filename, e)

    out, err = out.getvalue(), err.getvalue()
    print("\t\tReformated:", end=" ")
    print(out.split(" ")[0])


def format_(filename):
    def _check_flake8(filename):
        """Same as: `flake8 --config=.flake8 $@`"""
        print("\tCheking with flake8.")
        style_guide = flake8.get_style_guide(config=".flake8")
        report = style_guide.check_files([filename])
        e = report.get_statistics("E")
        if e:
            print("\t\tflake8 errors: ", report.get_statistics("E"))
        else:
            print("\t\tflake8 OK!")

    def _check_pylint(filename):
        """Same as: `pylint --rcfile=.pylintrc -f parseable -r n $@`"""
        print("\tCheking with pylint.")
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            Run(
                f"--rcfile=.pylintrc -f parseable -r n {filename}".split(" "),
                exit=False,
            )
        out, err = out.getvalue(), err.getvalue()

        for l in out.split("\n"):
            if (
                l
                and not l.startswith("*")
                and not l.startswith("-")
                and not l.startswith("Your code has been rated")
            ):
                print(f"\t\t{l}")

    _check_flake8(filename)
    _check_pylint(filename)


def deadcode(file, configs):
    """Same as: 
        ```
        vulture file whitelist.py \
            --exclude directory \
            --ignore-decorators "@decoratore.some",
        ```

    Args:
        file (str): file name
    """
    print("\tCheking with Vulture.")
    vulture = Vulture(
        ignore_names=configs.ignore_names, ignore_decorators=configs.ignore_decorators
    )
    vulture.scavenge(
        [file, "whitelist.py"],
        exclude=configs.exclude_paths,
    )

    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        vulture.report()
    out, err = out.getvalue(), err.getvalue()

    for l in out.split("\n"):
        if l and not l.startswith("Cheking with Vulture."):
            print(f"\t\t{l}")


def staged_files():
    """List of the staged files in this folder/reposetory

    Returns:
        list: list of staged files
    """
    return Repo().git.diff("--name-only", "--cached").split("\n")


def python_staged_files():
    return [file for file in staged_files() if file.endswith(".py")]


def gadd(file_list, configs: Configs = None):
    print("#######################")
    print("# Make it PEP8 again! #")
    print("#######################\n")
    if file_list:
        print(f"Found {len(file_list)} python file(s) staged:\n")
        for file in file_list:
            print(f"\033[1m{file}\033[0m")
            remove_unused_imports(file)
            sort_imports(file)
            format_(file)
            deadcode(file, configs)
            print()
    else:
        print("No staged python files found!\n")
    print("########")
    print("# Exit #")
    print("########")


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


if __name__ == "__main__":
    gadd(file_list=python_staged_files(), configs=Configs(_parse_args()))
