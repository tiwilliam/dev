from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.task import Task


class Env(Task):
    __schema__ = Schema({str: str})
    __description__ = 'Set env variables for current command'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return
        environment.set_env(args)
