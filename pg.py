#-*- coding: UTF-8 -*-
from __future__ import print_function
import os, os.path
import subprocess
import shutil
from settings import config

def find_in_dir(path, name):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.abspath(os.path.join(root, name))

class Database(object):
    @classmethod
    def db_engines(cls):
        psqls = find_in_dir(config.engines_dir, 'psql.exe')
        for psql in psqls:
            engine_dir = os.path.abspath(os.path.join(os.path.dirname(psql), '..'))
            yield Database(engine_dir)

    def __init__(self, engine_dir):
        self.engine_dir = engine_dir

    def _run(self, cmd, *args):
        c = '{} {}'.format(os.path.join(self.engine_dir, 'bin', cmd), ' '.join(args))
        cmd_line = '{} {}'.format(c, ' '.join(args))
        return subprocess.check_output(cmd_line)

    @property
    def version(self):
        return self._run('psql.exe --version').strip('\r\n').split(' ')[-1]

    @property
    def version_tuple(self):
        return tuple([int(d) for d in self.version.split('.')])

    @property
    def cluster_dir_name(self):
        m1, m2, _ = self.version_tuple
        d = os.path.join(config.data_dir, '{}.{}'.format(m1, m2))
        return d

    @property
    def cluster_dir_exists(self):
        return os.path.isdir(self.cluster_dir_name)

    def init_cluster(self, rebuild=False):
        if self.cluster_dir_exists:
            if rebuild:
                shutil.rmtree(self.cluster_dir_name)
            else:
                raise IOError('cluster directory exists at {} and rebuild parameters == True'.format(self.cluster_dir_name))
        self._run('initdb -D {}'.format(self.cluster_dir_name))

    def __repr__(self):
        return '<PostgreSQL version:{}, dir:{}>'.format(self.version, self.engine_dir)