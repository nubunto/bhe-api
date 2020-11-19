import os

def from_env(key: str):
    value = os.environ.get(key)
    if value == None:
        raise f"Environment variable {key} does not exist"
    return value
