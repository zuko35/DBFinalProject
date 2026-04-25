"""Reusable UI components: header bar, star display, and item cards."""
from nicegui import ui

from theme import BROWN, CREAM, GOLD, GRAY, RUST, SAGE, WHITE
from state import current_user, do_logout


def header(title_text: str):
    """Top app bar with brand, page title, and auth-aware action buttons."""
    with ui.element("div").style(
        f"background:{BROWN}; padding:16px 32px; display:flex; "
        "align-items:center; justify-content:space-between; "
        "box-shadow:0 2px 8px rgba(0,0,0,.3);"
    ):
        ui.label("🍴 Rhodes Recipes").style(
            f"color:{GOLD}; font-size:1.6rem; font-weight:800; "
            "font-family:'Georgia',serif; letter-spacing:1px;"
        )
        ui.label(title_text).style(
            f"color:{CREAM}; font-size:1.1rem; font-family:'Georgia',serif;"
        )
        with ui.row().style("gap:8px;"):
            if current_user["id"]:
                ui.label(f"👤 {current_user['name']}").style(
                    f"color:{GOLD}; font-size:0.9rem; align-self:center;"
                )
                ui.button("My Saved", on_click=lambda: ui.navigate.to("/saved")).props(
                    "flat dense"
                ).style(f"color:{CREAM};")
                ui.button("Logout", on_click=do_logout).props(
                    "flat dense"
                ).style(f"color:{CREAM};")
            else:
                ui.button("Login / Register", on_click=lambda: ui.navigate.to("/login")).props(
                    "flat dense"
                ).style(f"color:{CREAM};")


def star_display(rating: float) -> str:
    """Render a 0-5 numeric rating as ★/☆ characters."""
    full = int(rating)
    empty = 5 - full
    return "★" * full + "☆" * empty


def recipe_card(recipe: dict, on_click_fn):
    """Compact recipe card used in browse and search results."""
    stars = star_display(float(recipe.get("avg_rating") or 0))
    with ui.card().style(
        f"background:{WHITE}; border-radius:12px; width:280px; cursor:pointer; "
        "box-shadow:0 2px 10px rgba(0,0,0,.12); transition:transform .15s,box-shadow .15s; "
        "overflow:hidden; flex-shrink:0;"
    ).on("click", lambda r=recipe: on_click_fn(r["recipe_id"])):
        # Coloured top strip by meal type
        type_colors = {
            "Breakfast": "#F4A261", "Lunch": SAGE,
            "Dinner": RUST,        "Dessert": "#C77DFF",
        }
        strip_color = type_colors.get(recipe.get("type", ""), RUST)
        ui.element("div").style(f"background:{strip_color}; height:8px; width:100%;")
        with ui.column().style("padding:16px; gap:6px;"):
            ui.label(recipe["recipe_name"]).style(
                f"font-size:1.05rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif;"
            )
            ui.label(recipe.get("description", "")[:80] + "…").style(
                f"font-size:0.82rem; color:{GRAY}; line-height:1.4;"
            )
            with ui.row().style("justify-content:space-between; margin-top:4px;"):
                ui.label(f"🍽 {recipe.get('type','')}  ·  {recipe.get('cuisine','')}").style(
                    f"font-size:0.78rem; color:{GRAY};"
                )
                ui.label(f"⏱ {recipe.get('cook_time','')} min").style(
                    f"font-size:0.78rem; color:{GRAY};"
                )
            with ui.row().style("justify-content:space-between; margin-top:2px;"):
                ui.label(stars).style(f"color:{GOLD}; font-size:1rem;")
                ui.label(f"${float(recipe.get('cost_per_serving') or 0):.2f}/serving").style(
                    f"font-size:0.78rem; color:{SAGE}; font-weight:600;"
                )


def drink_card(drink: dict, on_click_fn):
    """Compact drink card used in browse and search results."""
    stars = star_display(float(drink.get("avg_rating") or 0))
    with ui.card().style(
        f"background:{WHITE}; border-radius:12px; width:280px; cursor:pointer; "
        "box-shadow:0 2px 10px rgba(0,0,0,.12); transition:transform .15s,box-shadow .15s; "
        "overflow:hidden; flex-shrink:0;"
    ).on("click", lambda d=drink: on_click_fn(d["drink_id"])):
        ui.element("div").style(f"background:{SAGE}; height:8px; width:100%;")
        with ui.column().style("padding:16px; gap:6px;"):
            ui.label(drink["drink_name"]).style(
                f"font-size:1.05rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif;"
            )
            ui.label("🥤 Beverage").style(
                f"font-size:0.82rem; color:{GRAY}; line-height:1.4;"
            )
            with ui.row().style("justify-content:space-between; margin-top:6px;"):
                ui.label(stars).style(f"color:{GOLD}; font-size:1rem;")
                ui.label(f"{drink.get('rating_count', 0)} rating(s)").style(
                    f"font-size:0.78rem; color:{GRAY};"
                )
