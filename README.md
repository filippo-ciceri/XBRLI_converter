# XBRLI_converter

XBRLi_converter is a Python package for conversion of XBRLi filings into simpler XBRL documents.

XBRLi_converter is one of the tools used to build [www.financialdatatree.com](https://www.financialdatatree.com/), an XBRL-powered website offering easy and free access to fundamental data from publicly traded US companies.
Visit [www.financialdatatree.com](https://www.financialdatatree.com/) for more details.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install XBRLi_converter.

```bash
pip install XBRLi_converter
```

## Usage

```python
import XBRLi_converter

files = ['goog-20201231.htm']

process_files(files)
```

To sort alphabetically the content of the resulting simplified XBRL file:

```python
process_files(files, sort=True)
```

The output files can be also automatically renamed using the `names` option:

```python
names = ['output_xbrl.xml']

process_files(files, sort=True, names=names)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)