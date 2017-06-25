import os
from typing import Callable, Optional, TypeVar

T = TypeVar('T')


class Config:
    def __init__(self, reader: Callable[[str], Optional[str]]):
        self._os_env_reader = reader

    def get_string_or_none(self, key: str) -> Optional[str]:
        return self._os_env_reader(key)

    def safe_parse_string(self, key: str, dflt: str, fn: Callable[[str], T]) -> T:
        value = self.get_string_or_none(key)
        if value is None:
            value = dflt
        try:
            return fn(value)
        except Exception as e:
            raise ConfigParseError(key, str(e), e)

    def safe_parse_or_value(self, key: str, dflt: T, fn: Callable[[str], T]) -> T:
        value = self.get_string_or_none(key)
        if value is None:
            return dflt
        else:
            try:
                return fn(value)
            except Exception as e:
                raise ConfigParseError(key, str(e), e)


class ConfigError(Exception):

    def __init__(self, key: str, message: str, cause: Optional[Exception]=None):
        super().__init__('ConfigError(key={}): {}'.format(key, message))
        self.cause = cause


class ConfigParseError(ConfigError):

    def __init__(self, key: str, message: str, cause: Optional[Exception]=None):
        super().__init__(key, message, cause)


class ConfigMissingKeyError(ConfigError):

    def __init__(self, key: str, message: str):
        super().__init__(key, message)


env = Config(lambda k: os.environ.get(k))
