from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class Env(Task):
    __schema__ = Schema({str: str})
    __description__ = 'Set env variables'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return
        environment.set_env(args)
        ShadowenvHelper.set_environments(args)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return
        environment.unset_env(args)
        ShadowenvHelper.unset_environments()
