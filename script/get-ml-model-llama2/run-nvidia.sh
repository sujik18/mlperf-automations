#!/bin/bash

echo "Set tp size is ${MLC_NVIDIA_TP_SIZE}"
echo "Set pp size is ${MLC_NVIDIA_PP_SIZE}"

if [[ ! -e ${MLC_NVIDIA_MLPERF_SCRATCH_PATH}/models/Llama2/Llama-2-70b-chat-hf ]]; then
  mkdir -p ${MLC_NVIDIA_MLPERF_SCRATCH_PATH}/models/Llama2/Llama-2-70b-chat-hf
  cd ${LLAMA2_CHECKPOINT_PATH}
  cp -r ${LLAMA2_CHECKPOINT_PATH}/* ${MLC_NVIDIA_MLPERF_SCRATCH_PATH}/models/Llama2/Llama-2-70b-chat-hf
  test $? -eq 0 || exit $?
fi

echo "cd ${MLC_TENSORRT_LLM_CHECKOUT_PATH}"
cd ${MLC_TENSORRT_LLM_CHECKOUT_PATH}

make -C docker build
test $? -eq 0 || exit $?

if [ "${MLC_NVIDIA_TP_SIZE}" -eq 1 ]; then
  RUN_CMD="bash -c 'git lfs install && git lfs pull && python3 scripts/build_wheel.py -a=${MLC_GPU_ARCH} --clean --install --use_ccache --trt_root /usr/local/tensorrt/ && python examples/quantization/quantize.py --dtype=float16  --output_dir=/mnt/models/Llama2/fp8-quantized-ammo/llama2-70b-chat-hf-tp${MLC_NVIDIA_TP_SIZE}pp${MLC_NVIDIA_PP_SIZE}-fp8-02072024 --model_dir=/mnt/models/Llama2/Llama-2-70b-chat-hf --qformat=fp8 --kv_cache_dtype=fp8 --tp_size ${MLC_NVIDIA_TP_SIZE} --pp_size ${MLC_NVIDIA_PP_SIZE}'"
else
  RUN_CMD="bash -c 'git lfs install && git lfs pull && python3 scripts/build_wheel.py -a=${MLC_GPU_ARCH} --clean --install --use_ccache --trt_root /usr/local/tensorrt/ && python examples/quantization/quantize.py --dtype=float16  --output_dir=/mnt/models/Llama2/fp8-quantized-ammo/llama2-70b-chat-hf-tp${MLC_NVIDIA_TP_SIZE}pp${MLC_NVIDIA_PP_SIZE}-fp8 --model_dir=/mnt/models/Llama2/Llama-2-70b-chat-hf --qformat=fp8 --kv_cache_dtype=fp8 --tp_size ${MLC_NVIDIA_TP_SIZE} --pp_size ${MLC_NVIDIA_PP_SIZE}'"
fi
# TODO: check whether --device nvidia.com/gpu=all would work for docker
DOCKER_RUN_ARGS=" -v ${MLC_NVIDIA_MLPERF_SCRATCH_PATH}:/mnt -u $(id -u):$(id -g) --userns=keep-id --device nvidia.com/gpu=all -e NVIDIA_VISIBLE_DEVICES=all"
export DOCKER_RUN_ARGS="$DOCKER_RUN_ARGS"
export RUN_CMD="$RUN_CMD"
make -C docker run LOCAL_USER=1
test $? -eq 0 || exit $?

echo "MLPerf Nvidia scratch path is:${MLC_NVIDIA_MLPERF_SCRATCH_PATH}"
