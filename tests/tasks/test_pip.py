from unittest.mock import call, patch

import pytest

from dev.tasks.pip import Pip


@patch('dev.tasks.pip.run_command')
def test_up(run_command_mock):
    Pip('requirements/base.txt', extra_args=[])

    run_command_mock.assert_has_calls([
        call('pip --disable-pip-version-check install -r requirements/base.txt'),
    ])


@patch('dev.tasks.pip.run_command')
def test_up_list(run_command_mock):
    Pip(['requirements/base.txt', 'requirements/development.txt'], extra_args=[])

    run_command_mock.assert_has_calls([
        call('pip --disable-pip-version-check install -r requirements/base.txt'),
        call('pip --disable-pip-version-check install -r requirements/development.txt'),
    ])


@patch('dev.tasks.pip.os.path.exists')
@patch('dev.tasks.pip.run_command')
def test_up_default(run_command_mock, path_exists_mock):
    path_exists_mock.return_value = True

    Pip(None, extra_args=[])

    run_command_mock.assert_has_calls([
        call('pip --disable-pip-version-check install -r requirements.txt'),
    ])


@patch('dev.task.error_console.print')
@patch('dev.tasks.pip.run_command')
def test_up_missing_file(run_command_mock, console_print_mock):
    with pytest.raises(SystemExit):
        Pip('missing.txt', extra_args=[])

    run_command_mock.assert_not_called()
    console_print_mock.assert_called_once_with('Failed to run [b]Pip[/] task: missing.txt does not exist', style='red')


@patch('dev.tasks.pip.run_command')
def test_up_with_package(run_command_mock):
    Pip('pytest', extra_args=[])

    run_command_mock.assert_has_calls([
        call('pip --disable-pip-version-check install pytest'),
    ])
