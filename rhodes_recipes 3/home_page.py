"""Home page (`/`): browse Recipes and Drinks via tabs with filters."""
from nicegui import ui

import database as db
from theme import BROWN, CREAM, GRAY, RUST, WHITE
from widgets import header, recipe_card, drink_card
from dialogs import open_recipe_dialog, open_drink_dialog


@ui.page("/")
def show_home():
    ui.query("body").style(f"background:{CREAM}; margin:0;")
    header("Browse Recipes & Drinks")

    with ui.column().style("padding:24px 32px; gap:20px; max-width:1200px; margin:auto;"):

        # ── Tab toggle ───────────────────────────────────────────────────────
        tabs = ui.tabs().style(
            f"color:{RUST}; background:{WHITE}; border-radius:12px; "
            "box-shadow:0 2px 8px rgba(0,0,0,.08); padding:4px;"
        )
        with tabs:
            tab_recipes = ui.tab("🍴 Recipes")
            tab_drinks  = ui.tab("🥤 Drinks")

        with ui.tab_panels(tabs, value=tab_recipes).style("background:transparent; width:100%;"):
            _render_recipes_tab(tab_recipes)
            _render_drinks_tab(tab_drinks)


# ─────────────────────────────────────────────────────────────────────────────
# Tab content builders
# ─────────────────────────────────────────────────────────────────────────────

def _render_recipes_tab(tab):
    with ui.tab_panel(tab):
        with ui.card().style(
            f"background:{WHITE}; border-radius:12px; padding:20px; "
            "box-shadow:0 2px 8px rgba(0,0,0,.08);"
        ):
            ui.label("🔍 Filter Recipes").style(
                f"font-size:1.1rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif; margin-bottom:12px;"
            )
            with ui.row().style("flex-wrap:wrap; gap:16px; align-items:flex-end;"):
                cuisines   = ["All"] + db.get_cuisines()
                meal_types = ["All"] + db.get_meal_types()
                allergens  = ["None"] + db.get_allergens()

                sel_cuisine    = ui.select(cuisines,   value="All",  label="Cuisine").style("min-width:140px;")
                sel_type       = ui.select(meal_types, value="All",  label="Meal Type").style("min-width:140px;")
                sel_allergen   = ui.select(allergens,  value="None", label="Exclude Allergen").style("min-width:160px;")
                inp_ingredient = ui.input(placeholder="e.g. potatoes", label="Key Ingredient").style("min-width:160px;")
                inp_time       = ui.number(label="Max Cook Time (min)", min=1, max=300, step=5).style("min-width:160px;")

                results_row = ui.row().style("flex-wrap:wrap; gap:16px; margin-top:4px;")

                def run_search():
                    results_row.clear()
                    recipes = db.search_recipes(
                        cuisine          = sel_cuisine.value,
                        meal_type        = sel_type.value,
                        max_cook_time    = inp_time.value,
                        allergen_exclude = sel_allergen.value,
                        ingredient       = inp_ingredient.value or None,
                    )
                    with results_row:
                        if recipes:
                            for r in recipes:
                                recipe_card(r, open_recipe_dialog)
                        else:
                            ui.label("No recipes found — try adjusting your filters.").style(
                                f"color:{GRAY}; font-style:italic; padding:16px;"
                            )

                ui.button("Search", on_click=run_search).style(
                    f"background:{RUST}; color:{WHITE}; font-weight:600; "
                    "border-radius:8px; padding:8px 24px;"
                )

        ui.label("All Recipes").style(
            f"font-size:1.3rem; font-weight:700; color:{BROWN}; "
            "font-family:'Georgia',serif; margin-top:16px;"
        )
        with ui.row().style("flex-wrap:wrap; gap:16px;"):
            for r in db.search_recipes():
                recipe_card(r, open_recipe_dialog)


def _render_drinks_tab(tab):
    with ui.tab_panel(tab):
        with ui.card().style(
            f"background:{WHITE}; border-radius:12px; padding:20px; "
            "box-shadow:0 2px 8px rgba(0,0,0,.08);"
        ):
            ui.label("🔍 Filter Drinks").style(
                f"font-size:1.1rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif; margin-bottom:12px;"
            )
            with ui.row().style("flex-wrap:wrap; gap:16px; align-items:flex-end;"):
                d_allergens = ["None"] + db.get_allergens()

                d_inp_ingredient = ui.input(
                    placeholder="e.g. lemon", label="Key Ingredient"
                ).style("min-width:160px;")
                d_sel_allergen = ui.select(
                    d_allergens, value="None", label="Exclude Allergen"
                ).style("min-width:160px;")
                d_sel_min_rating = ui.select(
                    [0, 1, 2, 3, 4, 5], value=0, label="Min Avg Rating"
                ).style("min-width:140px;")

                d_results_row = ui.row().style("flex-wrap:wrap; gap:16px; margin-top:4px;")

                def run_drink_search():
                    d_results_row.clear()
                    drinks = db.search_drinks(
                        ingredient       = d_inp_ingredient.value or None,
                        allergen_exclude = d_sel_allergen.value,
                        min_rating       = d_sel_min_rating.value or None,
                    )
                    with d_results_row:
                        if drinks:
                            for d in drinks:
                                drink_card(d, open_drink_dialog)
                        else:
                            ui.label("No drinks found — try adjusting your filters.").style(
                                f"color:{GRAY}; font-style:italic; padding:16px;"
                            )

                ui.button("Search", on_click=run_drink_search).style(
                    f"background:{RUST}; color:{WHITE}; font-weight:600; "
                    "border-radius:8px; padding:8px 24px;"
                )

        ui.label("All Drinks").style(
            f"font-size:1.3rem; font-weight:700; color:{BROWN}; "
            "font-family:'Georgia',serif; margin-top:16px;"
        )
        with ui.row().style("flex-wrap:wrap; gap:16px;"):
            for d in db.search_drinks():
                drink_card(d, open_drink_dialog)
