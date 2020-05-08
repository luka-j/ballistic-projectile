from zipfile import ZipFile, ZIP_BZIP2
import os


def compress(filename: str, output: str, method=ZIP_BZIP2, name_inside_zip=None, keep_original=True):
    out = ZipFile(output, "w", method)
    out.write(filename, name_inside_zip)
    out.close()
    if not keep_original:
        os.remove(filename)


def uncompress(filename: str, output: str):
    zipfile = ZipFile(filename, "r")
    zipfile.extractall(output)
    zipfile.close()
