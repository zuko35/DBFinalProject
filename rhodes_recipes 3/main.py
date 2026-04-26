from nicegui import ui

ui.add_head_html(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Playfair+Display:ital,wght@0,500;0,700;0,800;1,500&'
    'family=Cormorant+Garamond:wght@400;500;600;700&'
    'display=swap" rel="stylesheet">'
    '<style>'
    'body{font-family:"Cormorant Garamond","Georgia",serif;}'
    '.brand-title{font-family:"Playfair Display","Georgia",serif;'
    'letter-spacing:1.5px;font-weight:800;}'
    '</style>',
    shared=True,
)

import home_page
import saved_page
import login_page


if __name__ in {"__main__", "__mp_main__"}:
    print("Starting Rhodes Recipes  ->  http://localhost:8080")
    ui.run(title="Rhodes Recipes", port=8080)
