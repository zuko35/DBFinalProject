import re

from nicegui import ui

import database as db
from theme import BROWN, CREAM, GOLD, GRAY, RUST, SAGE, WHITE
from state import current_user
from widgets import star_display


def _parse_instructions(text: str):
    if not text:
        return []
    pieces = re.split(r"\.\s+(?=\d+\.\s)", text.strip())
    steps = []
    for p in pieces:
        p = p.strip()
        p = re.sub(r"^\d+\.\s*", "", p)
        p = p.rstrip(".")
        if p:
            steps.append(p)
    return steps


def open_recipe_dialog(recipe_id: int):
    recipe, ingredients, drinks = db.get_recipe_detail(recipe_id)
    if not recipe:
        return

    with ui.dialog() as dlg, ui.card().style(
        f"min-width:520px; max-width:700px; background:{CREAM}; "
        "border-radius:16px; overflow:scroll; padding:0;"
    ):
        ui.element("div").style(
            f"background:{RUST}; padding:20px 24px;"
        ).add_slot("default", f"""
            <span style="color:{CREAM}; font-size:1.4rem; font-weight:800;
            font-family:'Playfair Display','Georgia',serif;">{recipe['recipe_name']}</span><br>
            <span style="color:rgba(255,255,255,.75); font-size:0.85rem;">
            {recipe['cuisine']} · {recipe['type']} · {recipe['cook_time']} min</span>
        """)

        with ui.column().style("padding:20px 24px; gap:14px;"):
            avg = float(recipe.get("avg_rating") or 0)
            ui.label(f"{star_display(avg)}  ({recipe.get('rating_count',0)} ratings)").style(
                f"color:{GOLD}; font-size:1.1rem;"
            )

            ui.label(recipe["description"]).style(
                f"color:{BROWN}; font-size:0.95rem; line-height:1.6;"
            )

            ui.label("Ingredients").style(
                f"font-weight:700; color:{BROWN}; font-family:'Playfair Display','Georgia',serif;"
            )
            with ui.element("div").style(
                f"background:{WHITE}; border-radius:8px; overflow:hidden; "
                "box-shadow:0 1px 4px rgba(0,0,0,.08);"
            ):
                cols = [
                    {"name": "ingredient", "label": "Ingredient", "field": "ingredient_name", "align": "left"},
                    {"name": "qty",        "label": "Qty",        "field": "qty"},
                    {"name": "unit",       "label": "Unit",       "field": "unit"},
                    {"name": "cost",       "label": "Cost/Unit",  "field": "cost"},
                ]
                rows = [
                    {
                        "ingredient_name": i["ingredient_name"],
                        "qty":  str(i["quantity"]),
                        "unit": i["unit"],
                        "cost": f"${float(i['cost_per_unit']):.2f}" if i["cost_per_unit"] else "—",
                    }
                    for i in ingredients
                ]
                ui.table(columns=cols, rows=rows).style("font-size:0.85rem;")

            steps = _parse_instructions(recipe.get("instructions") or "")
            if steps:
                ui.label("Instructions").style(
                    f"font-weight:700; color:{BROWN}; font-family:'Playfair Display','Georgia',serif; margin-top:4px;"
                )
                with ui.element("div").style(
                    f"background:{WHITE}; border-radius:8px; padding:14px 18px; "
                    "box-shadow:0 1px 4px rgba(0,0,0,.08);"
                ):
                    for idx, step in enumerate(steps, start=1):
                        with ui.row().style(
                            "gap:10px; align-items:flex-start; margin-bottom:8px; flex-wrap:nowrap;"
                        ):
                            ui.label(f"{idx}.").style(
                                f"color:{RUST}; font-weight:700; min-width:22px; "
                                "font-family:'Playfair Display','Georgia',serif;"
                            )
                            ui.label(step).style(
                                f"color:{BROWN}; font-size:0.9rem; line-height:1.5;"
                            )

            if drinks:
                with ui.row().style("align-items:center; gap:8px; flex-wrap:wrap;"):
                    ui.label("Pairs well with:").style(
                        f"color:{SAGE}; font-weight:600; font-size:0.9rem;"
                    )
                    for d in drinks:
                        ui.button(
                            d["drink_name"],
                            on_click=lambda did=d["drink_id"]: open_drink_dialog(did),
                        ).props("flat dense").style(
                            f"color:{RUST}; font-weight:600; font-size:0.9rem; "
                            "text-decoration:underline; padding:0;"
                        )

            with ui.row().style("gap:24px; flex-wrap:wrap;"):
                ui.label(f"Total cost: ${float(recipe['cost']):.2f}").style(
                    f"color:{GRAY}; font-size:0.85rem;"
                )
                ui.label(f"Servings: {recipe['servings']}").style(
                    f"color:{GRAY}; font-size:0.85rem;"
                )
                ui.label(f"Cost/serving: ${float(recipe['cost_per_serving']):.2f}").style(
                    f"color:{SAGE}; font-weight:600; font-size:0.85rem;"
                )

            with ui.row().style("gap:10px; margin-top:8px; flex-wrap:wrap;"):
                if current_user["id"]:
                    def do_save(rid=recipe_id):
                        db.save_recipe(current_user["id"], rid)
                        ui.notify("Recipe saved to your list!", color="positive")

                    ui.button("Save Recipe", on_click=do_save).style(
                        f"background:{SAGE}; color:{WHITE}; font-weight:600; border-radius:8px;"
                    )

                    ui.label("Rate:").style(f"color:{BROWN}; align-self:center; font-size:0.9rem;")
                    sel_rating = ui.select([1, 2, 3, 4, 5], value=3).style("width:80px;")

                    def do_rate(rid=recipe_id):
                        db.rate_recipe(current_user["id"], rid, sel_rating.value)
                        ui.notify("Rating submitted!", color="positive")

                    ui.button("Submit Rating", on_click=do_rate).style(
                        f"background:{GOLD}; color:{BROWN}; font-weight:600; border-radius:8px;"
                    )
                else:
                    ui.label("Log in to save or rate recipes.").style(
                        f"color:{GRAY}; font-size:0.85rem; font-style:italic;"
                    )

                ui.button("Close", on_click=dlg.close).props("flat").style(
                    f"color:{RUST}; font-weight:600;"
                )

    dlg.open()


def open_drink_dialog(drink_id: int):
    drink, ingredients = db.get_drink_detail(drink_id)
    if not drink:
        return
    with ui.dialog() as dlg, ui.card().style(
        f"min-width:520px; max-width:700px; background:{CREAM}; "
        "border-radius:16px; overflow:scroll; padding:0;"
    ):
        ui.element("div").style(
            f"background:{SAGE}; padding:20px 24px;"
        ).add_slot("default", f"""
            <span style="color:{CREAM}; font-size:1.4rem; font-weight:800;
            font-family:'Playfair Display','Georgia',serif;">{drink['drink_name']}</span><br>
            <span style="color:rgba(255,255,255,.85); font-size:0.85rem;">
            Beverage</span>
        """)

        with ui.column().style("padding:20px 24px; gap:14px;"):
            avg = float(drink.get("avg_rating") or 0)
            ui.label(f"{star_display(avg)}  ({drink.get('rating_count', 0)} ratings)").style(
                f"color:{GOLD}; font-size:1.1rem;"
            )

            ui.label("Ingredients").style(
                f"font-weight:700; color:{BROWN}; font-family:'Playfair Display','Georgia',serif;"
            )
            with ui.element("div").style(
                f"background:{WHITE}; border-radius:8px; overflow:hidden; "
                "box-shadow:0 1px 4px rgba(0,0,0,.08);"
            ):
                cols = [
                    {"name": "ingredient", "label": "Ingredient", "field": "ingredient_name", "align": "left"},
                    {"name": "qty",        "label": "Qty",        "field": "qty"},
                    {"name": "unit",       "label": "Unit",       "field": "unit"},
                    {"name": "cost",       "label": "Cost/Unit",  "field": "cost"},
                    {"name": "allergen",   "label": "Allergen",   "field": "allergen"},
                ]
                rows = [
                    {
                        "ingredient_name": i["ingredient_name"],
                        "qty":  str(i["quantity"]),
                        "unit": i["unit"],
                        "cost": f"${float(i['cost_per_unit']):.2f}" if i.get("cost_per_unit") else "—",
                        "allergen": i.get("allergen_name") or "—",
                    }
                    for i in ingredients
                ]
                ui.table(columns=cols, rows=rows).style("font-size:0.85rem;")

            total_cost = sum(
                float(i["quantity"]) * float(i["cost_per_unit"] or 0)
                for i in ingredients
            )
            if total_cost > 0:
                ui.label(f"Estimated cost: ${total_cost:.2f}").style(
                    f"color:{SAGE}; font-weight:600; font-size:0.85rem;"
                )

            with ui.row().style("gap:10px; margin-top:8px; flex-wrap:wrap;"):
                if current_user["id"]:
                    def do_save_drink(did=drink_id):
                        db.save_drink(current_user["id"], did)
                        ui.notify("Drink saved to your list!", color="positive")

                    ui.button("Save Drink", on_click=do_save_drink).style(
                        f"background:{SAGE}; color:{WHITE}; font-weight:600; border-radius:8px;"
                    )

                    ui.label("Rate:").style(f"color:{BROWN}; align-self:center; font-size:0.9rem;")
                    sel_drink_rating = ui.select([1, 2, 3, 4, 5], value=3).style("width:80px;")

                    def do_rate_drink(did=drink_id):
                        db.rate_drink(current_user["id"], did, sel_drink_rating.value)
                        ui.notify("Rating submitted!", color="positive")

                    ui.button("Submit Rating", on_click=do_rate_drink).style(
                        f"background:{GOLD}; color:{BROWN}; font-weight:600; border-radius:8px;"
                    )
                else:
                    ui.label("Log in to save or rate drinks.").style(
                        f"color:{GRAY}; font-size:0.85rem; font-style:italic;"
                    )

                ui.button("Close", on_click=dlg.close).props("flat").style(
                    f"color:{RUST}; font-weight:600;"
                )

    dlg.open()
