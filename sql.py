"""
SQL.py — A drop-in replacement for cs50's SQL class.

Usage is identical to cs50:
    from SQL import SQL
    db = SQL("sqlite:///weather.db")
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

Supports:
    - sqlite:///relative.db
    - sqlite:////absolute/path.db
    - ? positional placeholders (same as cs50)
    - SELECT  → list of dicts  (empty list if no rows)
    - INSERT  → int (last inserted row id)
    - UPDATE  → int (number of rows affected)
    - DELETE  → int (number of rows affected)
    - Other   → None
"""

import re
import sqlite3


class SQL:

    def __init__(self, url: str):
        match = re.fullmatch(r"sqlite:///(.+)", url, re.IGNORECASE)
        if not match:
            raise ValueError(
                f"Unsupported database URL: {url!r}\n"
                "Expected format:  sqlite:///filename.db\n"
                "                  sqlite:////absolute/path/to/file.db"
            )
        self._path = match.group(1)
        # Test that the file is accessible on startup, same as cs50 does
        conn = self._connect()
        conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row          # rows behave like dicts
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def execute(self, sql: str, *args):
        """
        Execute sql with positional args (? placeholders).

        Mirrors cs50.SQL.execute behaviour exactly:
          SELECT  → list[dict]
          INSERT  → lastrowid (int)
          UPDATE  → rowcount  (int)
          DELETE  → rowcount  (int)
          other   → None
        """
        # Strip leading/trailing whitespace for the keyword check
        keyword = sql.strip().upper().split()[0]

        try:
            with self._connect() as conn:
                cur = conn.execute(sql, args)
                conn.commit()

                if keyword == "SELECT":
                    # Convert sqlite3.Row objects → plain dicts (cs50 behaviour)
                    return [dict(row) for row in cur.fetchall()]

                if keyword == "INSERT":
                    return cur.lastrowid

                if keyword in ("UPDATE", "DELETE"):
                    return cur.rowcount

                return None

        except sqlite3.OperationalError as e:
            # Re-raise as a plain RuntimeError with a readable message,
            # same way cs50 surfaces SQL errors
            raise RuntimeError(str(e)) from e
