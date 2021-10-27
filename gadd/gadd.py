import sys

import autoflake
import black
import isort
from flake8.api import legacy as flake8
from git import Repo


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
    print("Applying Black")
    try:
        black.main([filename])
    except SystemExit:
        pass


def _format(filename):
    """
    flake8 --config=.flake8 $@

    pylint --rcfile=.pylintrc -f parseable -r n $@

    Args:
        file ([type]): [description]
    """
    style_guide = flake8.get_style_guide(ignore=["E24", "W503"])
    report = style_guide.check_files([filename])
    print("flake8 errors: ", report.get_statistics("E"))


def deadcode(file):
    print(file)


def staged_files():
    """List of the staged files in this folder/reposetory

    Returns:
        list: list of staged files
    """
    return Repo().git.diff("--name-only", "--cached").split("\n")


def python_staged_files():
    return [file for file in staged_files() if file.endswith(".py")]


def gadd(files):
    print("#######################")
    print("# Make it good again! #")
    print("#######################\n")
    if files:
        print(f"Found {len(files)} python files:\n")
        for file in files:
            print(f"\033[1m{file}\033[0m")
            remove_unused_imports(file)
            sort_imports(file)
            _format(file)
            deadcode(file)
            print()
    else:
        print("No python files found!\n")
    print("########")
    print("# Exit #")
    print("########")


if __name__ == "__main__":
    gadd(python_staged_files())
