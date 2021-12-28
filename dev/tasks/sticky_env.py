from typing import Any, Optional

from schema import Schema

from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class StickyEnv(Task):
    __schema__ = Schema({str: str})
    __description__ = 'Set env variables in project shell'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return
        ShadowenvHelper.set_environments(args)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return
        ShadowenvHelper.unset_environments()
