import helpers
import os
import platform
import subprocess


class Ebook2Cw:
    def __init__(self, executable_folder):
        """Class initialization.
            Setup internal data and detect if running on supported OS.
            Supported OSes: Windows, Linux.
        """

        BASE_URL = 'https://fkurz.net/ham/ebook2cw/'
        EXECUTABLE_BASE_NAME = 'ebook2cw'
        HASH_FILE_NAME = 'md5sums-bin.txt'
        CHANGELOG_FILE_NAME = 'ChangeLog'

        self.is_os_supported = False

        # assembly paths and urls
        ebook2cw_folder = os.path.normpath(executable_folder)
        if os.path.isfile(executable_folder):
            ebook2cw_folder = os.path.normpath(
                os.path.dirname(os.path.abspath(executable_folder)))

        self.executable_url = BASE_URL + EXECUTABLE_BASE_NAME
        self.executable_local_path = os.path.normpath(os.path.join(
            ebook2cw_folder, EXECUTABLE_BASE_NAME))

        self.hash_file_url = BASE_URL + HASH_FILE_NAME
        self.hash_file_local_path = os.path.normpath(os.path.join(
            ebook2cw_folder, HASH_FILE_NAME))

        self.changelog_file_url = BASE_URL + CHANGELOG_FILE_NAME
        self.changelog_file_local_path = os.path.normpath(os.path.join(
            ebook2cw_folder, CHANGELOG_FILE_NAME))

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
                executable_md5 = helpers.md5(self.executable_local_path)

                with open(os.path.normpath(self.hash_file_local_path), mode="r") as md5_file:
                    for line in md5_file:
                        md5_data = line.strip().split(None, 1)

                        # verify calculated and provided hash
                        if executable_file_name == md5_data[1] and executable_md5 == md5_data[0]:
                            is_verified = True
                            break

        return is_verified

    def _is_executable_present(self):
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

    def os_supported(self):
        """Returns if current OS is supported.
            If not all fuctionalities will fail.

        Args:
            None

        Returns:
            bool: True when OS is supported, False otherwise
        """

        return self.is_os_supported

    def get_executable_version_online(self):
        version = '0'

        if self.is_os_supported:
            helpers.get_file_from_web(
                self.changelog_file_url, self.changelog_file_local_path)

            if os.path.exists(self.changelog_file_local_path):
                with open(self.changelog_file_local_path, 'r') as changelog:
                    data = changelog.readline()
                extracted_version = data.split()[0]
                # basic check for version length which is at least X.Y.Z
                if len(extracted_version) >= 5:
                    version = extracted_version

        return version

    def get_executable_version_local(self):
        version = '0'

        if self.is_os_supported and self._is_executable_present():
            output = subprocess.Popen(
                [self.executable_local_path, "-h"], stdout=subprocess.PIPE).communicate()[0].decode()
            # correct response is: file_name version
            if len(output) > 0:
                extracted_version = output.split('\n', 1)[0].split()[1]
                # basic check for version length which is at least X.Y.Z
                if len(extracted_version) >= 5:
                    version = extracted_version

        return version

    def get_executable(self, force_latest=True):
        """Downloads latest version of the ebook2cw (OS speciffic)
            performing download integrity check by MD5 verification.
            When not forced it checks if executable exist locally.
            In case of not supported OS none of above is not performed.

        Args:
            force_latest (bool): Forces to download latest version

        Returns:
            bool: True when executable is available, False otherwise
        """

        if_got_executable = False

        if self.is_os_supported:
            # when not forced verify if downloaded already
            if not force_latest and os.path.exists(self.executable_local_path):
                if_got_executable = True
            else:
                # download files (executable + md5)
                helpers.get_file_from_web(
                    self.executable_url, self.executable_local_path)
                helpers.get_file_from_web(
                    self.hash_file_url, self.hash_file_local_path)

                if os.path.exists(self.executable_local_path) and os.path.exists(self.hash_file_local_path):
                    # verify executable's integrity
                    if self._verify_executable_against_md5_file():
                        if_got_executable = True
                    else:
                        # md5 mismatch - remove files
                        os.remove(self.executable_local_path)
                        os.remove(self.hash_file_local_path)

        return if_got_executable
