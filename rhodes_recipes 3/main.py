"""Rhodes Recipes — entry point.

Each `*_page.py` module registers its own `@ui.page` route on import,
so all this file does is wire them up and start the server.
"""
from nicegui import ui

# Importing these modules registers their routes with NiceGUI.
import home_page   # noqa: F401  → registers "/"
import saved_page  # noqa: F401  → registers "/saved"
import login_page  # noqa: F401  → registers "/login"


if __name__ in {"__main__", "__mp_main__"}:
    print("Starting Rhodes Recipes 🍴  →  http://localhost:8080")
    ui.run(title="Rhodes Recipes", port=8080, favicon="🍴")
