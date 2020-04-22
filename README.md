# Sinagot

Sinagot is a Python library to manage data processing with **scripts** on a **dataset**. 
Sinagot is able to batch scripts runs with a simple API. 
Parallelization of data processing is made possible by [Dask.distributed](https://distributed.dask.org/en/latest/). 

## Installation

Sinagot is available on PyPi:

```bash
pip install sinagot
```

## Full Documentation

<https://sinagot.readthedocs.io>

## Concept

*Dataset* are structured around some core concept : **record**, **subset**, **task**, **modality** and **script**. 
A *record*, identified by its unique ID, corresponds to a recording session where experimental *tasks* are performed, 
generating data of various *modalities*. Raw data of a **record** are processed with **scripts** to generate more useful data.

> The idea of Sinagot emerged for the data management of an EEG platform called SoNeTAA :
> https://research.pasteur.fr/en/project/sonetaa/ .
> 
> For documentation purpose SoNeTAA dataset structure will be used as example. 

On SoNeTAA, a record with an ID with timestamp info in this format `REC-[YYMMDD]-[A-Z]`, 
for example `"REC-200331-A"`. 

For a record, 3 tasks are performed: `"RS"`, `"MMN"` and `"HDC"`,
2 main modalities handle data for every tasks: `"EEG"` and `"clinical"`, and a third one `"behavior"` exists only for HDC.

## Demo with SoNeTAA example 

### Create a Dataset instance

Import Dataset class

```python
>>> from sinagot import Dataset
```

A `Dataset` instance needs 3 things: 

- A config file in toml format.
- A folder containing the dataset
- A folder containing all the scripts

To instantiate a dataset use the config file path as argument:

```python
>>> ds = Dataset('/path/to/conf')
>>> ds
<Dataset instance | task: None, modality: None>
```

> Be sure that dataset path and scripts path are correctly set in the config file

### Explore records

You can list all records ids:

```python
>>> for id in ds.ids():
...     print(id)
...
REC-200331-A
REC-200331-B
```

Create a `Record` instance. For a specific record:

```python
>>> rec = ds.get('REC-200331-A')
>>> rec
<Record instance | id: REC-200331-A, task: None, modality: None>
```

Or the first record found:

```python
>>> ds.first()
<Record instance | id: REC-200331-B, task: None, modality: None>
```

> Records are not sort by their ids.

### run scripts

You can run all scripts for each record of the dataset:

```python
>>> ds.run()
2020-03-31 16:03:58,869 : Begin step run
...
2020-03-31 16:03:58,869 : Step run finished
```

Or for a single record:

```python
>>> rec.run()
2020-03-31 16:06:57,313 : Begin step run
...
2020-03-31 16:06:57,314 : Step run finished
```

### Explore by task or modality

Each dataset or record has **subscopes** corresponding to their tasks and modalities
simply accessible by self attributes with the scope name.

For example to select only the task RS of the dataset:

```python
>>> ds.RS
<Subset instance | task: RS, modality: None>
```

> A dataset subscope is a **subset**.

Or the EEG modality of a record:

```python
>>> rec.EEG
<Record instance | id: REC-200331-A, task: None, modality: EEG>
```

You can select a specific couple of task and modality (called **unit**):

```python
>>> ds.RS.EEG
<Subset instance | task: RS, modality: EEG>
>>> ds.EEG.RS
<Subset instance | task: RS, modality: EEG>
```
