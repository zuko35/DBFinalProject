from nicegui import ui

current_user = {"id": None, "name": None}


def do_logout():
    current_user["id"] = None
    current_user["name"] = None
    ui.navigate.to("/")
