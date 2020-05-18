from zipfile import ZipFile, ZIP_BZIP2
import os


def compress(filename: str, output: str, method=ZIP_BZIP2, name_inside_zip=None, keep_original=True):
    """
    Compress a file to zip/bzip/whatever.
    :param filename: file to be compressed
    :param output: output file to be created
    :param method: output format
    :param name_inside_zip: how should the file be called inside the zip
    :param keep_original: should original file be kept or removed after compression
    :return:
    """
    out = ZipFile(output, "w", method)
    out.write(filename, name_inside_zip)
    out.close()
    if not keep_original:
        os.remove(filename)


def uncompress(filename: str, output: str, method=ZIP_BZIP2):
    """
    Uncompress a zip/bzip/whatever file.
    :param filename: filename to be uncompressed
    :param output: file to be created (where to uncompress the contents)
    :param method: input format
    :return:
    """
    zipfile = ZipFile(filename, "r", method)
    zipfile.extractall(output)
    zipfile.close()
