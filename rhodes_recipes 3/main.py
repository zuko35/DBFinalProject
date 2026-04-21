import time

from nicegui import ui, app
import database as db

# ── App state ─────────────────────────────────────────────────────────────────
current_user = {"id": None, "name": None}

# ── Color palette ─────────────────────────────────────────────────────────────
CREAM   = "#FDF6EC"
RUST    = "#C0522B"
RUST_LT = "#E8703A"
BROWN   = "#4A2C17"
SAGE    = "#7A9E7E"
GOLD    = "#D4A843"
WHITE   = "#FFFFFF"
GRAY    = "#6B6B6B"

# ─────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ─────────────────────────────────────────────────────────────────────────────

def header(title_text: str):
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
                ui.button("My Saved", on_click=show_saved_page).props(
                    "flat dense"
                ).style(f"color:{CREAM};")
                ui.button("Logout", on_click=do_logout).props(
                    "flat dense"
                ).style(f"color:{CREAM};")
            else:
                ui.button("Login / Register", on_click=show_login_page).props(
                    "flat dense"
                ).style(f"color:{CREAM};")


def star_display(rating: float):
    full  = int(rating)
    empty = 5 - full
    return "★" * full + "☆" * empty


def recipe_card(recipe: dict, on_click_fn):
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
        strip_color = type_colors.get(recipe.get("type",""), RUST)
        ui.element("div").style(
            f"background:{strip_color}; height:8px; width:100%;"
        )
        with ui.column().style("padding:16px; gap:6px;"):
            ui.label(recipe["recipe_name"]).style(
                f"font-size:1.05rem; font-weight:700; color:{BROWN}; "
                "font-family:'Georgia',serif;"
            )
            ui.label(recipe.get("description","")[:80] + "…").style(
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


# ─────────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────────

@ui.page("/")
def show_home():
    ui.query("body").style(f"background:{CREAM}; margin:0;")
    header("Browse Recipes")

    with ui.column().style("padding:24px 32px; gap:20px; max-width:1200px; margin:auto;"):

        # ── Filter bar ───────────────────────────────────────────────────────
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

                sel_cuisine  = ui.select(cuisines,   value="All",  label="Cuisine").style("min-width:140px;")
                sel_type     = ui.select(meal_types, value="All",  label="Meal Type").style("min-width:140px;")
                sel_allergen = ui.select(allergens,  value="None", label="Exclude Allergen").style("min-width:160px;")
                inp_ingredient = ui.input(placeholder="e.g. potatoes", label="Key Ingredient").style("min-width:160px;")
                inp_time     = ui.number(label="Max Cook Time (min)", min=1, max=300, step=5).style("min-width:160px;")

                results_row  = ui.row().style("flex-wrap:wrap; gap:16px; margin-top:4px;")

                def run_search():
                    results_row.clear()
                    recipes = db.search_recipes(
                        cuisine         = sel_cuisine.value,
                        meal_type       = sel_type.value,
                        max_cook_time   = inp_time.value,
                        allergen_exclude= sel_allergen.value,
                        ingredient      = inp_ingredient.value or None,
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

        # ── Initial results ──────────────────────────────────────────────────
        ui.label("All Recipes").style(
            f"font-size:1.3rem; font-weight:700; color:{BROWN}; "
            "font-family:'Georgia',serif;"
        )
        with ui.row().style("flex-wrap:wrap; gap:16px;") as initial_row:
            for r in db.search_recipes():
                recipe_card(r, open_recipe_dialog)


def open_recipe_dialog(recipe_id: int):
    recipe, ingredients, drinks = db.get_recipe_detail(recipe_id)
    if not recipe:
        return

    with ui.dialog() as dlg, ui.card().style(
        f"min-width:520px; max-width:700px; background:{CREAM}; "
        "border-radius:16px; overflow:scroll; padding:0;"
    ):
        # Header strip
        ui.element("div").style(
            f"background:{RUST}; padding:20px 24px;"
        ).add_slot("default", f"""
            <span style="color:{CREAM}; font-size:1.4rem; font-weight:800;
            font-family:Georgia,serif;">{recipe['recipe_name']}</span><br>
            <span style="color:rgba(255,255,255,.75); font-size:0.85rem;">
            {recipe['cuisine']} · {recipe['type']} · ⏱ {recipe['cook_time']} min</span>
        """)

        with ui.column().style("padding:20px 24px; gap:14px;"):
            # Rating
            avg = float(recipe.get("avg_rating") or 0)
            ui.label(f"{star_display(avg)}  ({recipe.get('rating_count',0)} ratings)").style(
                f"color:{GOLD}; font-size:1.1rem;"
            )

            # Description
            ui.label(recipe["description"]).style(
                f"color:{BROWN}; font-size:0.95rem; line-height:1.6;"
            )

            # Ingredients table
            ui.label("Ingredients").style(
                f"font-weight:700; color:{BROWN}; font-family:Georgia,serif;"
            )
            with ui.element("div").style(
                f"background:{WHITE}; border-radius:8px; overflow:hidden; "
                "box-shadow:0 1px 4px rgba(0,0,0,.08);"
            ):
                cols = [
                    {"name":"ingredient","label":"Ingredient","field":"ingredient_name","align":"left"},
                    {"name":"qty",       "label":"Qty",        "field":"qty"},
                    {"name":"unit",      "label":"Unit",       "field":"unit"},
                    {"name":"cost",      "label":"Cost/Unit",  "field":"cost"},
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

            # Recommended drinks — clickable to see drink detail
            if drinks:
                with ui.row().style("align-items:center; gap:8px; flex-wrap:wrap;"):
                    ui.label("🍷 Pairs well with:").style(
                        f"color:{SAGE}; font-weight:600; font-size:0.9rem;"
                    )
                    for d in drinks:
                        ui.button(d["drink_name"],
                                  on_click=lambda did=d["drink_id"]: open_drink_dialog(did)
                                  ).props("flat dense").style(
                            f"color:{RUST}; font-weight:600; font-size:0.9rem; "
                            "text-decoration:underline; padding:0;"
                        )

            # Cost info
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

            # Action buttons
            with ui.row().style("gap:10px; margin-top:8px; flex-wrap:wrap;"):
                if current_user["id"]:
                    def do_save(rid=recipe_id):
                        db.save_recipe(current_user["id"], rid)
                        ui.notify("Recipe saved to your list! 🎉", color="positive")

                    ui.button("💾 Save Recipe", on_click=do_save).style(
                        f"background:{SAGE}; color:{WHITE}; font-weight:600; border-radius:8px;"
                    )

                    # Star rating
                    rating_val = {"v": 3}
                    ui.label("Rate:").style(f"color:{BROWN}; align-self:center; font-size:0.9rem;")
                    sel_rating = ui.select([1,2,3,4,5], value=3).style("width:80px;")

                    def do_rate(rid=recipe_id):
                        db.rate_recipe(current_user["id"], rid, sel_rating.value)
                        ui.notify("Rating submitted! ⭐", color="positive")

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
        f"min-width:400px; max-width:500px; background:{CREAM}; border-radius:16px; overflow:hidden; padding:0;"
    ):
        with ui.column().style("padding:20px 24px; gap:12px;"):
            ui.label(drink["drink_name"]).style(
                f"font-size:1.3rem; font-weight:800; color:{BROWN}; font-family:Georgia,serif;"
            )
            ui.label(f"⭐ {drink['avg_rating']} / 5  ({drink['rating_count']} ratings)").style(
                f"color:{SAGE}; font-weight:600;"
            )
            if ingredients:
                ui.label("Ingredients").style(f"font-weight:700; color:{BROWN};")
                cols = [{"name":"name","label":"Ingredient","field":"name","align":"left"},{"name":"qty","label":"Qty","field":"qty"},{"name":"unit","label":"Unit","field":"unit"}]
                rows = [{"name":i["ingredient_name"],"qty":str(i["quantity"]),"unit":i["unit"]} for i in ingredients]
                ui.table(columns=cols, rows=rows).style("font-size:0.85rem;")
            if current_user["id"]:
                with ui.row().style("gap:10px; align-items:center; margin-top:4px;"):
                    ui.label("Rate:").style(f"color:{BROWN}; font-size:0.9rem;")
                    sel = ui.select([1,2,3,4,5], value=3).style("width:80px;")
                    def do_rate_drink(did=drink_id):
                        db.rate_drink(current_user["id"], did, sel.value)
                        ui.notify("Drink rated! 🥤", color="positive")
                    ui.button("Submit", on_click=do_rate_drink).style(f"background:{GOLD}; color:{BROWN}; font-weight:600; border-radius:8px;")
            ui.button("Close", on_click=dlg.close).props("flat").style(f"color:{RUST}; font-weight:600;")
    dlg.open()

@ui.page("/saved")
def show_saved_page():
    if not current_user["id"]:
        ui.navigate.to("/login")
        return

    ui.query("body").style(f"background:{CREAM}; margin:0;")
    header("My Saved Recipes")

    with ui.column().style("padding:24px 32px; gap:20px; max-width:1200px; margin:auto;"):

        saved = db.get_saved_recipes(current_user["id"])
        shopping = db.get_shopping_list(current_user["id"])

        with ui.row().style("align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;"):
            ui.label(f"You have {len(saved)} saved recipe(s)").style(
                f"font-size:1.3rem; font-weight:700; color:{BROWN}; font-family:Georgia,serif;"
            )
            ui.button("🏠 Back to Browse", on_click=lambda: ui.navigate.to("/")).style(
                f"background:{RUST}; color:{WHITE}; border-radius:8px; font-weight:600;"
            )

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
                            ui.label(f"{r['cuisine']} · {r['type']} · ⏱ {r['cook_time']} min").style(
                                f"font-size:0.8rem; color:{GRAY};"
                            )
                            def do_remove(rid=r["recipe_id"]):
                                db.remove_saved_recipe(current_user["id"], rid)
                                ui.navigate.to("/saved")
                            ui.button("Remove", on_click=do_remove).props("flat dense").style(
                                f"color:{RUST}; font-size:0.8rem;"
                            )

            # Shopping list
            ui.label("🛒 Shopping List").style(
                f"font-size:1.2rem; font-weight:700; color:{BROWN}; "
                "font-family:Georgia,serif; margin-top:12px;"
            )
            if shopping:
                total = sum(float(i.get("line_cost") or 0) for i in shopping)
                cols = [
                    {"name":"ingredient","label":"Ingredient","field":"ingredient_name","align":"left"},
                    {"name":"qty",       "label":"Total Qty", "field":"qty"},
                    {"name":"unit",      "label":"Unit",      "field":"unit"},
                    {"name":"cost",      "label":"Est. Cost", "field":"cost"},
                ]
                rows = [
                    {
                        "ingredient_name": i["ingredient_name"],
                        "qty":  str(i["total_quantity"]),
                        "unit": i["unit"],
                        "cost": f"${float(i['line_cost']):.2f}" if i["line_cost"] else "—",
                    }
                    for i in shopping
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
        else:
            ui.label("No saved recipes yet — browse and save some!").style(
                f"color:{GRAY}; font-style:italic;"
            )


@ui.page("/login")
def show_login_page():
    ui.query("body").style(f"background:{CREAM}; margin:0;")
    header("Login / Register")

    with ui.column().style(
        "max-width:420px; margin:60px auto; padding:0 16px; gap:16px;"
    ):
        with ui.card().style(
            f"background:{WHITE}; border-radius:16px; padding:32px; "
            "box-shadow:0 4px 20px rgba(0,0,0,.12);"
        ):
            ui.label("Welcome Back 🍴").style(
                f"font-size:1.5rem; font-weight:800; color:{BROWN}; "
                "font-family:Georgia,serif; margin-bottom:8px;"
            )

            tab_login = {"active": True}
            tabs = ui.tabs().style(f"color:{RUST};")
            with tabs:
                tab_l = ui.tab("Login")
                tab_r = ui.tab("Register")

            with ui.tab_panels(tabs, value=tab_l).style("width:100%;"):
                with ui.tab_panel(tab_l):
                    with ui.column().style("gap:12px; padding-top:8px;"):
                        inp_email = ui.input("Email", placeholder="you@example.com").style("width:100%;")
                        inp_pw    = ui.input("Password", password=True).style("width:100%;")
                        lbl_err   = ui.label("").style(f"color:{RUST}; font-size:0.85rem;")

                        def do_login():
                            user = db.login_user(inp_email.value, inp_pw.value)
                            if user:
                                current_user["id"]   = user["user_id"]
                                current_user["name"] = user["user_name"]
                                ui.navigate.to("/")
                            else:
                                lbl_err.set_text("Invalid email or password.")

                        ui.button("Login", on_click=do_login).style(
                            f"background:{RUST}; color:{WHITE}; font-weight:700; "
                            "border-radius:8px; width:100%; margin-top:4px;"
                        )

                with ui.tab_panel(tab_r):
                    with ui.column().style("gap:12px; padding-top:8px;"):
                        inp_name  = ui.input("Username").style("width:100%;")
                        inp_remail= ui.input("Email").style("width:100%;")
                        inp_rpw   = ui.input("Password", password=True).style("width:100%;")
                        lbl_rerr  = ui.label("").style(f"color:{RUST}; font-size:0.85rem;")
                        timestamp = int(time.time())
                        inp_rid = f"ID-{timestamp}"

                        def do_register():
                            uid, err = db.register_user(
                                inp_rid, inp_name.value, inp_remail.value, inp_rpw.value
                            )
                            if uid:
                                current_user["id"]   = uid
                                current_user["name"] = inp_name.value
                                ui.navigate.to("/")
                            else:
                                lbl_rerr.set_text(err or "Registration failed.")

                        ui.button("Register", on_click=do_register).style(
                            f"background:{SAGE}; color:{WHITE}; font-weight:700; "
                            "border-radius:8px; width:100%; margin-top:4px;"
                        )

        ui.button("← Back to Browse", on_click=lambda: ui.navigate.to("/")).props(
            "flat"
        ).style(f"color:{RUST}; align-self:center;")


def do_logout():
    current_user["id"]   = None
    current_user["name"] = None
    ui.navigate.to("/")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ in {"__main__", "__mp_main__"}:
    print("Starting Rhodes Recipes 🍴  →  http://localhost:8080")
    ui.run(title="Rhodes Recipes", port=8080, favicon="🍴")
