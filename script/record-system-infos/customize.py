from cmind import utils
import os
import shutil
import psutil       # used to measure the system infos(have not tested for obtaining gpu info)
import json         # used to write the measurements to json file
from datetime import datetime, timezone        
import time

# format of time measurement in mlperf logs
#:::MLLOG {"key": "power_begin", "value": "07-20-2024 17:54:38.800", "time_ms": 1580.314812, "namespace": "mlperf::logging", "event_type": "POINT_IN_TIME", "metadata": {"is_error": false, "is_warning": false, "file": "loadgen.cc", "line_no": 564, "pid": 9473, "tid": 9473}}
#:::MLLOG {"key": "power_end", "value": "07-20-2024 17:54:39.111", "time_ms": 1580.314812, "namespace": "mlperf::logging", "event_type": "POINT_IN_TIME", "metadata": {"is_error": false, "is_warning": false, "file": "loadgen.cc", "line_no": 566, "pid": 9473, "tid": 9473}}


def preprocess(i):

    os_info = i['os_info']

    if os_info['platform'] == 'windows':
        return {'return':1, 'error': 'Windows is not supported in this script yet'}

    env = i['env']

    if env.get("CM_RUN_DIR", "") == "":
        env['CM_RUN_DIR'] = os.getcwd()
    
    logs_dir = env.get('CM_LOGS_DIR', env['CM_RUN_DIR'])

    log_json_file_path = os.path.join(logs_dir, 'sys_utilisation_info.json')

    interval = int(env.get('CM_SYSTEM_INFO_MEASUREMENT_INTERVAL', '2'))

    print(f"The system dumps are created to the folder:{logs_dir}")

    print("WARNING: Currently the script is in its development stage. Only memory measurements supports as of now!")

    print("Started measuring system info!")

    while True:
        memory = psutil.virtual_memory()
        cpu_util = psutil.cpu_percent(interval=0)
        total_memory_gb = memory.total / (1024 ** 3)  
        used_memory_gb = memory.used / (1024 ** 3)    

        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cpu_utilisation': cpu_util,
            'total_memory_gb': total_memory_gb,
            'used_memory_gb': used_memory_gb
        }

        # Append data to JSON file
        with open(log_json_file_path, 'a') as f:
            json.dump(data, f)
            f.write(',\n')  # Add newline for readability

        time.sleep(interval)

    return {'return':0}

def postprocess(i):

    env = i['env']

    return {'return':0}
