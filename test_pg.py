#-*-coding: utf-8-*-
from pg import Database, find_in_dir
import shutil, os

def _rmtree(folder_name):
    try:
        shutil.rmtree(folder_name)
    except:
        pass

def test_find_file():
    files = list(find_in_dir('.', 'psql.exe'))
    assert 2 == len(files)

def test_find_engine():
    engines = list(Database.db_engines())
    assert 2 == len(engines)

def test_engine_version():
    engines = list(Database.db_engines())
    versions = list([e.version for e in engines])
    assert '9.3.5' in versions and '9.4.0' in versions

def test_engine_ver_tuple():
    engines = list(Database.db_engines())
    ver_tuples = list([e.version_tuple for e in engines])
    assert (9, 3, 5) in ver_tuples and (9, 4, 0) in ver_tuples

def test_empty_data_folder():
    engines = list(Database.db_engines())
    lower_ver_engine = filter(lambda e:e.version.startswith('9.3'), engines)
    higher_ver_engine = filter(lambda e:e.version.startswith('9.4'), engines)
    assert len(lower_ver_engine) > 0 and not lower_ver_engine[0].cluster_dir_exists
    assert len(higher_ver_engine) > 0 and not higher_ver_engine[0].cluster_dir_exists

def test_none_empty_data_folder():
    folder_name = './Data/9.3'
    try:
        os.makedirs(folder_name)
        engines = list(Database.db_engines())
        lower_ver_engine = filter(lambda e:e.version.startswith('9.3'), engines)
        assert len(lower_ver_engine) > 0 and lower_ver_engine[0].cluster_dir_exists
    finally:
        _rmtree(folder_name)

def test_init_cluster_from_scatch():
    db = Database('./App/9.3')
    folder_name = './Data/9.3'
    try:
        db.init_cluster()
        assert db.cluster_dir_exists
        assert os.path.abspath(folder_name) == db.cluster_dir_name
    finally:
        _rmtree(folder_name)

def test_rebuild_cluster():
    db = Database('./App/9.3')
    folder_name = './Data/9.3'
    try:
        os.makedirs(folder_name)
        db.init_cluster(rebuild=True)
        assert db.cluster_dir_exists
        assert os.path.abspath(folder_name) == db.cluster_dir_name
    finally:
        _rmtree(folder_name)


def test_rebuild_cluster_failed():
    db = Database('./App/9.4')
    folder_name = './Data/9.4'
    try:
        os.makedirs(folder_name)
        try:
            db.init_cluster()
        except IOError as e:
            assert True, 'IOError captured'
        else:
            assert False, 'Negative case, should not be here'
    finally:
        _rmtree(folder_name)

def test_engine_not_running_with_cluster():
    folder_name = './Data/9.4'
    try:
        db = Database('./App/9.4')
        db.init_cluster()
        assert db.cluster_dir_exists
        assert not db.running
    finally:
        _rmtree(folder_name)

def test_engine_not_running_with_cluster():
    db = Database('./App/9.4')
    assert not db.cluster_dir_exists
    assert not db.running

def test_stop_nothing():
    db = Database('./App/9.4')
    db.stop()
    assert True

def test_stop_with_cluster_initialized():
    db = Database('./App/9.4')
    db.init_cluster()
    assert db.cluster_dir_exists
    db.stop()
    assert True

def test_start_server():
    folder_name = './Data/9.4'
    try:
        db = Database('./App/9.4')
        db.init_cluster()
        db.start()
        assert db.running
        assert db.pid > 0
    finally:
        db.stop()
        _rmtree(folder_name)