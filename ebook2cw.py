import helpers
import os
import platform


class Ebook2Cw:
    def __init__(self, base_path, data_folder):
        """Class initialization.
            Setup internal data and detect if running on supported OS.
            Currently supported platforms: Windows, Linux.
        """

        BASE_URL = 'https://fkurz.net/ham/ebook2cw/'
        EXECUTABLE_BASE_NAME = 'ebook2cw'
        HASH_FILE_NAME = 'md5sums-bin.txt'

        self.is_os_supported = False

        # assembly paths and urls
        self.executable_url = BASE_URL + EXECUTABLE_BASE_NAME
        self.executable_local_path = os.path.normpath(os.path.join(
            base_path, data_folder, EXECUTABLE_BASE_NAME))

        self.hash_file_url = BASE_URL + HASH_FILE_NAME
        self.hash_file_local_path = os.path.normpath(os.path.join(
            base_path, data_folder, HASH_FILE_NAME))

        current_os = platform.system()

        # check for supported OS'es
        if current_os == 'Windows' or current_os == 'Linux':
            self.is_os_supported = True

            # add executable's 'exe' extension for Windows
            if current_os == 'Windows':
                self.executable_url += '.exe'
                self.executable_local_path += '.exe'

    def _verify_executable_against_md5_file(self):
        """Verifies if ebook2cw file's calculated MD5 hash match the one stored
            in relevant md5 file. Files are expected to exist in default location.
            File with pre-calculated MD5 hashes should contain a row with hash
            and file name separated by space.

        Args:
            None

        Returns:
            bool: True when MD5 verification succeeded, False otherwise
        """

        is_verified = False

        if self.is_os_supported:
            if os.path.exists(self.executable_local_path) and os.path.exists(self.hash_file_local_path):
                executable_file_name = os.path.basename(
                    self.executable_local_path)

                with open(os.path.normpath(self.hash_file_local_path), mode="r") as md5_file:
                    for line in md5_file:
                        md5_data = line.strip().split(None, 1)

                        # verify calculated and provided hash
                        executable_md5 = helpers.md5(
                            self.executable_local_path)
                        if executable_file_name == md5_data[1] and executable_md5 == md5_data[0]:
                            is_verified = True
                            break

        return is_verified

    def os_supported(self):
        """Returns if current OS is supported.
            If not all fuctionalities will fail.

        Args:
            None

        Returns:
            bool: True when OS is supported, False otherwise
        """

        return self.is_os_supported

    def is_executable_present(self, file_path):
        """Returns if ebook2cw executable is available in default directory.

        Args:
            None

        Returns:
            bool: True when executable is available, False otherwise
        """

        is_executable_available = False

        if self.is_os_supported:
            # check if file is there
            if os.path.exists(self.executable_local_path):
                is_executable_available = True

        return is_executable_available

    def get_executable(self):
        """Downloads latest version of the ebook2cw (OS speciffic)
            performing download integrity check by MD5 verification.
            In case of not supported OS download is not performed.

        Args:
            None

        Returns:
            bool: True when executable was downloaded and verified,
                   False otherwise
        """

        if_downloaded_ok = False

        if self.is_os_supported:
            # download files (executable + md5)
            helpers.get_file_from_web(
                self.executable_url, self.executable_local_path)
            helpers.get_file_from_web(
                self.hash_file_url, self.hash_file_local_path)

            # verify if both files were downloaded
            if os.path.exists(self.executable_local_path) and os.path.exists(self.hash_file_local_path):
                # verify executable's integrity
                if self._verify_executable_against_md5_file():
                    if_downloaded_ok = True
                else:
                    os.remove(self.executable_local_path)
                    os.remove(self.hash_file_local_path)

        return if_downloaded_ok
