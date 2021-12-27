from pathlib import PosixPath
from unittest.mock import call, patch

from dev.tasks.python import Python


@patch('dev.tasks.python.run_command')
@patch('dev.tasks.python.HomebrewHelper.install_formula')
@patch('dev.tasks.python.ShadowenvHelper.configure_provider')
def test_up(configure_provider_mock, install_formula_mock, run_command_mock):
    run_command_mock.return_value = '/dummy'

    Python('3.10.0', extra_args=[])

    install_formula_mock.assert_called_once_with('pyenv')
    run_command_mock.assert_has_calls([
        call('pyenv root', output=True, silent=True),
        call('pyenv install --skip-existing 3.10.0'),
        call('pyenv local 3.10.0'),
        call("pyenv exec python -m venv /dummy/versions/3.10.0/virtualenvs/dev"),
    ])
    configure_provider_mock.assert_called_once_with(
        'python', '3.10.0', PosixPath('/dummy/versions/3.10.0/virtualenvs/dev'), env_name='WORKON_HOME'
    )


@patch('dev.tasks.python.Python.python_already_installed')
@patch('dev.tasks.python.Python.virtualenv_already_created')
@patch('dev.tasks.python.run_command')
@patch('dev.tasks.python.HomebrewHelper.install_formula')
@patch('dev.tasks.python.ShadowenvHelper.configure_provider')
def test_up_already_installed(
    configure_provider_mock, install_formula_mock, run_command_mock, virtualenv_already_created_mock,
    python_already_installed_mock
):
    run_command_mock.return_value = '/dummy'
    python_already_installed_mock.return_value = True
    virtualenv_already_created_mock.return_value = True

    Python('3.10.0', extra_args=[])

    install_formula_mock.assert_called_once_with('pyenv')
    run_command_mock.assert_called_once_with('pyenv root', output=True, silent=True)
    configure_provider_mock.assert_called_once_with(
        'python', '3.10.0', PosixPath('/dummy/versions/3.10.0/virtualenvs/dev'), env_name='WORKON_HOME'
    )


@patch('dev.tasks.python.Python.virtualenv_already_created')
@patch('dev.tasks.python.run_command')
def test_down(run_command_mock, virtualenv_already_created_mock):
    run_command_mock.return_value = '/dummy'
    virtualenv_already_created_mock.return_value = True

    Python('3.10.0', extra_args=[], direction='down')

    run_command_mock.assert_has_calls([
        call('pyenv root', output=True, silent=True),
        call('rm -rf /dummy/versions/3.10.0/virtualenvs/dev'),
    ])
