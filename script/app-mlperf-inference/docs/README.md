# README for app-mlperf-inference
This README is automatically generated. Please follow the [script execution document](https://docs.mlcommons.org/mlcflow/targets/script/execution-flow/) to understand more about the MLC script execution.

## Run Commands

```bash
mlcr app,vision,language,mlcommons,mlperf,inference,generic
```

### Script Inputs

| Name | Description | Choices | Default |
|------|-------------|---------|------|
| `--scenario` | MLPerf inference scenario | ['Offline', 'Server', 'SingleStream', 'MultiStream'] | `Offline` |
| `--mode` | MLPerf inference mode | ['performance', 'accuracy'] | `accuracy` |
| `--test_query_count` | Specifies the number of samples to be processed during a test run |  | `10` |
| `--target_qps` | Target QPS |  | `` |
| `--target_latency` | Target Latency |  | `` |
| `--max_batchsize` | Maximum batchsize to be used |  | `` |
| `--num_threads` | Number of CPU threads to launch the application with |  | `` |
| `--hw_name` | Valid value - any system description which has a config file (under same name) defined [here](https://github.com/mlcommons/cm4mlops/tree/main/script/get-configs-sut-mlperf-inference/configs) |  | `` |
| `--output_dir` | Location where the outputs are produced |  | `` |
| `--rerun` | Redo the run even if previous run files exist |  | `True` |
| `--regenerate_files` | Regenerates measurement files including accuracy.txt files even if a previous run exists. This option is redundant if `--rerun` is used |  | `` |
| `--adr.python.name` | Python virtual environment name (optional) |  | `mlperf` |
| `--adr.python.version_min` | Minimal Python version |  | `3.8` |
| `--adr.python.version` | Force Python version (must have all system deps) |  | `` |
| `--adr.compiler.tags` | Compiler for loadgen |  | `gcc` |
| `--adr.inference-src-loadgen.env.MLC_GIT_URL` | Git URL for MLPerf inference sources to build LoadGen (to enable non-reference implementations) |  | `` |
| `--adr.inference-src.env.MLC_GIT_URL` | Git URL for MLPerf inference sources to run benchmarks (to enable non-reference implementations) |  | `` |
| `--quiet` | Quiet run (select default values for all questions) |  | `False` |
| `--readme` | Generate README with the reproducibility report |  | `` |
| `--debug` | Debug MLPerf script |  | `` |
### Generic Script Inputs

| Name | Description | Choices | Default |
|------|-------------|---------|------|
| `--input` | Input to the script passed using the env key `MLC_INPUT` |  | `` |
| `--output` | Output from the script passed using the env key `MLC_OUTPUT` |  | `` |
| `--outdirname` | The directory to store the script output |  | `cache directory ($HOME/MLC/repos/local/cache/<>) if the script is cacheable or else the current directory` |
| `--outbasename` | The output file/folder name |  | `` |
| `--name` |  |  | `` |
| `--extra_cache_tags` | Extra cache tags to be added to the cached entry when the script results are saved |  | `` |
| `--skip_compile` | Skip compilation |  | `False` |
| `--skip_run` | Skip run |  | `False` |
| `--accept_license` | Accept the required license requirement to run the script |  | `False` |
| `--skip_system_deps` | Skip installing any system dependencies |  | `False` |
| `--git_ssh` | Use SSH for git repos |  | `False` |
| `--gh_token` | Github Token |  | `` |
| `--hf_token` | Huggingface Token |  | `` |
| `--verify_ssl` | Verify SSL |  | `False` |
