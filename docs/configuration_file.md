## TOML format

The configuration file is in `.toml` : format https://github.com/toml-lang/toml

## File Name

The default file name is `workspace.toml` you can use a custom name if you specify it in configuration path :

```python
Worspace("folder_path/cusom_conf_name.toml")
```

## Required sections

### records

`id_pattern` is a regex pattern for record ID matching. For example :

```toml
[records]
    id_pattern = "REC-[\\d]{8}"
```

### steps

`scripts` List scripts name (without `.py` extension) to run in execution order. All scripts must correspond to ha ve in script folder

```toml
[steps]
    scripts = ["count", "mean"]
```

## Optional sections

### path

If you want to use custom path. Default is :

```toml
[path]
    dataset = './dataset'
    scripts = './scripts'
```

### run

If you want to use main process or Dask plugin. Default is :

```toml
[run]
    mode = "main_process"
```

### log

To customize logger. Default is :

```toml
[log]
    name = "sinagot"
    format = "%(asctime)s : %(message)s"
    level = 'INFO'
```

## Advanced sections

If you use tasks and modalities, you must provide *tasks* and *modalities* sections.

### tasks

```toml
[tasks]
    [tasks.RS]
        modalities = ["clinical", "EEG"]
    [tasks.MMN]
        modalities = ["clinical", "EEG"]
    [tasks.HDC]
        modalities = ["clinical", "EEG", "behavior"]
```

### modalities

```toml
[modalities]
    [modalities.EEG]
        file_match = [true, false]
        scripts = ['preprocess']
        task_scripts.RS = ['RS_alpha', 'RS_alpha_plot', "RS_PSD"]
        task_scripts.MMN = ['MMN_amplitude_latency', 'MMN_plot']
        task_scripts.HDC = ["HDC_PSD"]
    [modalities.behavior]
        scripts = ['scores', 'scores_norm', 'plot_scores']
    [modalities.clinical]
        models.plugin = "pandas"
        models.dataframe_path = ['CLINICAL', 'data.csv']
    [modalities.report]
        models.dataframe_path = ['CLINICAL', 'data.csv']
```

### processed

Optionaly you can specify *processed data* :

```toml
[processed]
    [processed.RS_alpha]
        task = "RS"
        modality = "EEG"
        step_label = "RS_alpha"
        path_label = "data"
        data_type = "float"
    [processed.behavior_raw_scores]
        task = "HDC"
        modality = "behavior"
        step_label = "scores"
        data_getter = "dataframe_from_csv"
    [processed.MMN_amplitude_latency]
        task = "MMN"
        modality = "EEG"
        step_label = "MMN_amplitude_latency"
        data_getter = "series_from_csv"
        path_label = "data"
```