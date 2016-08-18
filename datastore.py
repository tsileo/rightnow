# coding: utf-8
from datetime import datetime
import json
import os
import signal

import plyvel

from config import CONFIG

DATA_PATH = os.path.expanduser('~/var/rightnow')


class DataStore(object):
    def __init__(self, name, data_path=None):
        if data_path is None:
            data_path = CONFIG.get('data_path', DATA_PATH)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self._root = os.path.join(data_path, name)
        self._makedirs(self._root)
        self._index = plyvel.DB(os.path.join(self._root, 'index'), create_if_missing=True)

    def close(self):
        return self._index.close()

    @staticmethod
    def _makedirs(path):
        if not os.path.exists(path):
            return os.makedirs(path)

    def _load(self):
        path = os.path.join(self._root, 'json')
        for root, dirs, files in os.walk(path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                b = fpath.split('/')
                print 'put', fpath
                self._index.put(''.join(b[-4:-1]) + 'T' +  b[-1].split('.')[0], '')


    def insert(self, data, dt=None):
        if dt is None:
            dt = datetime.utcnow()

        p = os.path.join(self._root, 'json', dt.strftime('%Y/%m/%d/'))
        self._makedirs(p)
        fname = dt.strftime('%H%M%S') + '.json'

        js = json.dumps(data)
        with open(os.path.join(p, fname), 'w+') as f:
            f.write(js)

        self._index.put(dt.strftime('%Y%m%dT%H%M%S'), '')

    def _key_dt(self, k):
        return datetime.strptime(k, '%Y%m%dT%H%M%S')

    def _open_key(self, dt):
        fpath = os.path.join(self._root, 'json', dt.strftime('%Y'), dt.strftime('%m'),
                             dt.strftime('%d'), dt.strftime('%H%M%S') + '.json')
        data = json.load(open(fpath, 'rb'))

        data['dt'] = dt

        return data

    def latest(self, dt=None):
        if dt is None:
            dt = datetime.utcnow()

        try:
            k = self._index.iterator(reverse=True).next()
            if k:
                return self._open_key(self._key_dt(k[0]))
        except StopIteration:
            pass

        return None
