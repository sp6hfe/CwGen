import os
import hashlib
import urllib.request


def get_file_from_web(file_url, file_path):
    """Downloads specified file from provided URL and store in selected location.
        In order to keep data integrity file after downloading is saved with
        suffix and later on is renamed to the original name assuring already
        existing file gets deleted.

    Args:
        file_url  (str): URL of the file to download
        file_path (str): Path to the resulting file (incl. file name)

    Returns:
        bool: True when file was downloaeded, False on error
    """

    TEMP_FILE_SUFFIX = '_tmp'
    is_file_downloaded = True

    # make sure directories are there
    file_directory = os.path.dirname(file_path)
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    # download the file with temporary suffix
    temp_file_path = file_path + TEMP_FILE_SUFFIX
    try:
        urllib.request.urlretrieve(file_url, temp_file_path)
    except urllib.error.URLError:
        is_file_downloaded = False

    if is_file_downloaded:
        # verify if another copy already exist
        if os.path.exists(file_path):
            os.remove(file_path)

        # rename downloaded file
        os.rename(temp_file_path, file_path)

    return is_file_downloaded


def md5(file_path):
    """Calculate MD5 hash out of provided file

    Args:
        file_path (str): Path to the file to calculate MD5 out of

    Returns:
        string: A string containing HEX representation of calculated MD5 hash
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for data_chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(data_chunk)

    return hash_md5.hexdigest()
