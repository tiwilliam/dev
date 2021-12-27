from unittest.mock import patch, call

from dev.tasks.internal.update import Update


@patch('dev.tasks.internal.update.run_command')
def test_up(run_command_mock):
    Update([], extra_args=[])

    run_command_mock.assert_has_calls([
        call('git -C /opt/dev fetch --quiet --depth=1 origin main'),
        call('git -C /opt/dev reset --quiet origin/main --hard'),
        call('/opt/dev/venv/bin/pip install --disable-pip-version-check -e /opt/dev'),
    ])
