import numpy as np
import zipfile
import os


def line_to_data(line, np_array=True, dtype=int):
    """
    Return an array of data with each value being of type dtype.
    The values are extracted from line, which is separated by spaces by default.
    if np_array is true, returns a numpy array, otherwise returns a python List.
    """
    if np_array:
        return np.fromstring(line, dtype=dtype, sep=" ")
    else:
        return [dtype(x) for x in line.split(" ")]


def zip_dir(in_dir, out_loc, ext=None):
    """
    Zip up in_dir to out_loc, optionally only taking files with given ext.
    """
    zipf = zipfile.ZipFile(out_loc, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(in_dir):
        for f in files:
            if ext is not None:
                if os.path.splitext(f)[-1] == ext:
                    zipf.write(os.path.join(root, f), os.path.relpath(
                        os.path.join(root, f), os.path.join(out_loc, '..')))
            else:
                zipf.write(os.path.join(root, f), os.path.relpath(
                    os.path.join(root, f), os.path.join(out_loc, '..')))
    zipf.close()
    print("Wrote zip file with source code to {}".format(out_loc))
