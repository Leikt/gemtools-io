import argparse

from .tools import UnknownExtensionError, load_file, load_encrypted_file, decrypt_file, encrypt_file, \
    save_encrypted_file, save_file, generate_key, encrypt, decrypt, load_string, dump_string, register_string_dumper, \
    register_loader, register_dumper, register_string_loader

CMD = 'files'


def setup_main_parser(parser: argparse.ArgumentParser):
    parser.description = "Manage encrypted files."


def main(args):
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='gemtoolsio')
    subparsers = parser.add_subparsers(title='Sub-Command', dest='command')
    subparsers.required = True

    keygen_parser = subparsers.add_parser('key-gen')
    keygen_parser.description = 'Generate a new random encryption key.'
    keygen_parser.add_argument('path', type=Path, help='Path where to store the encryption key.')
    keygen_parser.add_argument('--allow-overwrite', action='store_true',
                               help='Allow the overwrite of the existing file. '
                                    'To use carefully because it can make existing '
                                    'encrypted files inaccessible.')

    encrypt_parser = subparsers.add_parser('encrypt')
    encrypt_parser.description = 'Encrypt the given file into a new one. Will add the extension ".fer" to the filename.'
    encrypt_parser.add_argument('path', type=Path, help='Path to the file to encrypt.')
    encrypt_parser.add_argument('key', type=Path, help='Path to the file containing the encryption key.')

    decrypt_parser = subparsers.add_parser('decrypt')
    decrypt_parser.description = 'Decrypt the given file into a new one.'
    decrypt_parser.add_argument('path', type=Path, help='Path to the file to encrypt (without the ".fer" extension).')
    decrypt_parser.add_argument('key', type=Path, help='Path to the file containing the encryption key.')

    args = parser.parse_args(args)

    if args.command == 'key-gen':
        args.path.parent.mkdir(exist_ok=True, parents=True)
        generate_key(args.path, allow_overwrite=args.allow_overwrite)
    elif args.command == 'encrypt':
        key = args.key.read_bytes()
        encrypt_file(args.path, key)
    elif args.command == 'decrypt':
        key = args.key.read_bytes()
        decrypt_file(args.path, key)
