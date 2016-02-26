import os.path as path
import os
def ensure_dir(dir):
    if not path.exists(dir):
        os.makedirs(dir)

