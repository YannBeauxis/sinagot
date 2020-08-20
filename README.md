# Sinagot

Sinagot is a Python library to batch multiple **scripts** on a file-system **dataset** with a simple API.
Parallelization of data processing is made possible by [Dask.distributed](https://distributed.dask.org/en/latest/). 

## Installation

Sinagot is available on PyPi:

```bash
pip install sinagot
```

## Full Documentation

<https://sinagot.readthedocs.io>

## Concept

Sinagot main class is build around the `sinagot.Workspace` class. To create an instance, you must provide 3 pathes to :

- A configuration file in `.toml` format.
- A data folder.
- A scripts fodler.

<img src="https://github.com/YannBeauxis/sinagot/raw/master/docs/workspace_structure.png" width="200">

Dataset is structured as a collection of **records**. A record is identified by an unique ID but many files can be generated for a single record. Those files are processed with **scripts** which generate other files as results.

## Basic example 

### Harbor workspace

You can find in "example" folder of the git the [harbor](https://github.com/YannBeauxis/sinagot/tree/master/example/harbor) workspace that has a record per day of a harbor occupancy. In this example, a record is created each day to count the boats that occupy the harbor. The record ID include a timestamp for the day of recording.

In Unix environment, you can that type this to get the workspace :

```bash
wget -qO- https://github.com/YannBeauxis/sinagot/raw/master/example/harbor.tar.gz | tar xvz
```

To create the workspace instance :

```python
>>> from sinagot import Workspace
>>> ws = Workspace('/path/to/harbor/workspace/folder')
>>> ws
<Workspace instance>
```

### Explore records

You can list all records ids:

```python
>>> list(ws.records.iter_ids())
['REC-20200602', 'REC-20200603', 'REC-20200601']
```

Create a `Record` instance. For a specific record:

```python
>>> ws.records.get('REC-20200603')
<Record instance | id: REC-20200603>
```

Or the first record found:

```python
>>> ws.records.first()
<Record instance | id: REC-20200602>
```

> Records are not sort by their ids.

### run scripts

You can run all scripts for each record of the dataset:

```python
>>> ws.steps.run()
REC-20200602 | 2020-08-20 11:19:11,530 | count : Init run
REC-20200602 | 2020-08-20 11:19:11,531 | count : Processing run
REC-20200602 | 2020-08-20 11:19:11,556 | count : Run finished
...
REC-20200601 | 2020-08-20 11:19:11,625 | mean : Init run
REC-20200601 | 2020-08-20 11:19:11,626 | mean : Processing run
REC-20200601 | 2020-08-20 11:19:11,634 | mean : Run finished

```

Or for a single record:

```python
>>> ws.records.get('REC-20200603').steps.run()
REC-20200603 | 2020-08-20 11:28:32,588 | count : Init run
REC-20200603 | 2020-08-20 11:28:32,590 | count : Processing run
REC-20200603 | 2020-08-20 11:28:32,616 | count : Run finished
REC-20200603 | 2020-08-20 11:28:32,619 | mean : Init run
REC-20200603 | 2020-08-20 11:28:32,621 | mean : Processing run
REC-20200603 | 2020-08-20 11:28:32,637 | mean : Run finished
```

## More complex dataset

You can handle more complexity of dataset structure with **task** and **modality** concepts. During a recording session for a single record, data can be generate for differents task and each task can generate different kind of data called **modality**. 

### SoNeTAA usecase

The idea of Sinagot emerged for the data management of an EEG platform called SoNeTAA :
https://research.pasteur.fr/en/project/sonetaa/ .

For documentation purpose SoNeTAA workspace structure will be used as example. 

On SoNeTAA, a record with an ID with timestamp info in this format `REC-[YYMMDD]-[A-Z]`, 
for example `"REC-200331-A"`. 

For a record, 3 tasks are performed: 

* "RS" for Resting State
* "MMN" for MisMatch Negativity
* "HDC" for Human Dynamic Clamp.

3 modalities handle data depending of the tasks
* For each tasks, "EEG" modality create data from ElectroEncephalogram .
* A "behavior" modality create date only for HDC task.
* A "clinical" modality handle data used for every task.

### Explore by task or modality

Each record collection or single record has **subscopes** corresponding to their tasks and modalities accessible as attribute.

For example to select only the task RS of the dataset:

```python
>>> ws.RS
<RecordCollection instance | task: RS, modality: None>
```

> A dataset subscope is a **RecordCollection**.

Or the EEG modality of a record:

```python
>>> rec.EEG
<Record instance | id: REC-200331-A, task: None, modality: EEG>
```

You can select a specific couple of task and modality (called **unit**):

```python
>>> ws.RS.EEG
<RecordCollection instance | task: RS, modality: EEG>
>>> ws.EEG.RS
<RecordCollection instance | task: RS, modality: EEG>
```
