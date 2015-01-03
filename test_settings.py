#-*-coding: utf-8-*-

from settings import _D

def test_setting_keys():
    s = {
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
    d = _D(**s)
    assert set(s.keys()) <= set(d.__dict__.keys())
    assert s['k1'] == d.k1
    assert s['k10'] == d.k10