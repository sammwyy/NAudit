import os

def get_path(path):
    file = os.path.dirname(__file__)
    current = os.path.join(file, "..")
    return os.path.join(current, path)

def get_tmp(path):
    tmp = get_path("tmp")
    return os.path.join(tmp, path)

def walk_dir(dir, ext):
    files = []
    for root, dirs, filenames in os.walk(dir):
        for child in dirs:
            files += walk_dir(os.path.join(root, child), ext)

        for filename in filenames:
            if filename.endswith(ext):
                files.append(os.path.join(root, filename))

    return files
