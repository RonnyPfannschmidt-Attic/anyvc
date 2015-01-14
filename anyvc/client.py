# -*- coding: utf-8 -*-
"""
    Command line client for anyvc.

    :license: GPL2 or later
"""
from __future__ import unicode_literals
import os
import click
from . import workdir


@click.group()
@click.option('-d', '--working-directory',
              default=os.getcwd,

              help='The working directory')
@click.option('--ignored_workdirs',
              envvar='ANYVC_IGNORED_WORKDIRS',
              type=click.Path(), multiple=True)
@click.pass_context
def cli(ctx, working_directory, ignored_workdirs):

    repo = ctx.obj = workdir.open(working_directory, dont_try=ignored_workdirs)
    if repo is None:
        click.secho('missing repo in %s' % working_directory,
                    err=True, bold=True)
        raise click.Abort()

with_paths = click.argument('paths', type=click.Path(exists=True), nargs=-1)
with_revision = click.option('-r', '--revision', default=None)

list_letters = {
    'clean': '-',
    'unknown': '?',
    'modified': 'M',
    'added': 'A',
    'removed': 'D',
    'deleted': '!',
    'ignored': 'I',
}

list_colors = {
    # 'clean': '',
    'unknown': 'purple',
    'modified': 'red',
    'added': 'blue',
    'removed': 'blue',
    'deleted': 'yellow',
    'ignored': 'black',
}


def output_state(st, hidden_states):
    if st.state in hidden_states:
        return
    output = list_letters.get(st.state, '*').ljust(2)
    color = list_colors.get(st.state)
    click.secho(output + st.relpath, bold=True, fg=color)


@cli.command()
@click.pass_obj
@click.option('--list-all', '-a')
@with_paths
def status(vc, list_all, paths):
    hidden_states = () if list_all else ('clean', 'ignored', 'unknown')

    for st in vc.status(recursive=True):
        output_state(st, hidden_states)


@cli.command()
@click.pass_obj
@with_paths
def diff(vc, paths):
    diff = vc.diff(paths=paths)
    for line in diff.splitlines():
        colors = {'-': 'red', '+': 'green'}
        click.secho(line, fg=colors.get(line[0]),
                    bold=line[4:] in ('diff', '+++', '---'))


@cli.command()
@click.option('--message', '-m', default=None)
@click.pass_obj
@with_paths
def commit(vc, message, paths):
    out = vc.commit(
        message=message,
        paths=paths)
    click.echo(out)


@cli.command()
@click.pass_obj
@with_paths
def add(vc, paths):
    out = vc.add(paths=paths)
    click.echo(out)


@cli.command()
@click.argument('location', default=None, required=False)
@with_revision
@click.pass_obj
def push(vc, location, revision):
    repo = vc.repository
    if repo is None:
        click.echo("cant find local repo to push from", err=True)

    if not repo.local:
        # XXX: better handling
        name = type(repo).__name__
        click.echo("can't push from a non-local %s" % name, err=True)
        raise click.Abort()
    out = repo.push(location, revision)
    click.echo(out)
