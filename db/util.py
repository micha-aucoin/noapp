#!/usr/bin/env python3

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_FILE = BASE_DIR / "app.db"

def main():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    try:
        while True:
            sql = input("sqlite> ").strip()
            if sql in {".quit", ".exit"}:
                break
            if not sql:
                continue
            try:
                cursor = connection.execute(sql)
                if cursor.description:
                    rows = cursor.fetchall()
                    for row in rows:
                        print(dict(row))
                else:
                    connection.commit()
                    print(f"{cursor.rowcount} rows affected")
            except sqlite3.Error as error:
                print(f"error: {error}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()

