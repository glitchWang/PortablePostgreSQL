#-*-coding: utf-8-*-
import click

@click.group()
def cli():
    pass

@click.command()
def ls():
    print()

if __name__ == '__main__':
    cli()