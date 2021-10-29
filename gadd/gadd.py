import sys

import autoflake
import black
import isort
from flake8.api import legacy as flake8
from git import Repo
from pylint.lint import Run
from vulture import Vulture


def remove_unused_imports(filename):
    """
    isort --recursive --force-single-line-imports --line-width 999 $LOC
    autoflake --recursive --ignore-init-module-imports --in-place --remove-all-unused-imports $LOC

    Args:
        filename ([type]): [description]
    """
    print("Removing and sorting imports.")
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
    print("Applying Black.")
    try:
        black.main([filename])  # pylint: disable=no-value-for-parameter
    except SystemExit as e:
        print(filename, e)


def format_(filename):
    def _check_flake8(filename):
        """Same as: `flake8 --config=.flake8 $@`"""
        print("Cheking with flake8.")
        style_guide = flake8.get_style_guide(config=".flake8")
        report = style_guide.check_files([filename])
        e = report.get_statistics("E")
        if e:
            print("flake8 errors: ", report.get_statistics("E"))
        else:
            print("flake8 OK!")

    def _check_pylint(filename):
        """Same as: `pylint --rcfile=.pylintrc -f parseable -r n $@`"""
        print("Cheking with pylint.")
        Run(f"--rcfile=.pylintrc -f parseable -r n {filename}".split(" "), exit=False)

    _check_flake8(filename)
    _check_pylint(filename)


def deadcode(file):
    """Same as: 
        ```
        vulture file whitelist.py \
            --exclude directory \
            --ignore-decorators "@decoratore.some",
        ```

    Args:
        file (str): file name
    """
    print("Cheking with Vulture.")
    vulture = Vulture(ignore_decorators=["@decoratore.some"])
    vulture.scavenge(
        [file, "whitelist.py"],
        exclude=["directory"],
    )
    vulture.report()


def staged_files():
    """List of the staged files in this folder/reposetory

    Returns:
        list: list of staged files
    """
    return Repo().git.diff("--name-only", "--cached").split("\n")


def python_staged_files():
    return [file for file in staged_files() if file.endswith(".py")]


def gadd(file_list):
    print("#######################")
    print("# Make it PEP8 again! #")
    print("#######################\n")
    if file_list:
        print(f"Found {len(file_list)} python file(s):\n")
        for file in file_list:
            print(f"\033[1m{file}\033[0m")
            remove_unused_imports(file)
            sort_imports(file)
            format_(file)
            deadcode(file)
            print()
    else:
        print("No python files found!\n")
    print("########")
    print("# Exit #")
    print("########")


if __name__ == "__main__":
    gadd(python_staged_files())
