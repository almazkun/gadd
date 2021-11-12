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
    out, err = StringIO(), StringIO()
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
        standard_out=out,
        standard_error=err,
    )
    out = out.getvalue()
    if out:
        print("\t\t", out)
    else:
        print("\t\tautoflake is OK!")


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

    out = out.getvalue()
    if out:
        print("\t\tReformated!")
    else:
        print("\t\tBlack is OK!")


def check_flake8(filename):
    """Same as: `flake8 --config=.flake8 $@`"""
    print("\tCheking with flake8.")
    style_guide = flake8.get_style_guide(config=".flake8")
    report = style_guide.check_files([filename])
    e = report.get_statistics("E")
    if e:
        print("\t\tflake8 errors: ", report.get_statistics("E"))
    else:
        print("\t\tflake8 is OK!")


def check_pylint(filename):
    """Same as: `pylint --rcfile=.pylintrc -f parseable -r n $@`"""
    print("\tCheking with pylint.")
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        Run(
            f"--rcfile=.pylintrc -f parseable -r n {filename}".split(" "),
            exit=False,
        )
    out, err = out.getvalue(), err.getvalue()

    list_out = [
        l
        for l in out.split("\n")
        if (
            l
            and not l.startswith("*")
            and not l.startswith("-")
            and not l.startswith("Your code has been rated")
        )
    ]
    if list_out:
        for l in list_out:
            print(f"\t\t{l}")
    else:
        print("\t\tpylint is OK!")


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
    out = out.getvalue()

    list_out = [
        l for l in out.split("\n") if (l and not l.startswith("Cheking with Vulture."))
    ]
    if list_out:
        for l in list_out:
            print(f"\t\t{l}")
    else:
        print("\t\tVulture is OK!")


class Gadd:
    def __init__(self):
        pass

    def execute(self) -> None:
        print("# Gadd: Make it PEP8 again! #")
        file_list = self._python_staged_files
        if file_list:
            start = time()
            print(f"Found {len(file_list)} python file(s) staged:")
            for filename in file_list:
                print(self._run_then_all(filename).getvalue())
            print(f"Took: {(time() - start):.2f} seconds!")
        else:
            print("No staged python files found!")
        print("# Exit #")

    def _run_then_all(self, filename: str) -> None:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            print(f"\033[1m{filename}\033[0m")
            remove_unused_imports(filename)
            sort_imports(filename)
            check_flake8(filename)
            check_pylint(filename)
            run_vulture(filename)
        return out

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


if __name__ == "__main__":
    Gadd().execute()
