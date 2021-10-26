# gadd
Very opinionated formatting python files after git add

# Intent
I needed a small tool to reformat and lint all the staged `.py` files according to the specific rules. I wanted it to be able to `pip` install it. it is called `gadd` because you run it after `git add` commend.
It will do:
* remove unused imports
* sort imports
* `lint`
* `format`
* `deadcode`


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