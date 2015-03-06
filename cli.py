#-*-coding: utf-8-*-
from __future__ import print_function
import click
import pg


@click.group()
def cli():
    pass


@click.command()
def ls():
    engines = pg.Database.db_engines()
    click.echo('\n'.join([repr(e) for e in engines]))


@click.command()
@click.argument('ver')
def init(ver):
    engine_path = './App/{}'.format(ver)
    engine = pg.Database(engine_path)
    if not engine.cluster_dir_exists:
        engine.init_cluster()


cli.add_command(ls)
cli.add_command(init)

if __name__ == '__main__':
    cli()
