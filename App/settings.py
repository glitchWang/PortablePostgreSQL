#-*- coding: UTF-8 -*-
from __future__ import print_function

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
                inner_list = []
                for i, elem in enumerate(v):
                    type_elem = type(elem)
                    if type_elem in (int, str, unicode):
                        inner_list.append(elem)
                    elif type_elem == dict:
                        inner_list.append(_D(**elem))
                setattr(self, k, inner_list)

    def __repr__(self):
        return u'abcdefg'

settings = {
    "k1": 'v1',
    'k2': 42,
    'k3': u'v3',
    'k4': [1,2,3],
    'k5': [1,'2'],
    'k6': {'kk1': 'vv1', 'kk2':42},
    'k7': {'kk1': 'vv1', 'kk2':[1,2,3], 'kk3': {'kkk1': 'vvv1', 'kkk2':'vvv2'}},
    'k8': (),
    'k9': (1,2,3),
    'k10': ('1',2,3)
}
config = _D(**settings)
__all__ = ['config']