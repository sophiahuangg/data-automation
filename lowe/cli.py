import click
from lowe.edd.autoedd import news_release_numbers

@click.group()
@click.option("--debug/--no-debug", type=bool, default=False)
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """Setup Click with a debug mode"""
    ctx.obj = {"debug": debug}

