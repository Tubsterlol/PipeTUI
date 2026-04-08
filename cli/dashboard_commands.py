import click
from utils.dashboard import start_dashboard


@click.command()
def dashboard():

    start_dashboard()