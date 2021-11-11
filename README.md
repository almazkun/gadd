# gadd
Very opinionated formatting python files after git add

# Intent
I needed a small tool to reformat and lint all the staged `.py` files according to the specific rules. I wanted it to be able to `pip` install it. it is called `gadd` because you run it after `git add` command.
It will do:
* Remove unused imports
* Sort imports
* Reformat with [`Black`](https://github.com/psf/black)
* Run [`flake8`](https://github.com/PyCQA/pylint) and [`pylint`](https://github.com/PyCQA/flake8) linters
* Search for deadcode with [`vulture`](https://github.com/jendrikseipp/vulture)

Configs for [`vulture`](https://github.com/jendrikseipp/vulture) could be saved.

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


# TODO
* [ ] load from `.conf` file
* [ ] publish to pip
* [ ] make it `async`
* [ ] 