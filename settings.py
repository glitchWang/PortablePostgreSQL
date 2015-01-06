#-*- coding: UTF-8 -*-
from __future__ import print_function
import os.path

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

class _D(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            tv = type(v)
            if tv in (int, str, unicode):
                setattr(self, k, v)
            elif tv == dict:
                inner_d = _D(**v)
                setattr(self, k, inner_d)
            elif tv in (list, tuple):
                values = []
                for i, elem in enumerate(v):
                    type_elem = type(elem)
                    if type_elem in (int, str, unicode):
                        values.append(elem)
                    elif type_elem == dict:
                        values.append(_D(**elem))
                setattr(self, k, tv(values))

    def __repr__(self):
        d = dict()
        for k, v in self.__dict__.items():
            tv = type(v)
            if tv in (int, str, unicode):
                pass
            elif tv == dict:
                pass
        return ''

settings = {
    'engines_dir': os.path.join(ROOT_DIR, 'App'),
    'data_dir': os.path.join(ROOT_DIR, 'Data'),
    'liveness_test_threshold': 10
}
config = _D(**settings)
__all__ = ['config']