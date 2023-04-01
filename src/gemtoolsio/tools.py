import json
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Union, Callable, TextIO, Optional

import toml
import yaml
from cryptography import fernet


class UnknownExtensionError(Exception):
    """Exception raised when trying to load/save a file with an extension that cannot be handled by the system."""


Loader = Callable[[Union[TextIO]], Any]
_loaders: dict[str, Loader] = {
    '.yml': yaml.safe_load,
    '.yaml': yaml.safe_load,
    '.json': json.load,
    '.toml': toml.load,
    '.ini': toml.load
}

StringLoader = Callable[[Union[str]], Any]
_string_loaders: dict[str, StringLoader] = {
    '.yml': yaml.safe_load,
    '.yaml': yaml.safe_load,
    '.json': json.loads,
    '.toml': toml.loads,
    '.ini': toml.loads
}

Dumper = Callable[[Any, Optional[TextIO]], None]
_dumpers: dict[str, Dumper] = {
    '.yml': yaml.safe_dump,
    '.yaml': yaml.safe_dump,
    '.json': json.dump,
    '.toml': toml.dump,
    '.ini': toml.dump
}

StringDumper = Callable[[Any], str]
_string_dumpers: dict[str, StringDumper] = {
    '.yml': yaml.safe_dump,
    '.yaml': yaml.safe_dump,
    '.json': json.dumps,
    '.toml': toml.dumps,
    '.ini': toml.dumps
}


def register_dumper(suffix: str, dumper: Dumper, allow_overwrite: bool = False):
    if suffix in _loaders and not allow_overwrite:
        raise PermissionError(f'"{suffix}" already has a dumper. Allow overwrite to force the replacement.')
    _dumpers[suffix] = dumper


def register_loader(suffix: str, loader: Loader, allow_overwrite: bool = False):
    if suffix in _loaders and not allow_overwrite:
        raise PermissionError(f'"{suffix}" already has a loader. Allow overwrite to force the replacement.')
    _loaders[suffix] = loader


def register_string_loader(suffix: str, loader: StringLoader, allow_overwrite: bool = False):
    if suffix in _loaders and not allow_overwrite:
        raise PermissionError(f'"{suffix}" already has a string loader. Allow overwrite to force the replacement.')
    _string_loaders[suffix] = loader


def register_string_dumper(suffix: str, dumper: StringDumper, allow_overwrite: bool = False):
    if suffix in _loaders and not allow_overwrite:
        raise PermissionError(f'"{suffix}" already has a string dumper. Allow overwrite to force the replacement.')
    _string_dumpers[suffix] = dumper


def load_file(path: Union[str, PathLike]) -> Any:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'No such file {path}')

    if path.suffix not in _loaders:
        msg = f'Cannot load data from {path.suffix} files'
        logging.critical(msg)
        raise UnknownExtensionError(msg)

    return _loaders[path.suffix](path.open('r'))


def load_string(stream: str, suffix: str) -> Any:
    if suffix not in _loaders:
        msg = f'Cannot load data from {suffix} format'
        logging.critical(msg)
        raise UnknownExtensionError(msg)

    return _string_loaders[suffix](stream)


def save_file(path: Union[str, PathLike], data: Any, allow_overwrite: bool = False):
    path = Path(path)
    if path.exists() and not allow_overwrite:
        msg = f'{path} already exists. To overwrite the file, use the allow_overwrite parameter.'
        logging.critical(msg)
        raise PermissionError(msg)
    path.parent.mkdir(exist_ok=True, parents=True)

    if path.suffix not in _dumpers:
        msg = f'Cannot save data to {path.suffix} files'
        logging.critical(msg)
        raise UnknownExtensionError(msg)

    _dumpers[path.suffix](data, path.open('w'))


def dump_string(obj: Any, suffix: str) -> str:
    if suffix not in _string_dumpers:
        msg = f'Cannot save data to {suffix} format'
        logging.critical(msg)
        raise UnknownExtensionError(msg)

    return _string_dumpers[suffix](obj)


def load_encrypted_file(path: Union[str, PathLike], key: bytes) -> Any:
    path = Path(path)
    data_string = fernet.Fernet(key).decrypt(path.read_bytes()).decode('utf-8')

    return load_string(data_string, path.suffix)


def save_encrypted_file(path: Union[str, PathLike], key: bytes, data: Any, allow_overwrite: bool = False):
    path = Path(path)
    if path.exists() and not allow_overwrite:
        msg = f'{path} already exists. To overwrite the file, use the allow_overwrite parameter.'
        logging.critical(msg)
        raise PermissionError(msg)
    path.parent.mkdir(exist_ok=True, parents=True)

    data_string = dump_string(data, path.suffix)

    real_path = path.parent / path.name
    if real_path.exists() and not allow_overwrite:
        msg = f'{real_path} already exists. To overwrite the file, use the allow_overwrite parameter.'
        logging.critical(msg)
        raise PermissionError(msg)

    data_bytes = fernet.Fernet(key).encrypt(data_string.encode('utf-8'))
    real_path.write_bytes(data_bytes)


def generate_key(path: Union[str, PathLike] = None, allow_overwrite=False) -> bytes:
    if path is not None:
        path = Path(path)
    key = fernet.Fernet.generate_key()
    if path is not None:
        if allow_overwrite is False and path.exists():
            msg = f'{path} already exists. To overwrite the file, use the allow_overwrite parameter.'
            logging.critical(msg)
            raise PermissionError(msg)

        path.write_bytes(key)
    return key


def encrypt_file(path: Union[str, PathLike], key: bytes):
    path = Path(path)
    data_bytes = path.read_bytes()
    data_bytes = fernet.Fernet(key).encrypt(data_bytes)
    path.write_bytes(data_bytes)


def encrypt(token: Union[str, bytes], key: bytes, encoding: str = 'utf-8') -> bytes:
    data_bytes = token.encode(encoding) if isinstance(token, str) else token
    return fernet.Fernet(key).encrypt(data_bytes)


def decrypt_file(path: Union[str, PathLike], key: bytes):
    path = Path(path)
    data_bytes = fernet.Fernet(key).decrypt(path.read_bytes())
    path.write_bytes(data_bytes)


def decrypt(token: Union[str, bytes], key: bytes, encoding: str = 'utf-8') -> str:
    return fernet.Fernet(key).decrypt(token).decode(encoding)
