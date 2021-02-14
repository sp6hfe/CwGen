import helpers
import os
import platform


class Ebook2Cw:
    def __init__(self, base_path):
        self.base_path = base_path
        self.base_url = 'https://fkurz.net/ham/ebook2cw/'
        self.executable_base_name = 'ebook2cw'
        self.hash_file_name = 'md5sums-bin.txt'
        self.storage_folder = 'ebook2cw'

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

                    if split_data[1] == file_name and split_data[0] == self._md5(file_path):
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

        BASE_URL = 'https://fkurz.net/ham/ebook2cw/'
        EXECUTABLE_BASE_NAME = 'ebook2cw'
        HASH_FILE_NAME = 'md5sums-bin.txt'

        current_os = platform.system()
        if current_os == 'Windows' or current_os == 'Linux':
            cwgen_path = os.path.dirname(sys.argv[0])
            executable_local_base_path = os.path.normpath(os.path.join(
                cwgen_path, 'ebook2cw'))

            # prepare files urls/paths
            executable_name = EXECUTABLE_BASE_NAME
            if current_os == 'Windows':
                executable_name += '.exe'
            executable_url = BASE_URL + executable_name
            executable_local_path = os.path.normpath(os.path.join(
                executable_local_base_path, executable_name))

            hash_file_url = BASE_URL + HASH_FILE_NAME
            hash_file_local_path = os.path.normpath(os.path.join(
                executable_local_base_path, HASH_FILE_NAME))

            # download files (executable + md5)
            helpers.get_file_from_web(
                executable_url, executable_local_path)
            helpers.get_file_from_web(
                hash_file_url, hash_file_local_path)

            # verify executable integrity
            if self._verify_executable_against_md5_file(
                    executable_local_path, hash_file_local_path):
                if_downloaded_ok = True
            else:
                os.remove(executable_local_path)

        return if_downloaded_ok
