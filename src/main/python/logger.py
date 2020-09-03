import logging
import json


with open('settings.json') as f:
    file_content = f.read()
    data = json.loads(file_content)

log_dir = data['log_dir']
debug_file = data['debug_file']

def write_log():
    logging.basicConfig(
        format='|%(levelname)s|%(name)s|%(process)d:%(processName)s| %(lineno)d:%(funcName)s:%(filename)s %(message)s|%(pathname)s|',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_dir+"/"+debug_file, 'a', 'utf-8'),
            logging.StreamHandler()
        ])
    return logging
