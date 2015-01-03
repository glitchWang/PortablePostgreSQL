#-*- coding: UTF-8 -*-
from settings import config
import pprint

if __name__ == '__main__':
    for k,v in config.__dict__.items():
        pprint.pprint('{}:{}'.format(k, v))
    pprint.pprint(config.k7.__dict__)
    pprint.pprint(config.k6.__dict__)