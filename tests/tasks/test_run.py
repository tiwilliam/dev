from unittest.mock import call, patch

from dev.tasks.run import Run


@patch('dev.tasks.run.run_command')
def test_up_string(run_command_mock):
    Run('echo "testing"', [])
    run_command_mock.assert_called_once_with('echo "testing"', env=None)


@patch('dev.tasks.run.run_command')
def test_up_list(run_command_mock):
    Run(['echo "testing"', 'echo "testing again"'], [])
    run_command_mock.assert_has_calls(
        [
            call('echo "testing"', env=None),
            call('echo "testing again"', env=None),
        ]
    )


@patch('dev.tasks.run.run_command')
def test_up_dict(run_command_mock):
    Run({'command': 'echo "testing"', 'env': {'SCOPE': 'something'}}, [])
    run_command_mock.assert_called_once_with('echo "testing"', env={'SCOPE': 'something'})


@patch('dev.tasks.run.run_command')
def test_up_dict_with_many_commands(run_command_mock):
    Run({'command': ['echo "testing"', 'echo "testing again"'], 'env': {'SCOPE': 'something'}}, [])
    run_command_mock.assert_has_calls(
        [
            call('echo "testing"', env={'SCOPE': 'something'}),
            call('echo "testing again"', env={'SCOPE': 'something'}),
        ]
    )
