# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["sinagot", "sinagot.models", "sinagot.plugins"]

package_data = {"": ["*"]}

install_requires = [
    "json-log-formatter>=0.3.0,<0.4.0",
    "pandas>=1.0.2,<2.0.0",
    "toml>=0.10.0,<0.11.0",
]

setup_kwargs = {
    "name": "sinagot",
    "version": "latest",
    "description": "Python library to manage data processing on a dataset.",
    "long_description": '# Sinagot\n\nSinagot is a Python library to manage data processing with **scripts** on a **dataset**. \nSinagot is able to batch scripts runs with a simple API. \nParallelization of data processing is made possible by [Dask.distributed](https://distributed.dask.org/en/latest/). \n\n## Installation\n\nSinagot is available on PyPi:\n\n```bash\npip install sinagot\n```\n\n## Full Documentation\n\n<https://sinagot.readthedocs.io/en/latest/>\n\n## Concept\n\n*Dataset* are structured around some core concept : **record**, **subset**, **task**, **modality** and **script**. \nA *record*, identified by its unique ID, corresponds to a recording session where experimental *tasks* are performed, \ngenerating data of various *modalities*. Raw data of a **record** are processed with **scripts** to generate more useful data.\n\n> The idea of Sinagot emerged for the data management of an EEG platform called SoNeTAA :\n> https://research.pasteur.fr/en/project/sonetaa/ .\n> \n> For documentation purpose SoNeTAA dataset structure will be used as example. \n\nOn SoNeTAA, a record with an ID with timestamp info in this format `REC-[YYMMDD]-[A-Z]`, \nfor example `"REC-200331-A"`. \n\nFor a record, 3 tasks are performed: `"RS"`, `"MMN"` and `"HDC"`,\n2 main modalities handle data for every tasks: `"EEG"` and `"clinical"`, and a third one `"behavior"` exists only for HDC.\n\n## Demo with SoNeTAA example \n\n### Create a Dataset instance\n\nImport Dataset class\n\n```python\n>>> from sinagot import Dataset\n```\n\nA `Dataset` instance needs 3 things: \n\n- A config file in toml format.\n- A folder containing the dataset\n- A folder containing all the scripts\n\nTo instantiate a dataset use the config file path as argument:\n\n```python\n>>> ds = Dataset(\'/path/to/conf\')\n>>> ds\n<Dataset instance | task: None, modality: None>\n```\n\n> Be sure that dataset path and scripts path are correctly set in the config file\n\n### Explore records\n\nYou can list all records ids:\n\n```python\n>>> for id in ds.ids():\n...     print(id)\n...\nREC-200331-A\nREC-200331-B\n```\n\nCreate a `Record` instance. For a specific record:\n\n```python\n>>> rec = ds.get(\'REC-200331-A\')\n>>> rec\n<Record instance | id: REC-200331-A, task: None, modality: None>\n```\n\nOr the first record found:\n\n```python\n>>> ds.first()\n<Record instance | id: REC-200331-B, task: None, modality: None>\n```\n\n> Records are not sort by their ids.\n\n### run scripts\n\nYou can run all scripts for each record of the dataset:\n\n```python\n>>> ds.run()\n2020-03-31 16:03:58,869 : Begin step run\n...\n2020-03-31 16:03:58,869 : Step run finished\n```\n\nOr for a single record:\n\n```python\n>>> rec.run()\n2020-03-31 16:06:57,313 : Begin step run\n...\n2020-03-31 16:06:57,314 : Step run finished\n```\n\n### Explore by task or modality\n\nEach dataset or record has **subscopes** corresponding to their tasks and modalities\nsimply accessible by self attributes with the scope name.\n\nFor example to select only the task RS of the dataset:\n\n```python\n>>> ds.RS\n<Subset instance | task: RS, modality: None>\n```\n\n> A dataset subscope is a **subset**.\n\nOr the EEG modality of a record:\n\n```python\n>>> rec.EEG\n<Record instance | id: REC-200331-A, task: None, modality: EEG>\n```\n\nYou can select a specific couple of task and modality (called **unit**):\n\n```python\n>>> ds.RS.EEG\n<Subset instance | task: RS, modality: EEG>\n>>> ds.EEG.RS\n<Subset instance | task: RS, modality: EEG>\n```\n',
    "author": "Yann Beauxis",
    "author_email": "dev@yannbeauxis.net",
    "maintainer": "Yann Beauxis",
    "maintainer_email": "dev@yannbeauxis.net",
    "url": "https://github.com/YannBeauxis/sinagot",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.6.1,<4.0.0",
}


setup(**setup_kwargs)
