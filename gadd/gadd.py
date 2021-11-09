import sys
from argparse import ArgumentParser
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
from time import time

import autoflake
import black
import isort
from flake8.api import legacy as flake8
from git import Repo
from pylint.lint import Run
from vulture import Vulture

__version__ = "0.1.0"


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


def check_flake8(filename):
    """Same as: `flake8 --config=.flake8 $@`"""
    print("\tCheking with flake8.")
    style_guide = flake8.get_style_guide(config=".flake8")
    report = style_guide.check_files([filename])
    e = report.get_statistics("E")
    if e:
        print("\t\tflake8 errors: ", report.get_statistics("E"))
    else:
        print("\t\tflake8 OK!")


def check_pylint(filename):
    """Same as: `pylint --rcfile=.pylintrc -f parseable -r n $@`"""
    print("\tCheking with pylint.")
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        Run(
            f"--rcfile=.pylintrc -f parseable -j 0 -r n {filename}".split(" "),
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


def run_vulture(filename):
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
    vulture = Vulture(ignore_names="", ignore_decorators="")
    vulture.scavenge(
        [filename, "whitelist.py"],
        exclude="",
    )

    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        vulture.report()
    out, err = out.getvalue(), err.getvalue()

    for l in out.split("\n"):
        if l and not l.startswith("Cheking with Vulture."):
            print(f"\t\t{l}")


class Gadd:
    def __init__(self):
        pass

    def execute(self) -> None:
        print("#######################")
        print("# Make it PEP8 again! #")
        print("#######################\n")
        file_list = self._python_staged_files
        if file_list:
            start = time()
            print(f"Found {len(file_list)} python file(s) staged:\n")
            for filename in file_list:
                self._run_then_all(filename)
            end = time()
            print(f"Took: {(end - start):.2f} seconds!")
        else:
            print("No staged python files found!\n")
        print("########")
        print("# Exit #")
        print("########")

    def report(self):
        pass

    def _run_then_all(self, filename: str) -> None:
        print(f"\033[1m{filename}\033[0m")
        remove_unused_imports(filename)
        sort_imports(filename)
        check_flake8(filename)
        check_pylint(filename)
        run_vulture(filename)
        print()

    @property
    def _staged_files(self) -> list:
        """List of the staged files in this folder/reposetory

        Returns:
            list: list of staged files
        """
        return Repo().git.diff("--name-only", "--cached").split("\n")

    @property
    def _python_staged_files(self) -> list:
        """List all the `.py` in staged files

        Returns:
            list: of files ending .py
        """
        return [file for file in self._staged_files if file.endswith(".py")]


def _parse_args():
    usage = "%(prog)s command [options] PATH [PATH ...]"
    version = f"gadd {__version__}"
    glob_help = (
        "Patterns for `vulture` may contain glob wildcards (*, ?, [abc], [!abc])."
    )
    parser = ArgumentParser(prog="gadd", usage=usage)

    parser.add_argument(
        "--exclude",
        metavar="PATTERNS",
        default=list(),
        help="Comma-separated list of paths to ignore (e.g.,"
        ' "*settings.py,docs/*.py"). {glob_help} A PATTERN without glob'
        " wildcards is treated as *PATTERN*.".format(**locals()),
    )
    parser.add_argument(
        "--ignore-decorators",
        metavar="PATTERNS",
        default=list(),
        help="Comma-separated list of decorators. Functions and classes using"
        ' these decorators are ignored (e.g., "@app.route,@require_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--ignore-names",
        metavar="PATTERNS",
        default=list(),
        help='Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        " {glob_help}".format(**locals()),
    )
    # parser.add_argument("--version", action="version", version=version)
    return parser.parse_args()


if __name__ == "__main__":
    Gadd().execute()
