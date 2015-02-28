#-*- coding: UTF-8 -*-
from __future__ import print_function
import os
import os.path
import time
import subprocess
import datetime
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


def read_line(fname, lineno):
    linecache.clearcache()
    return linecache.getline(fname, lineno).strip('\r\n')


def from_time_stamp(ts):
    return datetime.datetime.fromtimestamp(long(ts))


class ClusterInstance(object):

    def __init__(self, fname):
        self.fname = fname
        self.properties = {
            'pid': (1, int),
            'data_dir': (2, str),
            'uptimestamp': (3, from_time_stamp),
            'port': (4, int),
            'domain_socket_path': (5, str),
            'listen_addr': (6, str),
        }

    @property
    def running(self):
        if os.path.isfile(self.fname):
            return psutil.pid_exists(self.pid)
        return False

    def __getattr__(self, name):
        if os.path.isfile(self.fname):
            if name in self.properties:
                lineno, convert = self.properties[name]
                return convert(read_line(self.fname, lineno))
        return None

    def __repr__(self):
        return '<ClusterInstance from {}>'.format(self.fname)


class Database(object):

    @classmethod
    def db_engines(cls):
        psqls = find_in_dir(config.engines_dir, 'psql.exe')
        for psql in psqls:
            engine_dir = os.path.abspath(
                os.path.join(os.path.dirname(psql), '..'))
            yield Database(engine_dir)

    def __init__(self, engine_dir):
        self.engine_dir = engine_dir

    def _run(self, cmd, *args):
        c = '{} {}'.format(
            os.path.join(self.engine_dir, 'bin', cmd), ' '.join(args))
        cmd_line = '{} {}'.format(c, ' '.join(args))
        return subprocess.check_output(cmd_line)

    def _run_and_exit(self, cmd, *args):
        c = '{} {}'.format(
            os.path.join(self.engine_dir, 'bin', cmd), ' '.join(args))
        cmd_line = '{} {}'.format(c, ' '.join(args))
        return subprocess.call(cmd_line)

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

    @property
    def instance(self):
        fname = os.path.join(self.cluster_dir_name, 'postmaster.pid')
        return ClusterInstance(fname)

    @property
    def log_file_name(self):
        return os.path.join(self.cluster_dir_name, 'postgresql.log')

    def _ensure_engine_status(self, bool_state):
        for n in range(0, config.liveness_test_threshold):
            if bool_state == self.instance.running:
                return True
            else:
                time.sleep(1)
        return bool_state == self.instance.running

    def init_cluster(self, rebuild=False):
        if self.cluster_dir_exists:
            if rebuild:
                shutil.rmtree(self.cluster_dir_name)
            else:
                raise IOError('cluster directory exists at {} and rebuild == {}'.format(
                    self.cluster_dir_name, rebuild))
        self._run('initdb -D {} -A trust'.format(self.cluster_dir_name))

    def stop(self):
        if self.instance.running:
            pid = self.instance.pid
            if pid:
                cmd = 'pg_ctl stop -D {}'.format(self.cluster_dir_name)
                self._run_and_exit(cmd)
                if not self._ensure_engine_status(False):
                    self.kill_proc_tree(pid)
                    if not self._ensure_engine_status(False):
                        raise IOError(
                            'Cannot kill the postgresql server using pid:{}'.format(pid))

    def start(self, restart=False):
        if self.cluster_dir_exists:
            if self.instance.running:
                if restart:
                    self.stop()
            cmd = 'pg_ctl start -D {} -l {}'.format(
                self.cluster_dir_name, self.log_file_name)
            self._run_and_exit(cmd)
            if not self._ensure_engine_status(True):
                raise IOError('postmaster.pid still not exist under {}, start might fail'.format(
                    self.cluster_dir_name))
        else:
            raise IOError('cluster dir does not exist:{}, create it before serving'.format(
                self.cluster_dir_name))

    def psql(self):
        self._run_and_exit('psql.exe')

    def __repr__(self):
        return '<PostgreSQL version:{}, dir:{}>'.format(self.version, self.engine_dir)
