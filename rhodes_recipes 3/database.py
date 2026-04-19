import psycopg
from dbinfo import DBUSER, DBPASS


def get_conn():
    return psycopg.connect(
        f"host=dbclass.rhodescs.org dbname=practice user={DBUSER} password={DBPASS}",
        row_factory=psycopg.rows.dict_row
    )


# ── Query functions (all hand-written SQL) ───────────────────────────────────

def search_recipes(cuisine=None, meal_type=None, max_cook_time=None,
                   allergen_exclude=None, ingredient=None):
    """
    Filter recipes by cuisine, meal type, max cook time, excluded allergen,
    or a key ingredient. Returns list of recipe dicts with avg rating.
    """
    sql = """
        SELECT DISTINCT r.recipe_id, r.recipe_name, r.description,
               r.cuisine, r.type, r.cook_time, r.unit,
               r.cost, r.servings, r.cost_per_serving,
               COALESCE(ROUND(AVG(rr.rating)::numeric, 1), 0) AS avg_rating
        FROM Recipes r
        LEFT JOIN RecipeRatings rr     ON r.recipe_id = rr.recipe_id
        LEFT JOIN RecipeIngredients ri ON r.recipe_id = ri.recipe_id
        LEFT JOIN Ingredients i        ON ri.ingredient_id = i.ingredient_id
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
        sql += " AND r.cook_time <= %s"
        params.append(int(max_cook_time))

    if allergen_exclude and allergen_exclude != "None":
        sql += """
            AND r.recipe_id NOT IN (
                SELECT ri2.recipe_id
                FROM RecipeIngredients ri2
                JOIN Ingredients i2 ON ri2.ingredient_id = i2.ingredient_id
                JOIN Allergens a    ON i2.allergy_id = a.allergen_id
                WHERE a.allergen_name = %s
            )
        """
        params.append(allergen_exclude)

    if ingredient:
        sql += " AND LOWER(i.ingredient_name) LIKE LOWER(%s)"
        params.append(f"%{ingredient}%")

    sql += " GROUP BY r.recipe_id ORDER BY avg_rating DESC, r.recipe_name"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def get_recipe_detail(recipe_id):
    """
    Return full recipe info, its ingredients (with allergen info),
    and recommended drinks.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT r.*,
                       COALESCE(ROUND(AVG(rr.rating)::numeric, 1), 0) AS avg_rating,
                       COUNT(rr.rating) AS rating_count
                FROM Recipes r
                LEFT JOIN RecipeRatings rr ON r.recipe_id = rr.recipe_id
                WHERE r.recipe_id = %s
                GROUP BY r.recipe_id
            """, (recipe_id,))
            recipe = cur.fetchone()

            cur.execute("""
                SELECT i.ingredient_name,
                       ri.quantity,
                       i.unit,
                       i.cost_per_unit,
                       a.allergen_name
                FROM RecipeIngredients ri
                JOIN Ingredients i   ON ri.ingredient_id = i.ingredient_id
                LEFT JOIN Allergens a ON i.allergy_id = a.allergen_id
                WHERE ri.recipe_id = %s
                ORDER BY i.ingredient_name
            """, (recipe_id,))
            ingredients = cur.fetchall()

            cur.execute("""
                SELECT d.drink_id, d.drink_name
                FROM RecommendedDrinks rd
                JOIN Drinks d ON rd.drink_id = d.drink_id
                WHERE rd.recipe_id = %s
                ORDER BY d.drink_name
            """, (recipe_id,))
            drinks = cur.fetchall()

    return recipe, ingredients, drinks


def get_drink_detail(drink_id):
    """Return a drink's details, ingredients, and average rating."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.drink_id, d.drink_name,
                       COALESCE(ROUND(AVG(dr.rating)::numeric, 1), 0) AS avg_rating,
                       COUNT(dr.rating) AS rating_count
                FROM Drinks d
                LEFT JOIN DrinkRatings dr ON d.drink_id = dr.drink_id
                WHERE d.drink_id = %s
                GROUP BY d.drink_id, d.drink_name
            """, (drink_id,))
            drink = cur.fetchone()

            cur.execute("""
                SELECT i.ingredient_name, di.quantity, i.unit
                FROM DrinkIngredients di
                JOIN Ingredients i ON di.ingredient_id = i.ingredient_id
                WHERE di.drink_id = %s
                ORDER BY i.ingredient_name
            """, (drink_id,))
            ingredients = cur.fetchall()

    return drink, ingredients


def get_saved_recipes(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.description,
                       r.cuisine, r.type, r.cook_time, r.unit,
                       r.servings, r.cost_per_serving
                FROM UserSavedRecipes usr
                JOIN Recipes r ON usr.recipe_id = r.recipe_id
                WHERE usr.user_id = %s
                ORDER BY r.recipe_name
            """, (user_id,))
            return cur.fetchall()


def get_shopping_list(user_id):
    """
    Consolidated shopping list from all saved recipes.
    Sums identical ingredients and estimates total cost.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.ingredient_name,
                       SUM(ri.quantity) AS total_quantity,
                       i.unit,
                       i.cost_per_unit,
                       ROUND((SUM(ri.quantity) * i.cost_per_unit)::numeric, 2) AS line_cost
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
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
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
                INSERT INTO RecipeRatings (user_id, recipe_id, rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, recipe_id) DO UPDATE SET rating = %s
            """, (user_id, recipe_id, rating, rating))
        conn.commit()


def rate_drink(user_id, drink_id, rating):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO DrinkRatings (user_id, drink_id, rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, drink_id) DO UPDATE SET rating = %s
            """, (user_id, drink_id, rating, rating))
        conn.commit()


def get_user_allergies(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.allergen_name
                FROM UserAllergies ua
                JOIN Allergens a ON ua.allergen_id = a.allergen_id
                WHERE ua.user_id = %s
            """, (user_id,))
            return [r["allergen_name"] for r in cur.fetchall()]


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
                SELECT user_id, user_name
                FROM Users
                WHERE email = %s AND password = %s
            """, (email, password))
            return cur.fetchone()


def register_user(username, email, password):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Users (user_name, email, password)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                """, (username, email, password))
                uid = cur.fetchone()["user_id"]
            conn.commit()
            return uid, None
    except psycopg.errors.UniqueViolation:
        return None, "Email already registered."
