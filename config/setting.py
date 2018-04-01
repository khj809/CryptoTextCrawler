import os
import json
import logging.config

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config')
_settings_conf = 'settings.json'
_logging_conf = 'logging.conf'

with open(os.path.join(CONFIG_PATH, _settings_conf)) as config:
    settings = json.load(config)

# setups for logging
settings['common']['log_path'] = os.path.join(PROJECT_ROOT, settings['common']['log_path'])
os.system('mkdir -p %s' % settings['common']['log_path'])
logging.config.fileConfig(os.path.join(CONFIG_PATH, _logging_conf))

# setups for results
result_paths = settings['common']['result_path']
for key in result_paths.keys():
    result_paths[key] = os.path.join(PROJECT_ROOT, result_paths[key])
os.system('mkdir -p %s' % result_paths['base'])
os.system('mkdir -p %s' % result_paths['english'])
os.system('mkdir -p %s' % result_paths['korean'])
os.system('mkdir -p %s' % result_paths['japanese'])
os.system('mkdir -p %s' % result_paths['chinese'])
