from typing import Any, Optional

from schema import Schema

from dev.helpers import run_command
from dev.task import InternalTask


class Update(InternalTask):
    __schema__ = Schema([])
    __description__ = 'Update dev to latest version'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        run_command('git -C /opt/dev fetch --quiet --depth=1 origin main')
        run_command('git -C /opt/dev reset --quiet origin/main --hard')
        run_command('/opt/dev/venv/bin/pip install --disable-pip-version-check -e /opt/dev')
