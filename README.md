# Dev

[![Continous integration](https://github.com/MasonData/dev/actions/workflows/ci.yml/badge.svg)](https://github.com/MasonData/dev/actions/workflows/ci.yml)

Dev is a Makefile replacement for modern development environments. Dev let's you manage cloned repositories, setup or teardown environments, execute commands, open pull requests and more. Dev is currently only supported on macOS with shell support for bash and zsh.

## Installation

Install dev by running the [installer](https://github.com/MasonData/dev/blob/main/install.sh):

```
curl -s https://raw.githubusercontent.com/MasonData/dev/main/install.sh | sh
```

## Getting started

Dev commands are defined in a `Devfile`, it maps a command to pre-defined tasks. Here is an example file:

```yaml
name: dev
version: 1

up:
    - python: 3.10.0
    - pip: requirements/development.txt
commands:
    test: py.test --color=yes
    style:
        - run: yapf -rip dev
        - run: flake8 .
    upload:
        - pypi: upload
```

Running a command:

```
$ dev test
=> Running command: py.test --color=yes
============================= test session starts ==============================
platform darwin -- Python 3.10.0, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /Users/alex/src/github.com/MasonData/dev
collected 5 items

tests/test_cli.py .....                                                  [100%]

============================== 5 passed in 0.27s ===============================
```

## Managing git clones

Clone and navigate repositores with `clone` and `cd` commands. Clone repositores in a unified way and navigate between them using fuzzy search.

```
~/src/github.com/MasonData/dev $ dev clone hookit
Cloning into '/Users/alex/src/github.com/MasonData/hookit'...
remote: Enumerating objects: 153, done.
remote: Total 153 (delta 0), reused 0 (delta 0), pack-reused 153
Receiving objects: 100% (153/153), 23.12 KiB | 3.30 MiB/s, done.
Resolving deltas: 100% (69/69), done.
~/src/github.com/MasonData/hookit $ dev cd dev
~/src/github.com/MasonData/dev $
```

Helpful fuzzy search for faster repository navigation:
```
$ dev cd heroku
Found multiple matches, select which one you meant:
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Index ┃ Repository                ┃ Organization ┃ Host       ┃ Path                                                           ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1   │ heroku-buildpack-yarn     │ MasonData    │ github.com │ /Users/alex/src/github.com/MasonData/heroku-buildpack-yarn     │
│   2   │ heroku-buildpack-swig-lib │ MasonData    │ github.com │ /Users/alex/src/github.com/MasonData/heroku-buildpack-swig-lib │
└───────┴───────────────────────────┴──────────────┴────────────┴────────────────────────────────────────────────────────────────┘
Which one? (1):
```

## Browser links

Dev provide a way to open links related to your project. A new pull request or issue can easily be opened if your project is hosted on Github. Custom links are added to your `Devfile`.

```
open:
    actions: https://github.com/MasonData/dev/actions
```

Open links using the `dev open` command:

```
$ dev open actions
=> Running command: open https://github.com/MasonData/dev/actions

$ dev open pr
=> Running command: open https://github.com/MasonData/dev/pull/open-url

$ dev open issue
=> Running command: open https://github.com/MasonData/dev/issues/new
```

## Bundled tasks

You can list all tasks available to Dev using the `--tasks` flag. This will list all bundled tasks and locally provided custom tasks.

```
$ dev --tasks
                             Tasks
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task                ┃ Description                           ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ docker_compose      │ Manage docker-compose                 │
│ docker_compose_exec │ Run shell commands in docker-compose  │
│ env                 │ Set env variables for current command │
│ homebrew            │ Install formulas on macOS             │
│ homebrew_cask       │ Install cask formulas on macOS        │
│ hosts               │ Configure hosts file                  │
│ mkcert              │ Generate self-signed certificates     │
│ nginx               │ Configure and control nginx           │
│ node                │ Install a specific Node version       │
│ npm                 │ Run npm install -g                    │
│ pip                 │ Run pip install                       │
│ pypi                │ Manage packages on PyPi               │
│ python              │ Install a specific Python version     │
│ run                 │ Run shell args                        │
│ sticky_env          │ Set env variables in project shell    │
└─────────────────────┴───────────────────────────────────────┘
```

## Custom tasks

Dev provides a handful of common and useful tasks by default, but you might want to define your own to simplify your `Devfile`. A new task can easily be defined in your project by placing it in a `devs` module.

1. Create `devs.custom_task` and define a class named `CustomTask` with a `up` and optionally a `down` method:

    ```python
    from dev.task import Task


    class CustomTask(Task):
        __description__ = 'Demo custom task'

        def up(self, args, extra_args):
            print('Hello world!')

        def down(self, args, extra_args):
            print('Bye world!')
    ```

1. Reference your new task in your `Devfile`:

    ```
    name: project
    version: 1

    up:
        - custom_task
    commands:
        hello:
            - custom_task
    ```

1. Try using it:

    ```
    $ dev up
    Hello world!
    
    $ dev down
    Bye world!

    $ dev hello
    Hello world!
    ```

## Uninstall

Simply remove your `/opt/dev` directory and any reference in your shell config. Restart your shell to clear loaded environment functions.

## License

This project is licensed under the terms of the MIT license.

Inspiration for building this tool comes from an internal tool at Shopify. You can read more about it here: https://devproductivity.io/dev-shopifys-all-purpose-development-tool/
