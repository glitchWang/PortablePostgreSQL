#-*- coding: UTF-8 -*-
from __future__ import print_function
import os, os.path
import glob
from settings import config

class Database(object):
    @staticmethod
    def db_engines(cls):
        config.engines_dir

    def __init__(self, engine_dir):
        pass

    def init_cluster(self):
        pass

    @property
    def cluster_dir(self):
        pass