#!/Users/abhiuppal/miniforge3/envs/lowe/bin/python
# This file creates command line utilities for the Lowe
# WORK IN PROGRESS

import click
from lowe.edd.autoedd import news_release_numbers
from lowe.locations.lookup import search as location_search


@click.group()
@click.option("--debug/--no-debug", type=bool, default=False)
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """Setup Click with a debug mode"""
    ctx.obj = {"debug": debug}


# ----------------------------
# EDD Command Group
# ----------------------------


@cli.group()
def edd():
    """Command group for EDD data-related utilities"""
    pass


@edd.command()
@click.argument("file", type=str, nargs=1)
@click.option("--num_results", "-n", type=int, default=10)
def news(fname: str = "./edd/data/RIVE$HWS.xlsx", num_top_results: int = 10):
    """[summary]

    Parameters
    ----------
    fname : str, optional
        [description], by default "./edd/data/RIVE.xlsx"
    num_top_results : int, optional
        [description], by default 10
    """
    news_release_numbers(fname=fname, num_top_results=num_top_results)


cli.add_command(edd)
edd.add_command(news)

# ----------------------------
# Locations Command Group
# ----------------------------


@cli.command()
@click.argument("locationtype", type=str, nargs=1)
@click.argument("query", type=str, nargs=1)
# @click.option("searchon", "-s", default=None, type=str)
def search(locationtype, query):
    res = location_search(query=query, codetype=locationtype, search_on=None)
    click.echo(res)
    return None


def main():
    cli(obj={})


if __name__ == "__main__":
    # Run the Click CLI interface
    cli(obj={})
