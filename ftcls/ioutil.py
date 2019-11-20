import pathlib
from pathlib import Path
import csv
import json

# Storage Interfaces
# (k-v manner)
# - Create
# - Read
# - Modify

# Profile Interfaces
#
#
# TODO: Dump dirty for exiting gracefully (register to...)


class Profile:
    def __init__(self, path, conf_name, default_config, path_prefix=""):
        self.dirty = False
        self.path = Path(path_prefix).joinpath(path)
        self.conf_name = conf_name
        self.conf_path = self.path.joinpath(conf_name)
        if self.conf_path.exists():
            self.load()
        else:
            self.path.mkdir(parents=True, exist_ok=True)
            self.config = default_config
            self.dump()
        self.path.mkdir(parents=True, exist_ok=True)

    def load(self):
        with open(self.conf_path, "r") as f:
            self.config = json.load(f)

    def dump(self):
        with open(self.conf_path, "w") as f:
            json.dump(self.config, f)

    def set_key(self, k, v):
        self.config[k] = v
        self.dump()

    def get_key(self, k):
        return self.config[k]


class ProjectProfile(Profile):
    def __init__(self, pid, path_prefix="instance/test/project/"):
        str_pid = str(pid)
        self.pid = pid
        super().__init__(str_pid, str_pid + ".json", {"pid": pid}, path_prefix=path_prefix)


class DatasetStorage(Profile):
    def __init__(self, dsid, parser=None):
        # dsid looks like 'pid-dsindex', e.g. 1-5
        str_dsindex, str_pid = [str(_) for _ in dsid.split('-')]
        self.pid = pid
        super().__init__(str_dsid, str_pid + ".json", {})


class AnnotationStorage(Profile):
    def __init__(self):
        pass

