import os
from typing import Any, Dict

name: str
env: Dict[Any, Any] = dict(os.environ)


def set_name(new_name: str) -> None:
    global name
    name = new_name


def set_env(env_to_set: dict) -> None:
    global env
    env.update(env_to_set)


def unset_env(env_to_unset: dict) -> None:
    for k in env_to_unset:
        if k not in env:
            continue
        del env[k]


def prepend_path(new_path: str) -> None:
    global env
    old_path = env['PATH']
    env['PATH'] = f'{new_path}:{old_path}'
