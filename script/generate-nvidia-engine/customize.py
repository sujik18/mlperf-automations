from mlc import utils
import os
import shutil


def preprocess(i):

    os_info = i['os_info']

    if os_info['platform'] == 'windows':
        return {'return': 1, 'error': 'Windows is not supported in this script yet'}

    if 'MLC_MODEL' not in env:
        return {
            'return': 1, 'error': 'Please select a variation specifying the model to run'}
    if 'MLC_MLPERF_DEVICE' not in env:
        return {
            'return': 1, 'error': 'Please select a variation specifying the device to run on'}

    # will later extend to other scenarios
    scenarios = env['MLC_LOADGEN_SCENARIO']
    cmd = " --action generate_engines " +\
          " --benchmarks " + env['MLC_MODEL'] + \
          " --scenarios " + scenarios + \
          " --gpu_batch_size=" + env['MLC_MODEL_BATCH_SIZE'] +\
          " --gpu_copy_streams=" + env['MLC_GPU_COPY_STREAMS'] +\
          " --workspace_size=" + env['MLC_TENSORRT_WORKSPACE_SIZE']


~
return {'return': 0}


def postprocess(i):

    env = i['env']
    return {'return': 0}
