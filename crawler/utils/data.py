import os
import glob
import logging
import regex as re
import sqlite3
from . import _settings
from .locale import classify_locale

try:
    conn = sqlite3.connect(_settings['database'], isolation_level=None)
    cur = conn.cursor()
    cur.execute(
    """CREATE TABLE IF NOT EXISTS steemit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    author TEXT NOT NULL,
    permlink TEXT NOT NULL,
    status BOOLEAN NOT NULL DEFAULT 1
    );"""
    )
except:
    logging.error('Failed to get connection to sqlite3 database')
    exit(-1)


def get_cursor():
    return conn.cursor()


# legacy function
def _get_new_filename(path, prefix):
    filenames = glob.glob(os.path.join(path, '%s_*.txt' % prefix))
    nums = sorted(list(map(lambda x: int(re.findall('\d+$', os.path.splitext(x)[0])[0]), filenames)) + [0])
    new_filename = '%s_%08d.txt' % (prefix, nums[-1] + 1)
    return os.path.join(path, new_filename)


def save_result(result, file, locale=None):
    if isinstance(result, str):
        result_string = result
    elif isinstance(result, list):
        result_string = '\n'.join(result)
    else:
        logging.error('Invalid file is given with type "%s"' % type(result).__name__)
        return

    locale = locale or classify_locale(result_string)

    save_path = _settings['result_path'][locale]
    # filename = _get_new_filename(save_path, prefix)
    filename = os.path.join(save_path, '%s.txt' % file)

    with open(filename, 'w', encoding='utf8') as f:
        f.write(result_string)
