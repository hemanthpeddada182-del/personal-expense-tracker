import sqlite3


# Display database errors in the VS Code terminal
def handle_database_error(error):
    print(f"Database error: {error}")


# Create a database connection
def create_connection():
    try:
        connection = sqlite3.connect("expenses.db")
        return connection

    except sqlite3.Error as error:
        handle_database_error(error)
        return None


# Create database tables
def create_table():
    connection = create_connection()

    if connection is None:
        return

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                notes TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS monthly_budgets (
                month TEXT PRIMARY KEY,
                budget REAL NOT NULL
            )
        """)

        connection.commit()

    except sqlite3.Error as error:
        handle_database_error(error)

    finally:
        connection.close()


# Add a new expense
def add_expense(expense_name, amount, category, expense_date, notes):
    connection = create_connection()

    if connection is None:
        return False

    try:
        connection.execute(
            """
            INSERT INTO expenses
            (expense_name, amount, category, expense_date, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (expense_name, amount, category, expense_date, notes)
        )

        connection.commit()
        return True

    except sqlite3.Error as error:
        handle_database_error(error)
        return False

    finally:
        connection.close()


# Retrieve all expenses
def get_expenses():
    connection = create_connection()

    if connection is None:
        return []

    try:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT id, expense_name, amount, category, expense_date, notes
            FROM expenses
            ORDER BY expense_date DESC, id DESC
        """).fetchall()

        return [dict(row) for row in rows]

    except sqlite3.Error as error:
        handle_database_error(error)
        return []

    finally:
        connection.close()


# Calculate total spending
def get_total_spending():
    connection = create_connection()

    if connection is None:
        return 0

    try:
        result = connection.execute("""
            SELECT SUM(amount)
            FROM expenses
        """).fetchone()

        return result[0] if result[0] is not None else 0

    except sqlite3.Error as error:
        handle_database_error(error)
        return 0

    finally:
        connection.close()


# Calculate spending by category
def get_category_spending():
    connection = create_connection()

    if connection is None:
        return []

    try:
        rows = connection.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()

        return rows

    except sqlite3.Error as error:
        handle_database_error(error)
        return []

    finally:
        connection.close()


# Calculate monthly spending
def get_monthly_spending():
    connection = create_connection()

    if connection is None:
        return []

    try:
        rows = connection.execute("""
            SELECT
                strftime('%Y-%m', expense_date) AS month,
                SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month
        """).fetchall()

        return rows

    except sqlite3.Error as error:
        handle_database_error(error)
        return []

    finally:
        connection.close()


# Delete an expense
def delete_expense(expense_id):
    connection = create_connection()

    if connection is None:
        return False

    try:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as error:
        handle_database_error(error)
        return False

    finally:
        connection.close()


# Update an existing expense
def update_expense(
    expense_id,
    expense_name,
    amount,
    category,
    expense_date,
    notes
):
    connection = create_connection()

    if connection is None:
        return False

    try:
        cursor = connection.execute(
            """
            UPDATE expenses
            SET expense_name = ?,
                amount = ?,
                category = ?,
                expense_date = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                expense_name,
                amount,
                category,
                expense_date,
                notes,
                expense_id
            )
        )

        connection.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as error:
        handle_database_error(error)
        return False

    finally:
        connection.close()


# Save or update a monthly budget
def save_monthly_budget(month, budget):
    connection = create_connection()

    if connection is None:
        return False

    try:
        connection.execute(
            """
            INSERT INTO monthly_budgets (month, budget)
            VALUES (?, ?)
            ON CONFLICT(month)
            DO UPDATE SET budget = excluded.budget
            """,
            (month, budget)
        )

        connection.commit()
        return True

    except sqlite3.Error as error:
        handle_database_error(error)
        return False

    finally:
        connection.close()


# Retrieve a monthly budget
def get_monthly_budget(month):
    connection = create_connection()

    if connection is None:
        return 0

    try:
        result = connection.execute(
            """
            SELECT budget
            FROM monthly_budgets
            WHERE month = ?
            """,
            (month,)
        ).fetchone()

        return result[0] if result else 0

    except sqlite3.Error as error:
        handle_database_error(error)
        return 0

    finally:
        connection.close()


# Calculate spending for a particular month
def get_monthly_total(month):
    connection = create_connection()

    if connection is None:
        return 0

    try:
        result = connection.execute(
            """
            SELECT SUM(amount)
            FROM expenses
            WHERE strftime('%Y-%m', expense_date) = ?
            """,
            (month,)
        ).fetchone()

        return result[0] if result[0] is not None else 0

    except sqlite3.Error as error:
        handle_database_error(error)
        return 0

    finally:
        connection.close()


# Filter expenses by date range and category
def filter_expenses(start_date, end_date, category):
    connection = create_connection()

    if connection is None:
        return []

    try:
        connection.row_factory = sqlite3.Row

        if category == "All":
            rows = connection.execute(
                """
                SELECT *
                FROM expenses
                WHERE expense_date BETWEEN ? AND ?
                ORDER BY expense_date DESC, id DESC
                """,
                (start_date, end_date)
            ).fetchall()

        else:
            rows = connection.execute(
                """
                SELECT *
                FROM expenses
                WHERE expense_date BETWEEN ? AND ?
                AND category = ?
                ORDER BY expense_date DESC, id DESC
                """,
                (start_date, end_date, category)
            ).fetchall()

        return [dict(row) for row in rows]

    except sqlite3.Error as error:
        handle_database_error(error)
        return []

    finally:
        connection.close()