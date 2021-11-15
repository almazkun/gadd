# gadd
Very opinionated formatting python files after git add

# Intent
I needed a small tool to reformat and lint all the staged `.py` files according to the specific rules. I wanted it to be able to `pip` install it and available in the `PATH`. It is called `gadd` because you run it after `git add` command.
It will do:
* Remove unused imports
* Sort imports
* Reformat with [`Black`](https://github.com/psf/black)
* Run [`flake8`](https://github.com/PyCQA/pylint) and [`pylint`](https://github.com/PyCQA/flake8) linters
* Search for deadcode with [`vulture`](https://github.com/jendrikseipp/vulture)

Obeys `.flake8`, `.pylintrc` and `whitelist.py` config files in the current directory.

# Tutorial
This is quick tutorial on hoe to create `pip` installable Python CLI tool.

* create a repository with the following file structure: 
```bash
user@computer gadd % exa -T .
.
├── gadd
│  ├── __init__.py
│  └── gadd.py
├── LICENSE
├── README.md
└── test
   ├── __init__.py
   └── test_gadd.py
```

# Publish to `pip` with [`poetry`](https://python-poetry.org)
Make it pip installable with CLI command.

Make and publish `pip` package with `poetry`:

* Install `poetry`. I would highly recommend to install it with `pipx`

```
cd gadd
pipx install poetry
poetry init
```
* Modify `pyproject.toml` file:
```toml
 [tool.poetry]
name = "gadd"
version = "0.1.0"
description = "Sort imports, remove unused imports, run Black, flake8, pylint, vulture in one go for al staged .py files"
authors = ["Almaz Kunpeissov <hello@akun.dev>"]
keywords = ["Black", "Sort imports", "analysis", "automation", "autopep8", "code", "flake8", "formatter", "gofmt", "lint", "linter", "pyfmt", "pylint", "python", "remove unused imports", "rustfmt", "static", "vulture", "yapf"]
readme = "README.md"
license = "MIT"
homepage = "https://github.com/almazkun/gadd"
repository = "https://github.com/almazkun/gadd"
documentation = "https://github.com/almazkun/gadd"
include = [
    "LICENSE",
]
classifiers = [
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Debuggers",
]

[tool.poetry.dependencies]
python = "^3.6"
autoflake = "^1.4"
black = "^21.10"
flake8 =  "^4.0"
gitpython = "^3.1"
isort =  "^5.10"
pylint = "^2.11"
vulture = "^2.3"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```



# TODO
* [ ] load from `.conf` file
* [ ] publish to pip
* [ ] make it `async`
* [ ] 