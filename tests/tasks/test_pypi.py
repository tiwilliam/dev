import os
from unittest.mock import call, patch

import pytest

from dev.tasks.pypi import Pypi


@patch('dev.tasks.pypi.os.environ')
@patch('dev.tasks.pypi.run_command')
def test_up(run_command_mock, environ_mock):
    environ_mock.get.return_value = 'abc'

    Pypi('upload', extra_args=[])

    run_command_mock.assert_has_calls(
        [
            call('rm -rf dist'),
            call('pip install --upgrade twine build'),
            call('python -m build'),
            call('python -m twine check dist/*'),
            call('python -m twine upload dist/*'),
        ]
    )


@patch('dev.task.error_console.print')
@patch('dev.tasks.pypi.os.environ')
@patch('dev.tasks.pypi.run_command')
def test_up_missing_command(run_command_mock, environ_mock, console_print_mock):
    environ_mock.get.return_value = 'abc'

    with pytest.raises(SystemExit):
        Pypi('abc', extra_args=[])

    run_command_mock.assert_not_called()
    console_print_mock.assert_called_once_with(
        'Failed to run [b]Pypi[/] task: Unknown argument [b]abc[/]', style='red'
    )


@patch.dict(os.environ, {'TWINE_USERNAME': 'abc'})
@patch('dev.task.error_console.print')
@patch('dev.tasks.pypi.run_command')
def test_up_missing_password(run_command_mock, console_print_mock):
    with pytest.raises(SystemExit):
        Pypi('upload', extra_args=[])

    run_command_mock.assert_not_called()
    console_print_mock.assert_called_once_with(
        'Failed to run [b]Pypi[/] task: You need to set TWINE_PASSWORD', style='red'
    )


@patch.dict(os.environ, {'TWINE_PASSWORD': 'abc'})
@patch('dev.task.error_console.print')
@patch('dev.tasks.pypi.run_command')
def test_up_missing_username(run_command_mock, console_print_mock):
    with pytest.raises(SystemExit):
        Pypi('upload', extra_args=[])

    run_command_mock.assert_not_called()
    console_print_mock.assert_called_once_with(
        'Failed to run [b]Pypi[/] task: You need to set TWINE_USERNAME', style='red'
    )
