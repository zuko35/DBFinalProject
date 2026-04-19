import psycopg
from dbinfo import DBUSER, DBPASS


def get_conn():
    return psycopg.connect(
        f"host=dbclass.rhodescs.org dbname=practice user={DBUSER} password={DBPASS}",
        row_factory=psycopg.rows.dict_row
    )


# ── Schema setup ─────────────────────────────────────────────────────────────

def create_tables():
    ddl = """
    CREATE TABLE IF NOT EXISTS Users (
        user_id   SERIAL PRIMARY KEY,
        user_name VARCHAR(255) NOT NULL,
        email     VARCHAR(255) NOT NULL UNIQUE,
        password  VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Allergens (
        allergen_id   SERIAL PRIMARY KEY,
        allergen_name VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Ingredients (
        ingredient_id   SERIAL PRIMARY KEY,
        ingredient_name VARCHAR(255) NOT NULL,
        allergy_id      INT REFERENCES Allergens(allergen_id),
        unit            VARCHAR(100) NOT NULL,
        cost_per_unit   FLOAT
    );

    CREATE TABLE IF NOT EXISTS Recipes (
        recipe_id       SERIAL PRIMARY KEY,
        recipe_name     VARCHAR(255) NOT NULL,
        description     TEXT NOT NULL,
        instructions    TEXT NOT NULL,
        cuisine         VARCHAR(255) NOT NULL,
        type            VARCHAR(255) NOT NULL,
        cook_time       VARCHAR(255) NOT NULL,
        unit            VARCHAR(255) NOT NULL,
        cost            FLOAT NOT NULL,
        servings        INT NOT NULL,
        cost_per_serving FLOAT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS RecipeIngredients (
        recipe_id     INT REFERENCES Recipes(recipe_id),
        ingredient_id INT REFERENCES Ingredients(ingredient_id),
        quantity      DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (recipe_id, ingredient_id)
    );

    CREATE TABLE IF NOT EXISTS Drinks (
        drink_id        SERIAL PRIMARY KEY,
        drink_name      VARCHAR(255) NOT NULL,
        ingredient_name VARCHAR(255)
    );

    CREATE TABLE IF NOT EXISTS Recommended_Drinks (
        recipe_id INT NOT NULL,
        drink_id  INT NOT NULL REFERENCES Drinks(drink_id),
        PRIMARY KEY (recipe_id, drink_id)
    );

    CREATE TABLE IF NOT EXISTS UserSavedRecipes (
        user_id   INT NOT NULL REFERENCES Users(user_id),
        recipe_id INT NOT NULL,
        PRIMARY KEY (user_id, recipe_id)
    );

    CREATE TABLE IF NOT EXISTS UserAllergies (
        user_id     INT NOT NULL REFERENCES Users(user_id),
        allergen_id INT NOT NULL,
        PRIMARY KEY (user_id, allergen_id)
    );

    CREATE TABLE IF NOT EXISTS RecipeRatings (
        user_id   INT,
        recipe_id INT,
        ratings   FLOAT,
        PRIMARY KEY (user_id, recipe_id)
    );

    CREATE TABLE IF NOT EXISTS DrinkRatings (
        user_id  INT,
        drink_id INT,
        ratings  FLOAT,
        PRIMARY KEY (user_id, drink_id)
    );
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()


def seed_sample_data():
    """Insert sample data so the UI has something to show on first run."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Allergens
            cur.execute("""
                INSERT INTO Allergens (allergen_name) VALUES
                ('Gluten'),('Dairy'),('Nuts'),('Eggs'),('Soy'),('Shellfish')
                ON CONFLICT DO NOTHING
            """)
            # Ingredients
            cur.execute("""
                INSERT INTO Ingredients (ingredient_name, allergy_id, unit, cost_per_unit) VALUES
                ('All-purpose flour', 1, 'cups', 0.50),
                ('Butter',           2, 'tbsp',  0.20),
                ('Eggs',             4, 'count', 0.30),
                ('Milk',             2, 'cups',  0.40),
                ('Potatoes',         NULL,'lbs',  0.80),
                ('Chicken breast',   NULL,'lbs',  3.50),
                ('Olive oil',        NULL,'tbsp',  0.15),
                ('Garlic',           NULL,'cloves',0.10),
                ('Pasta',            1,  'oz',    0.60),
                ('Cheddar cheese',   2,  'cups',  1.20)
                ON CONFLICT DO NOTHING
            """)
            # Recipes
            cur.execute("""
                INSERT INTO Recipes
                    (recipe_name, description, instructions, cuisine, type,
                     cook_time, unit, cost, servings, cost_per_serving) VALUES
                ('Classic Mashed Potatoes',
                 'Creamy, buttery mashed potatoes — the ultimate comfort side dish.',
                 '1. Boil potatoes until tender.\n2. Drain and mash.\n3. Add butter and milk.\n4. Season with salt and pepper.',
                 'American','Dinner','30','mins', 4.50, 4, 1.13),
                ('Garlic Chicken Pasta',
                 'Simple weeknight pasta with juicy chicken and aromatic garlic.',
                 '1. Cook pasta al dente.\n2. Sauté chicken in olive oil.\n3. Add garlic and toss with pasta.',
                 'Italian','Dinner','25','mins', 9.00, 2, 4.50),
                ('Fluffy Pancakes',
                 'Light and airy breakfast pancakes perfect with maple syrup.',
                 '1. Mix dry ingredients.\n2. Whisk in eggs and milk.\n3. Cook on griddle until golden.',
                 'American','Breakfast','20','mins', 3.00, 6, 0.50),
                ('Cheesy Potato Bake',
                 'Layered potatoes smothered in melted cheddar — pure indulgence.',
                 '1. Slice potatoes thin.\n2. Layer with cheese.\n3. Bake at 375°F for 45 min.',
                 'American','Dinner','60','mins', 7.00, 4, 1.75)
                ON CONFLICT DO NOTHING
            """)
            # RecipeIngredients links
            cur.execute("""
                INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity) VALUES
                (1,5,2.0),(1,2,4.0),(1,3,0.0),
                (2,6,1.0),(2,9,8.0),(2,7,2.0),(2,8,3.0),
                (3,1,2.0),(3,3,2.0),(3,4,1.0),
                (4,5,3.0),(4,10,2.0),(4,2,2.0)
                ON CONFLICT DO NOTHING
            """)
            # Drinks
            cur.execute("""
                INSERT INTO Drinks (drink_name, ingredient_name) VALUES
                ('Lemonade','Lemon'),
                ('Red Wine','Grapes'),
                ('Orange Juice','Oranges'),
                ('Sparkling Water',NULL)
                ON CONFLICT DO NOTHING
            """)
            # Recommended drinks
            cur.execute("""
                INSERT INTO Recommended_Drinks (recipe_id, drink_id) VALUES
                (1,4),(2,2),(3,3),(4,1)
                ON CONFLICT DO NOTHING
            """)
            # Sample user
            cur.execute("""
                INSERT INTO Users (user_name, email, password) VALUES
                ('demo_user','demo@rhodesrecipes.com','hashed_pw_here')
                ON CONFLICT DO NOTHING
            """)
        conn.commit()


# ── Query functions (all hand-written SQL) ───────────────────────────────────

def search_recipes(cuisine=None, meal_type=None, max_cook_time=None,
                   allergen_exclude=None, ingredient=None):
    """
    Filter recipes by cuisine, meal type, max cook time, excluded allergen,
    or a key ingredient. Returns list of recipe dicts.
    """
    sql = """
        SELECT DISTINCT r.recipe_id, r.recipe_name, r.description,
               r.cuisine, r.type, r.cook_time, r.cost_per_serving,
               COALESCE(AVG(rr.ratings), 0) AS avg_rating
        FROM Recipes r
        LEFT JOIN RecipeRatings rr ON r.recipe_id = rr.recipe_id
        LEFT JOIN RecipeIngredients ri ON r.recipe_id = ri.recipe_id
        LEFT JOIN Ingredients i       ON ri.ingredient_id = i.ingredient_id
        WHERE 1=1
    """
    params = []

    if cuisine and cuisine != "All":
        sql += " AND LOWER(r.cuisine) = LOWER(%s)"
        params.append(cuisine)

    if meal_type and meal_type != "All":
        sql += " AND LOWER(r.type) = LOWER(%s)"
        params.append(meal_type)

    if max_cook_time:
        sql += " AND CAST(r.cook_time AS INT) <= %s"
        params.append(max_cook_time)

    if allergen_exclude and allergen_exclude != "None":
        sql += """
            AND r.recipe_id NOT IN (
                SELECT ri2.recipe_id FROM RecipeIngredients ri2
                JOIN Ingredients i2 ON ri2.ingredient_id = i2.ingredient_id
                JOIN Allergens a    ON i2.allergy_id = a.allergen_id
                WHERE a.allergen_name = %s
            )
        """
        params.append(allergen_exclude)

    if ingredient:
        sql += " AND LOWER(i.ingredient_name) LIKE LOWER(%s)"
        params.append(f"%{ingredient}%")

    sql += " GROUP BY r.recipe_id ORDER BY avg_rating DESC"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def get_recipe_detail(recipe_id):
    """Return full recipe info including ingredients and recommended drink."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*,
                       COALESCE(AVG(rr.ratings), 0) AS avg_rating,
                       COUNT(rr.ratings)              AS rating_count
                FROM Recipes r
                LEFT JOIN RecipeRatings rr ON r.recipe_id = rr.recipe_id
                WHERE r.recipe_id = %s
                GROUP BY r.recipe_id
            """, (recipe_id,))
            recipe = cur.fetchone()

            cur.execute("""
                SELECT i.ingredient_name, ri.quantity, i.unit, i.cost_per_unit
                FROM RecipeIngredients ri
                JOIN Ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE ri.recipe_id = %s
            """, (recipe_id,))
            ingredients = cur.fetchall()

            cur.execute("""
                SELECT d.drink_name
                FROM Recommended_Drinks rd
                JOIN Drinks d ON rd.drink_id = d.drink_id
                WHERE rd.recipe_id = %s
            """, (recipe_id,))
            drinks = cur.fetchall()

    return recipe, ingredients, drinks


def get_saved_recipes(user_id):
    """Return all recipes saved by a user with their ingredient lists."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.description,
                       r.cuisine, r.type, r.cook_time, r.servings
                FROM UserSavedRecipes usr
                JOIN Recipes r ON usr.recipe_id = r.recipe_id
                WHERE usr.user_id = %s
                ORDER BY r.recipe_name
            """, (user_id,))
            return cur.fetchall()


def get_shopping_list(user_id):
    """
    Generate a consolidated shopping list from all saved recipes.
    Aggregates identical ingredients across recipes.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.ingredient_name,
                       SUM(ri.quantity)   AS total_quantity,
                       i.unit,
                       i.cost_per_unit,
                       SUM(ri.quantity * i.cost_per_unit) AS line_cost
                FROM UserSavedRecipes usr
                JOIN RecipeIngredients ri ON usr.recipe_id = ri.recipe_id
                JOIN Ingredients i        ON ri.ingredient_id = i.ingredient_id
                WHERE usr.user_id = %s
                GROUP BY i.ingredient_name, i.unit, i.cost_per_unit
                ORDER BY i.ingredient_name
            """, (user_id,))
            return cur.fetchall()


def save_recipe(user_id, recipe_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO UserSavedRecipes (user_id, recipe_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING
            """, (user_id, recipe_id))
        conn.commit()


def remove_saved_recipe(user_id, recipe_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM UserSavedRecipes
                WHERE user_id = %s AND recipe_id = %s
            """, (user_id, recipe_id))
        conn.commit()


def rate_recipe(user_id, recipe_id, rating):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO RecipeRatings (user_id, recipe_id, ratings)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, recipe_id) DO UPDATE SET ratings = %s
            """, (user_id, recipe_id, rating, rating))
        conn.commit()


def get_allergens():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT allergen_name FROM Allergens ORDER BY allergen_name")
            return [r["allergen_name"] for r in cur.fetchall()]


def get_cuisines():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT cuisine FROM Recipes ORDER BY cuisine")
            return [r["cuisine"] for r in cur.fetchall()]


def get_meal_types():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT type FROM Recipes ORDER BY type")
            return [r["type"] for r in cur.fetchall()]


def login_user(email, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, user_name FROM Users
                WHERE email = %s AND password = %s
            """, (email, password))
            return cur.fetchone()


def register_user(username, email, password):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Users (user_name, email, password)
                    VALUES (%s, %s, %s) RETURNING user_id
                """, (username, email, password))
                uid = cur.fetchone()["user_id"]
            conn.commit()
            return uid, None
    except psycopg2.errors.UniqueViolation:
        return None, "Email already registered."
