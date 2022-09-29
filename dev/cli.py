#!/usr/bin/env python3
"""
Usage:
  dev <command> [-- <extra_args>...]
  dev cd [<repository>]
  dev clone <repository_or_url>
  dev init <shell>
  dev open <target>
  dev update
  dev [-hvct]

Options:
  -h, --help       Show this screen
  -v, --version    Show version
  -c, --commands   List all commands
  -t, --tasks      List all tasks

"""

import os
import sys

from docopt import docopt

from dev.config import config
from dev.console import console, error_console
from dev.exceptions import (CommandNotFoundError, NonZeroReturnCodeError, TaskNotFoundError)
from dev.helpers import load_local_taks, task_to_class
from dev.helpers.parent_shell import ParentShellHelper
from dev.tasks.internal import HelpCommand, HelpTask
from dev.version import __version__

from . import sys_path  # noqa

args = docopt(__doc__ or '')

load_local_taks()


def main(args: dict = args) -> None:
    command = args['<command>']
    extra_args = args['<extra_args>']

    try:
        if args['--version'] is True:
            console.print(f'dev {__version__} - Running in Python {sys.version}')
            sys.exit(0)

        if args['--tasks'] is True:
            HelpTask()
            sys.exit(0)

        if not command or args['--commands'] is True:
            HelpCommand()
            sys.exit(0)

        warn_when_using_bare(command)

        for direction, tasks in config.resolve_tasks(command, extra_args).items():
            for task in tasks:
                task_to_class(task.name)(args=task.args, extra_args=extra_args, direction=direction)
    except CommandNotFoundError:
        HelpCommand(command)
    except TaskNotFoundError as e:
        HelpTask(e.task)
    except NonZeroReturnCodeError as e:
        console.print(
            f'Failed to run [b]{command}[/]:',
            f'Command [b]{e.command}[/] returned with exit code {e.code}',
            style='red',
        )
    finally:
        ParentShellHelper.send_queued_commands()


def warn_when_using_bare(command: str) -> None:
    if command == 'init':
        # We do not need the shell wrapper when initializing the shell environment.
        return

    if os.environ.get('INVOKED_VIA_SHELL') == '1':
        # We are already running in a shell wrapper.
        return

    shell = os.path.basename(os.environ.get('SHELL', 'bash'))

    error_console.print(
        'Warning: You are running [b]dev-bare[/] directly. For all features to work '
        'properly, you need to call [b]dev[/].\n'
        'If [b]dev[/] is not availible in your shell, add following to your shell config:\n\n'
        f'    eval "$({sys.argv[0]} init {shell})"\n',
        style='yellow',
    )


if __name__ == "__main__":
    main()
