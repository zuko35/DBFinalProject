"""Global app state and small helpers that act on it."""
from nicegui import ui

# Module-level dict so other modules read/write the same instance.
current_user = {"id": None, "name": None}


def do_logout():
    current_user["id"] = None
    current_user["name"] = None
    ui.navigate.to("/")
