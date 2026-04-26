import time

from nicegui import ui

import database as db
from theme import BROWN, CREAM, RUST, SAGE, WHITE
from state import current_user
from widgets import header


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
            ui.label("Welcome Back").style(
                f"font-size:1.5rem; font-weight:800; color:{BROWN}; "
                "font-family:'Playfair Display','Georgia',serif; margin-bottom:8px;"
            )

            tabs = ui.tabs().style(f"color:{RUST};")
            with tabs:
                tab_l = ui.tab("Login")
                tab_r = ui.tab("Register")

            with ui.tab_panels(tabs, value=tab_l).style("width:100%;"):
                _render_login_panel(tab_l)
                _render_register_panel(tab_r)

        ui.button("Back to Browse", on_click=lambda: ui.navigate.to("/")).props(
            "flat"
        ).style(f"color:{RUST}; align-self:center;")


def _render_login_panel(tab):
    with ui.tab_panel(tab):
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


def _render_register_panel(tab):
    with ui.tab_panel(tab):
        with ui.column().style("gap:12px; padding-top:8px;"):
            inp_name   = ui.input("Username").style("width:100%;")
            inp_remail = ui.input("Email").style("width:100%;")
            inp_rpw    = ui.input("Password", password=True).style("width:100%;")
            lbl_rerr   = ui.label("").style(f"color:{RUST}; font-size:0.85rem;")
            inp_rid    = f"ID-{int(time.time())}"

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
