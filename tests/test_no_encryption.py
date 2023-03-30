import shutil
import unittest

from src.gemtools_io import dump_string, load_string, save_file, load_file
from src.gemtools_io.tools import _string_dumpers, _loaders, _dumpers


class TestIONoEncryption(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {'key1': 'value1', 'key2': 2, 'key3': {'key4': ['A', 'B', 'C'], 'key5': 'value5'}}

    def test_loaders_and_dumpers(self):
        self.assertEqual(_loaders.keys(), _string_dumpers.keys())
        self.assertEqual(_loaders.keys(), _dumpers.keys())

    def test_plain_text(self):
        for suffix in _loaders.keys():
            dumped_data = dump_string(self.data, suffix)
            loaded_data = load_string(dumped_data, suffix)
            self.assertEqual(self.data, loaded_data)

    def test_file(self):
        shutil.rmtree('tmp', ignore_errors=True)
        for suffix in _loaders.keys():
            filename = f'tmp/test{suffix}'
            save_file(filename, self.data)
            loaded_data = load_file(filename)
            self.assertEqual(self.data, loaded_data)
            with self.assertRaises(PermissionError):
                save_file(filename, self.data)
            save_file(filename, self.data, allow_overwrite=True)  # Should not raise any error
        shutil.rmtree('tmp')
