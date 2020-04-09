# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sinagot', 'sinagot.models', 'sinagot.plugins']

package_data = \
{'': ['*']}

install_requires = \
['json-log-formatter>=0.3.0,<0.4.0',
 'pandas>=1.0.2,<2.0.0',
 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'sinagot',
    'version': '0.1.0',
    'description': 'Python library to manage data processing on a dataset.',
    'long_description': None,
    'author': 'Yann Beauxis',
    'author_email': 'dev@yannbeauxis.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
