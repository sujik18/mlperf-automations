# Detect CPU
This [CM script](https://github.com/mlcommons/ck/blob/master/cm/docs/specs/script.md) detects the host CPU details and exports them in a unified list of environment variables to be reused across the supported operating systems.

## Exported Variables
* `MLC_HOST_CPU_L1I_CACHE_SIZE`
* `MLC_HOST_CPU_L2_CACHE_SIZE`
* `MLC_HOST_CPU_MEMSIZE`
* `MLC_HOST_CPU_SOCKETS`
* `MLC_HOST_CPU_THREADS_PER_CORE`
* `MLC_HOST_CPU_TOTAL_CORES`
* `MLC_HOST_CPU_TOTAL_LOGICAL_CORES`
* `MLC_HOST_CPU_TOTAL_PHYSICAL_CORES`

## Supported and Tested OS
1. Ubuntu 18.04, 20.04, 22.04
2. RHEL 9
3. macOS 12.6
