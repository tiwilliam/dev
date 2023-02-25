import sys
from unittest.mock import call, patch

import pytest

sys.argv = ['dev', 'blah']

from dev.cli import main  # noqa
from dev.version import __version__  # noqa


@patch('dev.console.console.print')
def test_version(console_print_mock):
    with pytest.raises(SystemExit):
        main(args=docopt_args({'--version': True}))

    console_print_mock.assert_called_once()
    assert f'dev {__version__} - Running in Python' in console_print_mock.call_args[0][0]


@patch('dev.console.console.print')
@patch('dev.tasks.internal.help_task.Table')
def test_list_tasks(task_table_mock, console_print_mock):
    with pytest.raises(SystemExit):
        main(args=docopt_args({'--tasks': True}))

    console_print_mock.assert_called_once_with(task_table_mock())


@patch('dev.console.console.print')
@patch('dev.tasks.internal.help_command.Table')
def test_list_commands(command_table_mock, console_print_mock):
    with pytest.raises(SystemExit):
        main(args=docopt_args({'--commands': True}))

    console_print_mock.assert_has_calls(
        [
            call(command_table_mock()),
            call(command_table_mock()),
        ]
    )


@patch('dev.console.console.print')
@patch('dev.tasks.internal.help_command.Table')
def test_missing_command(command_table_mock, console_print_mock):
    main(args=docopt_args({'<command>': 'blah'}))

    console_print_mock.assert_has_calls(
        [
            call('Could not find command [b]blah', style='red'),
            call(command_table_mock()),
        ]
    )


@patch('dev.cli.config.resolve_tasks')
def test_up_command(resolve_mock):
    main(args=docopt_args({'<command>': 'up'}))

    resolve_mock.assert_called_once()
    resolve_mock.assert_called_once_with('up', None)


@patch('dev.cli.config.resolve_tasks')
def test_down_command(resolve_mock):
    main(args=docopt_args({'<command>': 'down'}))

    resolve_mock.assert_called_once()
    resolve_mock.assert_called_once_with('down', None)


def docopt_args(patch):
    args = {
        '--commands': False,
        '--help': False,
        '--tasks': False,
        '--version': False,
        '<command>': None,
        '<extra_args>': None,
    }
    args.update(patch)
    return args
