from nicegui import ui

import database as db
from theme import BROWN, CREAM, GOLD, GRAY, RUST, SAGE, WHITE
from state import current_user
from widgets import header, star_display


@ui.page("/saved")
def show_saved_page():
    if not current_user["id"]:
        ui.navigate.to("/login")
        return

    ui.query("body").style(f"background:{CREAM}; margin:0;")
    header("My Saved")

    with ui.column().style("padding:24px 32px; gap:20px; max-width:1200px; margin:auto;"):

        saved          = db.get_saved_recipes(current_user["id"])
        shopping       = db.get_shopping_list(current_user["id"])
        saved_drinks   = db.get_saved_drinks(current_user["id"])
        drink_shopping = db.get_drink_shopping_list(current_user["id"])

        with ui.row().style("align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;"):
            ui.label("My Saved Items").style(
                f"font-size:1.3rem; font-weight:700; color:{BROWN}; font-family:Georgia,serif;"
            )
            ui.button("Back to Browse", on_click=lambda: ui.navigate.to("/")).style(
                f"background:{RUST}; color:{WHITE}; border-radius:8px; font-weight:600;"
            )

        s_tabs = ui.tabs().style(
            f"color:{RUST}; background:{WHITE}; border-radius:12px; "
            "box-shadow:0 2px 8px rgba(0,0,0,.08); padding:4px;"
        )
        with s_tabs:
            s_tab_recipes = ui.tab(f"Recipes ({len(saved)})")
            s_tab_drinks  = ui.tab(f"Drinks ({len(saved_drinks)})")

        with ui.tab_panels(s_tabs, value=s_tab_recipes).style("background:transparent; width:100%;"):
            _render_saved_recipes(s_tab_recipes, saved, shopping)
            _render_saved_drinks(s_tab_drinks, saved_drinks, drink_shopping)


def _render_saved_recipes(tab, saved, shopping):
    with ui.tab_panel(tab):
        if saved:
            with ui.row().style("flex-wrap:wrap; gap:16px;"):
                for r in saved:
                    with ui.card().style(
                        f"background:{WHITE}; border-radius:12px; width:260px; "
                        "box-shadow:0 2px 8px rgba(0,0,0,.1);"
                    ):
                        with ui.column().style("padding:16px; gap:6px;"):
                            ui.label(r["recipe_name"]).style(
                                f"font-weight:700; color:{BROWN}; font-family:Georgia,serif;"
                            )
                            ui.label(f"{r['cuisine']} · {r['type']} · {r['cook_time']} min").style(
                                f"font-size:0.8rem; color:{GRAY};"
                            )
                            def do_remove(rid=r["recipe_id"]):
                                db.remove_saved_recipe(current_user["id"], rid)
                                ui.navigate.to("/saved")
                            ui.button("Remove", on_click=do_remove).props("flat dense").style(
                                f"color:{RUST}; font-size:0.8rem;"
                            )

            ui.label("Recipe Shopping List").style(
                f"font-size:1.2rem; font-weight:700; color:{BROWN}; "
                "font-family:Georgia,serif; margin-top:12px;"
            )
            if shopping:
                _shopping_list_card(shopping)
        else:
            ui.label("No saved recipes yet — browse and save some!").style(
                f"color:{GRAY}; font-style:italic;"
            )


def _render_saved_drinks(tab, saved_drinks, drink_shopping):
    with ui.tab_panel(tab):
        if saved_drinks:
            with ui.row().style("flex-wrap:wrap; gap:16px;"):
                for d in saved_drinks:
                    with ui.card().style(
                        f"background:{WHITE}; border-radius:12px; width:260px; "
                        "box-shadow:0 2px 8px rgba(0,0,0,.1);"
                    ):
                        with ui.column().style("padding:16px; gap:6px;"):
                            ui.label(d["drink_name"]).style(
                                f"font-weight:700; color:{BROWN}; font-family:Georgia,serif;"
                            )
                            stars = star_display(float(d.get("avg_rating") or 0))
                            ui.label(f"{stars}  ({d.get('rating_count', 0)} ratings)").style(
                                f"font-size:0.8rem; color:{GOLD};"
                            )
                            def do_remove_drink(did=d["drink_id"]):
                                db.remove_saved_drink(current_user["id"], did)
                                ui.navigate.to("/saved")
                            ui.button("Remove", on_click=do_remove_drink).props("flat dense").style(
                                f"color:{RUST}; font-size:0.8rem;"
                            )

            ui.label("Drinks Shopping List").style(
                f"font-size:1.2rem; font-weight:700; color:{BROWN}; "
                "font-family:Georgia,serif; margin-top:12px;"
            )
            if drink_shopping:
                _shopping_list_card(drink_shopping)
        else:
            ui.label("No saved drinks yet — browse and save some!").style(
                f"color:{GRAY}; font-style:italic;"
            )


def _shopping_list_card(items):
    total = sum(float(i.get("line_cost") or 0) for i in items)
    cols = [
        {"name": "ingredient", "label": "Ingredient", "field": "ingredient_name", "align": "left"},
        {"name": "qty",        "label": "Total Qty", "field": "qty"},
        {"name": "unit",       "label": "Unit",      "field": "unit"},
        {"name": "cost",       "label": "Est. Cost", "field": "cost"},
    ]
    rows = [
        {
            "ingredient_name": i["ingredient_name"],
            "qty":  str(i["total_quantity"]),
            "unit": i["unit"],
            "cost": f"${float(i['line_cost']):.2f}" if i["line_cost"] else "—",
        }
        for i in items
    ]
    with ui.card().style(
        f"background:{WHITE}; border-radius:12px; "
        "box-shadow:0 2px 8px rgba(0,0,0,.08); overflow:hidden;"
    ):
        ui.table(columns=cols, rows=rows).style("font-size:0.9rem;")
        ui.label(f"Estimated Total: ${total:.2f}").style(
            f"color:{SAGE}; font-weight:700; padding:12px 16px; "
            f"background:{CREAM}; text-align:right;"
        )
