import shutil
import unittest
from pathlib import Path

from cryptography import fernet
from cryptography.fernet import Fernet

from src.gemtoolsio import generate_key, save_encrypted_file, load_encrypted_file, encrypt_file, decrypt_file, encrypt, decrypt
from src.gemtoolsio.tools import _dumpers


class TestIOEncryption(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.key = fernet.Fernet.generate_key()
        shutil.rmtree('tmp', ignore_errors=True)
        cls.base_path = Path('tmp')
        Path('tmp').mkdir(exist_ok=True, parents=True)
        cls.data = {'key1': 'value1', 'key2': 2, 'key3': {'key4': ['A', 'B', 'C'], 'key5': 'value5'}}

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree('tmp', ignore_errors=True)

    def test_gen_key(self):
        key_path = self.base_path / 'test.ferkey'
        generate_key(key_path)
        with self.assertRaises(PermissionError):
            generate_key(key_path)
        generate_key(key_path, allow_overwrite=True)  # Should not raise any error

        key = key_path.read_bytes()
        Fernet(key)  # Should not raise any error

    def test_string_encryption(self):
        original = "Hello, World!"
        encrypted = encrypt(original, self.key)
        decrypted = decrypt(encrypted, self.key)
        self.assertEqual(original, decrypted)

    def test_io_file_encryption(self):
        for suffix in _dumpers.keys():
            path = self.base_path / f'test{suffix}'
            save_encrypted_file(path, self.key, self.data)
            loaded_data = load_encrypted_file(path, self.key)
            self.assertEqual(self.data, loaded_data)
            with self.assertRaises(PermissionError):
                save_encrypted_file(path, self.key, self.data)
            save_encrypted_file(path, self.key, self.data, allow_overwrite=True)

    def test_file_encryption(self):
        original = "Hello, World!"
        path = self.base_path / 'test.txt'
        path.write_text(original)

        encrypt_file(path, self.key)
        self.assertTrue(path.exists())
        self.assertNotEqual(original, path.read_text())

        decrypt_file(path, self.key)
        self.assertTrue(path.exists())
        self.assertEqual(original, path.read_text())
