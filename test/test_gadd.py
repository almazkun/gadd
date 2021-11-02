from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from unittest import TestCase

from git import Repo

from gadd import staged_files


class TestGadd(TestCase):
    """Test the Gadd

    Args:
        TestCase (TestCase): TestCase
    """

    def test_staged_files(self):
        with TemporaryDirectory(dir=".") as temp_dir:
            new_dir = temp_dir.split("/")[-1]
            with NamedTemporaryFile(dir=new_dir) as new_file:
                repo = Repo()
                new_file_name = "/".join(new_file.name.split("/")[-2:])

                repo.git.add(temp_dir)

                self.assertIn(new_file_name, staged_files())

                repo.git.rm(temp_dir, "--cached", "-r")


def not_used(file):
    """Should be found bu vulture
    d = {"ads": "asd", 'zxc': 'zxc'}
    Args:
        file ([type]): [description]
    """
    d = {"ads": "asd", "zxc": "zxc"}
    print(file)


def not_used_but_whitelisted(file):
    print(file)
