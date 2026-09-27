import os

from appdirs import user_data_dir

_DIR_APP_NAME = "labelu"


def get_data_dir():
    # LABELU_DATA_DIR overrides the per-user default so the SQLite db and media
    # can live next to the project (e.g. ./data) when running locally.
    data_dir = os.environ.get("LABELU_DATA_DIR") or user_data_dir(appname=_DIR_APP_NAME)
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
