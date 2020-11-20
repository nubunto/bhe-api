import os

class EnvVarUnsetError(Exception):
    def __init__(self, key):
        self.key = key
        self.message = f"Key '{key}' was not set"

def from_env(key: str):
    value = os.environ.get(key)
    if value == None:
        raise EnvVarUnsetError(key)
    return value
