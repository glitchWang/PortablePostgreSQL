#-*- coding: UTF-8 -*-
from __future__ import print_function
import os, os.path
import subprocess
import shutil
import linecache
from settings import config
import psutil

def find_in_dir(path, name):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.abspath(os.path.join(root, name))

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()

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

    def _run_and_exit(self, cmd, *args):
        c = '{} {}'.format(os.path.join(self.engine_dir, 'bin', cmd), ' '.join(args))
        cmd_line = '{} {}'.format(c, ' '.join(args))
        return subprocess.call(cmd_line).pid

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
                raise IOError('cluster directory exists at {} and rebuild == {}'.format(self.cluster_dir_name, rebuild))
        self._run('initdb -D {} -A trust'.format(self.cluster_dir_name))

    @property
    def pid(self):
        pid_files = list(find_in_dir(self.cluster_dir_name, 'postmaster.pid'))
        if pid_files:
            return int(linecache.getline(pid_files[0], 1).strip('\r\n'))
        return -1

    @property
    def running(self):
        if self.cluster_dir_exists:
            return psutil.pid_exists(self.pid)
        return False

    @property
    def log_file_name(self):
        return os.path.join(self.cluster_dir_name, 'postgresql.log')

    def stop(self, force=False):
        if self.running:
            pid = self.pid
            if pid:
                cmd = 'pg_ctl stop -D {}'.format(self.cluster_dir_name)
                self._run(cmd)
            if psutil.pid_exists(pid):
                # this is the best shot if pg_ctl stop doesn't work
                kill_proc_tree(pid)
            if psutil.pid_exists(pid):
                raise IOError('Cannot kill the postgresql server using pid:{}'.format(pid))

    def start(self, restart=False):
        if self.cluster_dir_exists:
            if self.running:
                if restart:
                    self.stop(force=True)
            cmd = 'pg_ctl start -D {} -l {}'.format(self.cluster_dir_name, self.log_file_name)
            self._run_and_exit(cmd)
        else:
            raise IOError('cluster dir does not exist:{}, create it before serving'.format(self.cluster_dir_name))

    def __repr__(self):
        return '<PostgreSQL version:{}, dir:{}>'.format(self.version, self.engine_dir)