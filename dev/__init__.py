from typing import List

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__: List[str] = extend_path(__path__, __name__)  # noqa
