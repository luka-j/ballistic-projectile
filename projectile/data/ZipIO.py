from zipfile import ZipFile, ZIP_BZIP2


def compress(filename: str, output: str, method=ZIP_BZIP2, name_inside_zip=None):
    out = ZipFile(output, "w", method, True, 8)
    out.write(filename, name_inside_zip)
    out.close()


def uncompress(filename: str, output: str):
    zipfile = ZipFile(filename, "r")
    zipfile.extractall(output)
    zipfile.close()
