import click
from storage.database import Database

@click.group()
def alerts():
    pass


@alerts.command()
def show():

    db = Database()
    alerts = db.get_alerts()

    for a in alerts:
        print(f"[{a[3]}] {a[1]} : {a[2]}")


@alerts.command()
def clear():

    db = Database()
    db.clear_alerts()

    print("Alerts cleared")