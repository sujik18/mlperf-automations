# Get SPEC Power Daemon
This [CM script](https://github.com/mlcommons/ck/blob/master/cm/docs/specs/script.md) git clones the [SPEC Power Daemon](https://github.com/mlcommons/power) used by MLPerf for power measurements.

## Commands
To install
```
cm run script --tags=get,mlperf,power,src
```

## Exported Variables
* `MLC_SPEC_PTD_PATH'`: Path to the PTDaemon
* `MLC_MLPERF_PTD_PATH'`: Path to the PTDaemon (same as `MLC_SPEC_PTD_DAEMON`)

## Supported and Tested OS
1. Ubuntu 18.04, 20.04, 22.04
2. RHEL 9
