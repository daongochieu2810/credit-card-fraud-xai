import numpy as np


class FeatureStore(object):

    def __init__(self, store):
        self.db = store

    def _key(self, key):
        return key

    def put(self, key, value):
        self.db[self._key(key)] = value

    def get(self, key, default_value):
        if self._key(key) not in self.db:
            return np.array(default_value)
        return np.array(self.db[self._key(key)])
