#!/bin/bash
export PATH=${MLC_CONDA_BIN_PATH}:$PATH

KMP_BLOCKTIME=${KMP_BLOCKTIME:-10}

export KMP_BLOCKTIME=${KMP_BLOCKTIME}
export KMP_AFFINITY=granularity=fine,compact,1,0
export LD_PRELOAD=${LD_PRELOAD}:${CONDA_PREFIX}/lib/libiomp5.so
export LD_PRELOAD=${LD_PRELOAD}:${CONDA_PREFIX}/lib/libtcmalloc.so

export num_physical_cores=`lscpu -b -p=Core,Socket | grep -v '^#' | sort -u | wc -l`
num_numa=$(numactl --hardware|grep available|awk -F' ' '{ print $2 }')

NUM_PROC=${NUM_PROC:-$num_numa}
CPUS_PER_PROC=$((num_physical_cores/num_numa))
WORKERS_PER_PROC=${WORKERS_PER_PROC:-1}
TOTAL_SAMPLE_COUNT=13368
BATCH_SIZE=${MLC_MLPERF_LOADGEN_BATCH_SIZE:-8}
TIMESTAMP=$(date +%m-%d-%H-%M)
HOSTNAME=$(hostname)
#OUTPUT_DIR=offline-output-${HOSTNAME}-batch-${BATCH_SIZE}-procs-${NUM_PROC}-ins-per-proc-${WORKERS_PER_PROC}-${TIMESTAMP}

export WORKLOAD_DATA=${MLC_HARNESS_CODE_ROOT}/data
export VALIDATION_DATA_JSON=${WORKLOAD_DATA}/validation-data/cnn_dailymail_validation.json

cd ${MLC_HARNESS_CODE_ROOT}
OUTPUT_DIR="${MLC_MLPERF_OUTPUT_DIR}"

USER_CONF="${MLC_MLPERF_USER_CONF}"


cmd="python runner.py --workload-name gptj \
	--scenario ${MLC_MLPERF_LOADGEN_SCENARIO} \
	--mode ${LOADGEN_MODE} \
	--num-proc ${NUM_PROC} \
	--cpus-per-proc ${CPUS_PER_PROC} \
	--model-checkpoint-path ${CHECKPOINT_DIR} \
	--dataset-path ${VALIDATION_DATA_JSON} \
	--batch-size ${BATCH_SIZE} \
	--mlperf-conf ${MLC_MLPERF_CONF} \
	--user-conf ${MLC_MLPERF_USER_CONF} \
	--precision ${PRECISION} \
	--pad-inputs \
	--quantized-model ${QUANTIZED_MODEL}  \
	--workers-per-proc ${WORKERS_PER_PROC} \
	--total-sample-count ${TOTAL_SAMPLE_COUNT} \
	--output-dir ${OUTPUT_DIR} \
	2>&1 | tee ${OUTPUT_DIR}.log"

echo "$cmd"
eval "$cmd"
