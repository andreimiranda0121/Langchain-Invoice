import hashlib

def hash_file(file):
    hasher = hashlib.md5()
    hasher.update(file.getvalue())
    return hasher.hexdigest()
