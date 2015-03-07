#-*-coding: utf-8-*-
from __future__ import print_function
import click
import pg


def create_engine(ver):
    engine_path = './App/{}'.format(ver)
    engine = pg.Database(engine_path)
    return engine


@click.group()
def cli():
    pass


@click.command()
def ls():
    engines = pg.Database.db_engines()
    click.echo('\n'.join([repr(e) for e in engines]))


@click.command()
@click.argument('ver')
@click.option('--rebuild', default=False, is_flag=True)
def init(ver, rebuild):
    engine = create_engine(ver)
    if rebuild:
        engine.stop()
        engine.init_cluster(rebuild=True)
    else:
        if not engine.cluster_dir_exists:
            engine.init_cluster()


@click.command()
@click.argument('ver')
def start(ver):
    engine = create_engine(ver)
    engine.start()


@click.command()
@click.argument('ver')
def stop(ver):
    engine = create_engine(ver)
    engine.stop()


cli.add_command(ls)
cli.add_command(init)
cli.add_command(start)
cli.add_command(stop)

if __name__ == '__main__':
    cli()
