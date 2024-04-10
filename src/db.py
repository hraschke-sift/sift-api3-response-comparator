import sqlite3
import json


def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS api_responses (
            id INTEGER PRIMARY KEY,
            customer_id TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            response_before TEXT,
            response_after TEXT,
            difference TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def insert_or_update_response(db_path, customer_id, endpoint, response, before=True):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Serialize response to JSON if it's a dictionary
    if isinstance(response, dict):
        response = json.dumps(response)

    # Check if the row exists
    cursor.execute(
        "SELECT id FROM api_responses WHERE customer_id = ? AND endpoint = ?",
        (customer_id, endpoint),
    )
    row = cursor.fetchone()

    if row is None:
        # Insert a new row if it doesn't exist
        if before:
            cursor.execute(
                "INSERT INTO api_responses (customer_id, endpoint, response_before) VALUES (?, ?, ?)",
                (customer_id, endpoint, response),
            )
        else:
            cursor.execute(
                "INSERT INTO api_responses (customer_id, endpoint, response_after) VALUES (?, ?, ?)",
                (customer_id, endpoint, response),
            )
    else:
        # Update the existing row
        if before:
            cursor.execute(
                "UPDATE api_responses SET response_before = ? WHERE customer_id = ? AND endpoint = ?",
                (response, customer_id, endpoint),
            )
        else:
            cursor.execute(
                "UPDATE api_responses SET response_after = ? WHERE customer_id = ? AND endpoint = ?",
                (response, customer_id, endpoint),
            )

    conn.commit()
    conn.close()


def get_responses(db_path, customer_id, endpoint):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT response_before, response_after FROM api_responses WHERE customer_id = ? AND endpoint = ?",
        (customer_id, endpoint),
    )
    response_before, response_after = cursor.fetchone()
    conn.close()

    return response_before, response_after


def set_difference(db_path, customer_id, endpoint, difference):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE api_responses SET difference = ? WHERE customer_id = ? AND endpoint = ?",
        (difference, customer_id, endpoint),
    )

    conn.commit()
    conn.close()
