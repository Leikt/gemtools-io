# General

gemtoolsio allows basic manipulations of the files and string, including symetrical encryption.

For the moment, only this file extensions are managed: toml, yml, yaml, json, ini. However, it is possible to add custom loaders.

Some of the functions are usable from cli : `python -m gemtoolsio --help`

## Userful functions
### load_file(path: Union\[str, PathLike\]) -> Any
- path: Path to the file to load

```python
from gemtoolsio import load_file
data = load_file('data.json')
```

The package will automatically detect the extension and try to load it with the matching loader.

### save_file(path: Union\[str, PathLike\], data: Any, allow_overwrite: bool = False)
- path: Path where to save the file
- data: Any serialiazable data, typically dicts, lists and primaries
- allow_overwrite: If True, the existing file will be replaced by the new one. Use this parameter carefully

```python
from gemtoolsio import save_file

save_file('data.json', data)
#>>> Will create the data.json file and store the json dumps of data

save_file('data.json', other_data)
#>>> WIll raise a Permission exception because data.json already exists

save_file('data.json', other_data, allow_overwrite=True)
#>>> Will erase existing data.json and replace them with other_data
```

