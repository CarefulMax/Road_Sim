import os


def rcpath(rel_path: str) -> str:
    rel_path = rel_path.lstrip('/')
    return os.path.join(os.getcwd(), rel_path)
