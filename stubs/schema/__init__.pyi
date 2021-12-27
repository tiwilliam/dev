from typing import Any
from typing import Optional as TypingOptional


class Schema:
    def __init__(
        self,
        schema: Any,
        error: str = None,
        ignore_extra_keys: bool = False,
        name: str = None,
        description: str = None,
        as_reference: bool = False,
    ) -> None:
        ...

    def validate(self, data: TypingOptional[dict], **kwargs: str) -> dict:
        ...


class Optional:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class And:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class Or(And):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class SchemaError(Exception):
    ...

    @property
    def code(self) -> str:
        ...
