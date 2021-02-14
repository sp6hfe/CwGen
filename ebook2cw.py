import helpers
import os
import platform


class Ebook2Cw:
    def __init__(self, base_path, data_folder):
        """Class initialization"""

        BASE_URL = 'https://fkurz.net/ham/ebook2cw/'
        EXECUTABLE_BASE_NAME = 'ebook2cw'
        HASH_FILE_NAME = 'md5sums-bin.txt'

        self.executable_url = BASE_URL + EXECUTABLE_BASE_NAME
        self.executable_local_path = os.path.normpath(os.path.join(
            base_path, data_folder, EXECUTABLE_BASE_NAME))

        self.hash_file_url = BASE_URL + HASH_FILE_NAME
        self.hash_file_local_path = os.path.normpath(os.path.join(
            base_path, data_folder, HASH_FILE_NAME))

    def _verify_executable_against_md5_file(self, file_path, md5_file_path):
        """Verifies if file's calculated MD5 hash match the one stored in other file.
            File with pre-calculated MD5 hashes should contain
            a row with hash and file name separated by space.

        Args:
            file_path     (str): Path to the file being verified
            md5_file_path (str): Path to the file containing pre-calculated MD5 hashes

        Returns:
            bool: True when MD5 verification succeeded, False otherwise

        """

        is_verified = False

        if os.path.exists(file_path) and os.path.exists(md5_file_path):
            file_name = os.path.basename(file_path)

            with open(os.path.normpath(md5_file_path), mode="r") as md5_file:
                for line in md5_file:
                    split_data = line.strip().split(None, 1)

                    if split_data[1] == file_name and split_data[0] == helpers.md5(file_path):
                        is_verified = True
                        break

        return is_verified

    def get_executable(self):
        """Downloads latest version of the ebook2cw (OS speciffic)
            performing download integrity check by MD5 verification.

        Args:
            None

        Returns:
            bool: True when executable was downloaded, False otherwise
        """

        if_downloaded_ok = False

        current_os = platform.system()
        if current_os == 'Windows' or current_os == 'Linux':
            # add exe extension for Windows
            if current_os == 'Windows':
                self.executable_url += ".exe"
                self.executable_local_path += '.exe'

            # download files (executable + md5)
            helpers.get_file_from_web(
                self.executable_url, self.executable_local_path)
            helpers.get_file_from_web(
                self.hash_file_url, self.hash_file_local_path)

            # verify executable integrity
            if self._verify_executable_against_md5_file(
                    self.executable_local_path, self.hash_file_local_path):
                if_downloaded_ok = True
            else:
                os.remove(self.executable_local_path)

        return if_downloaded_ok
