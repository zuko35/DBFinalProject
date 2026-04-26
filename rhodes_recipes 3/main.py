from nicegui import ui

import home_page
import saved_page
import login_page


if __name__ in {"__main__", "__mp_main__"}:
    print("Starting Rhodes Recipes  ->  http://localhost:8080")
    ui.run(title="Rhodes Recipes", port=8080)
