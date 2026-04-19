# Rhodes Recipes 🍴
**COMP 340 Course Project — Mallory, Rachel, Avery, Jessie**

---

## Setup in PyCharm

### 1. Open the project
File → Open → select the `rhodes_recipes` folder.

### 2. Create a virtual environment
PyCharm will usually prompt you automatically. If not:
- Go to **Settings → Project → Python Interpreter → Add Interpreter → Virtualenv**

### 3. Install dependencies
Open the PyCharm Terminal (bottom bar) and run:
```
pip install -r requirements.txt
```

### 4. Create your PostgreSQL database
In pgAdmin or psql:
```sql
CREATE DATABASE rhodes_recipes;
```

### 5. Edit your DB credentials
Open `database.py` and update the `DB_CONFIG` block at the top:
```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "rhodes_recipes",
    "user":     "postgres",
    "password": "YOUR_PASSWORD_HERE",   # ← change this
}
```

### 6. Run the app
Right-click `main.py` → **Run 'main'**
Then open your browser to: **http://localhost:8080**

---

## Project structure
```
rhodes_recipes/
├── main.py        ← NiceGUI pages & UI components
├── database.py    ← All PostgreSQL queries (hand-written SQL)
├── requirements.txt
└── README.md
```

---

## Features
| Feature | How it works |
|---|---|
| Browse & filter recipes | Cuisine, meal type, allergen exclusion, key ingredient, max cook time |
| Recipe detail view | Ingredients table, instructions, recommended drinks, cost breakdown |
| Star ratings | Submit a 1–5 rating per recipe (stored in RecipeRatings) |
| Save recipes | Users save recipes to their personal list (UserSavedRecipes) |
| Shopping list | Auto-aggregates ingredients from all saved recipes |
| Login / Register | Simple user auth (email + password) |

---

## Database schema
See `database.py → create_tables()` for all DDL.
Tables: Users, Allergens, Ingredients, Recipes, RecipeIngredients,
Drinks, Recommended_Drinks, UserSavedRecipes, UserAllergies,
RecipeRatings, DrinkRatings
