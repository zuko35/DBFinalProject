from nicegui import ui

from theme import BROWN, CREAM, GOLD, GRAY, RUST, SAGE, WHITE
from state import current_user, do_logout


SHIELD_SVG = (
    '<svg width="38" height="46" viewBox="0 0 100 120" '
    'xmlns="http://www.w3.org/2000/svg" style="display:block;">'
    '<path d="M5 5 L95 5 L95 70 Q95 105 50 115 Q5 105 5 70 Z" '
    'fill="#FAF6EE" stroke="#1A1A1A" stroke-width="4"/>'
    '<path d="M14 14 L86 96" stroke="#9E1B32" stroke-width="14" stroke-linecap="square"/>'
    '<path d="M86 14 L14 96" stroke="#9E1B32" stroke-width="14" stroke-linecap="square"/>'
    '<circle cx="50" cy="55" r="9" fill="#FAF6EE" stroke="#1A1A1A" stroke-width="2"/>'
    '</svg>'
)


def header(title_text: str):
    with ui.element("div").style(
        f"background:{BROWN}; padding:14px 32px; display:flex; "
        "align-items:center; justify-content:space-between; "
        f"border-bottom:4px solid {RUST}; "
        "box-shadow:0 2px 12px rgba(0,0,0,.35);"
    ):
        with ui.row().style("align-items:center; gap:14px;"):
            ui.html(SHIELD_SVG)
            with ui.column().style("gap:0;"):
                ui.label("Rhodes Recipes").style(
                    f"color:{CREAM}; font-size:1.65rem; line-height:1.1; "
                    "font-family:'Georgia',serif; font-weight:800; letter-spacing:1.5px;"
                )
                ui.label("Est. 1848").style(
                    f"color:{GOLD}; font-size:0.7rem; letter-spacing:3px; "
                    "font-family:'Georgia',serif; text-transform:uppercase;"
                )
        ui.label(title_text).style(
            f"color:{CREAM}; font-size:1.05rem; font-style:italic; "
            "font-family:'Georgia',serif; opacity:0.85;"
        )
        with ui.row().style("gap:8px;"):
            if current_user["id"]:
                ui.label(f"{current_user['name']}").style(
                    f"color:{GOLD}; font-size:0.95rem; align-self:center; "
                    "font-family:'Georgia',serif;"
                )
                ui.button("My Saved", on_click=lambda: ui.navigate.to("/saved")).props(
                    "flat dense"
                ).style(f"color:{CREAM}; letter-spacing:1px;")
                ui.button("Logout", on_click=do_logout).props(
                    "flat dense"
                ).style(f"color:{CREAM}; letter-spacing:1px;")
            else:
                ui.button("Login / Register", on_click=lambda: ui.navigate.to("/login")).props(
                    "flat dense"
                ).style(f"color:{CREAM}; letter-spacing:1px;")


def star_display(rating: float) -> str:
    full = int(rating)
    empty = 5 - full
    return "★" * full + "☆" * empty


def recipe_card(recipe: dict, on_click_fn):
    stars = star_display(float(recipe.get("avg_rating") or 0))
    with ui.card().style(
        f"background:{WHITE}; border-radius:6px; width:280px; cursor:pointer; "
        f"border:1px solid #E5DFD3; "
        "box-shadow:0 2px 10px rgba(0,0,0,.08); transition:transform .15s,box-shadow .15s; "
        "overflow:hidden; flex-shrink:0;"
    ).on("click", lambda r=recipe: on_click_fn(r["recipe_id"])):
        type_colors = {
            "Breakfast": GOLD,
            "Lunch": SAGE,
            "Dinner": RUST,
            "Dessert": "#7C1426",
        }
        strip_color = type_colors.get(recipe.get("type", ""), RUST)
        ui.element("div").style(f"background:{strip_color}; height:6px; width:100%;")
        with ui.column().style("padding:18px; gap:8px;"):
            ui.label(recipe["recipe_name"]).style(
                f"font-size:1.15rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif; line-height:1.25;"
            )
            ui.label(recipe.get("description", "")[:90] + "…").style(
                f"font-size:0.92rem; color:{GRAY}; line-height:1.45;"
            )
            with ui.row().style("justify-content:space-between; margin-top:6px;"):
                ui.label(f"{recipe.get('type','')}  ·  {recipe.get('cuisine','')}").style(
                    f"font-size:0.78rem; color:{GRAY}; letter-spacing:1px; "
                    "text-transform:uppercase;"
                )
                ui.label(f"{recipe.get('cook_time','')} min").style(
                    f"font-size:0.78rem; color:{GRAY}; letter-spacing:1px;"
                )
            with ui.row().style("justify-content:space-between; margin-top:2px; align-items:center;"):
                ui.label(stars).style(f"color:{GOLD}; font-size:1.05rem; letter-spacing:2px;")
                ui.label(f"${float(recipe.get('cost_per_serving') or 0):.2f}/serving").style(
                    f"font-size:0.82rem; color:{RUST}; font-weight:600;"
                )


def drink_card(drink: dict, on_click_fn):
    stars = star_display(float(drink.get("avg_rating") or 0))
    with ui.card().style(
        f"background:{WHITE}; border-radius:6px; width:280px; cursor:pointer; "
        f"border:1px solid #E5DFD3; "
        "box-shadow:0 2px 10px rgba(0,0,0,.08); transition:transform .15s,box-shadow .15s; "
        "overflow:hidden; flex-shrink:0;"
    ).on("click", lambda d=drink: on_click_fn(d["drink_id"])):
        ui.element("div").style(f"background:{SAGE}; height:6px; width:100%;")
        with ui.column().style("padding:18px; gap:8px;"):
            ui.label(drink["drink_name"]).style(
                f"font-size:1.15rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif; line-height:1.25;"
            )
            ui.label("Beverage").style(
                f"font-size:0.78rem; color:{GRAY}; letter-spacing:2px; "
                "text-transform:uppercase;"
            )
            with ui.row().style("justify-content:space-between; margin-top:8px; align-items:center;"):
                ui.label(stars).style(f"color:{GOLD}; font-size:1.05rem; letter-spacing:2px;")
                ui.label(f"{drink.get('rating_count', 0)} rating(s)").style(
                    f"font-size:0.82rem; color:{GRAY};"
                )
