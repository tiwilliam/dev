import hashlib
import os
from typing import Optional

from dev import environment
from dev.helpers import run_command


class HashCacheHelper:
    cache_prefix = f'/opt/dev/cache/{environment.name}'

    @classmethod
    def read_hash(cls, key):
        if not os.path.exists(f'{cls.cache_prefix}/{key}'):
            return None
        return open(f'{cls.cache_prefix}/{key}').read()

    @classmethod
    def write_hash(cls, key, hash):
        if not os.path.isdir(cls.cache_prefix):
            run_command(f'mkdir -p {cls.cache_prefix}', silent=True)
        with open(f'{cls.cache_prefix}/{key}', 'w+') as fp:
            fp.write(hash)

    @classmethod
    def has_changed(cls, key, hash):
        old_hash = cls.read_hash(key)
        return old_hash != hash

    @classmethod
    def hash_data(cls, data: str):
        hash_object = hashlib.sha1(data.encode())
        return hash_object.hexdigest()

    @classmethod
    def changed(cls, key: str, data: Optional[str] = None, filename: Optional[str] = None) -> bool:
        if filename:
            data = open(filename).read()
        elif not data:
            raise RuntimeError('Neither filename or data was passed')

        key_hash = cls.hash_data(key)
        new_data_hash = cls.hash_data(data)
        has_changed = cls.has_changed(key_hash, new_data_hash)
        if has_changed:
            cls.write_hash(key_hash, new_data_hash)
        return has_changed
