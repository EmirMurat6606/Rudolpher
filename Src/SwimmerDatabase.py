import sqlite3
import sys
from datetime import datetime


class SwimmerDatabase:
    def __init__(self, db_name="./Database/swimmers.db"):
        """Initialize the database connection and create the table if it doesn't exist"""
        self.db_name = db_name
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        """
        Connect to the database and create the table if it doesn't exist
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            cursor = self.connection.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS swimmer (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                birthyear INTEGER NOT NULL,
                gender TEXT NOT NULL CHECK(gender IN ('male', 'female')),
                id INTEGER NOT NULL CHECK(id > 0),
                points FLOAT CHECK(points >= 0),
                PRIMARY KEY (firstname, lastname, gender)
            )
            ''')
            self.connection.commit()
            print("Database connected successfully")
        except sqlite3.Error as e:
            print(f"Could not connect with the database: {e}")
            sys.exit(1)

    def add_swimmer(self, firstname: str, lastname: str, birth_year: int, gender: str, swimmer_id: int) -> None:
        """
        Add a swimmer to the database.
        :param firstname: First name of the swimmer
        :param lastname: Last name of the swimmer
        :param birth_year: Birth year of the swimmer (must be > 1900 and <= current year)
        :param gender: Gender of the swimmer ('male' or 'female')
        :param swimmer_id: ID of the swimmer (must be > 0)
        """
        current_year = datetime.now().year
        if not (1900 < birth_year <= current_year):
            raise ValueError("Geboortejaar moet tussen 1900 en het huidige jaar liggen")

        try:

            cursor = self.connection.cursor()

            query = """
               INSERT INTO swimmer (firstname, lastname, birthyear, gender, points, id)
               VALUES (?, ?, ?, ?, ?, ?)
               """
            cursor.execute(query, (firstname, lastname, birth_year, gender, 0, swimmer_id))

            self.connection.commit()
            print(f"Zwemmer {firstname} {lastname} succesvol toegevoegd!")
        except sqlite3.IntegrityError as e:
            raise ValueError("Zwemmer bestaat al in de database.") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Databasefout: {e}") from e

    def remove_swimmer(self, firstname: str, lastname: str, gender: str) -> None:
        """
        Remove a swimmer from the database.
        :param firstname: First name of the swimmer
        :param lastname: Last name of the swimmer
        :param gender: Gender of the swimmer ('male' or 'female')
        """
        try:
            cursor = self.connection.cursor()
            #  Remove the swimmer from the database
            cursor.execute('''
            DELETE FROM swimmer
            WHERE firstname = ? AND lastname = ? AND gender = ?
            ''', (firstname, lastname, gender))

            # Check if the swimmer was found
            if cursor.rowcount == 0:
                raise ValueError(f"Geen zwemmer gevonden met naam {firstname} {lastname} en geslacht {gender}.")

            print(f"Zwemmer {firstname} {lastname} succesvol verwijderd.")

            self.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Databasefout bij het verwijderen: {e}") from e

    def get_swimmer(self, firstname: str, lastname: str, gender: str) -> dict:
        """
        Get a swimmer from the database using firstname, lastname, and gender.
        :param firstname: First name of the swimmer
        :param lastname: Last name of the swimmer
        :param gender: Gender of the swimmer ('male' or 'female')
        :return: A dictionary with the swimmer's data {first_name, last_name, age, gender, id} or None if not found
        """
        try:
            current_year = datetime.now().year
            cursor = self.connection.cursor()
            cursor.execute('''
            SELECT firstname, lastname, birthyear, gender, points, id
            FROM swimmer
            WHERE firstname = ? AND lastname = ? AND gender = ?
            ''', (firstname, lastname, gender))
            swimmer = cursor.fetchone()
            if swimmer:
                return {"firstname": swimmer[0], "lastname": swimmer[1], "age": current_year - swimmer[2],
                        "gender": swimmer[3], "rudolph_points": swimmer[4], "id": swimmer[5]}
            else:
                raise ValueError(f"Geen zwemmer gevonden met naam {firstname} {lastname} en geslacht {gender}")

        except sqlite3.Error as e:
            raise RuntimeError(f"Fout bij het ophalen van zwemmer: {e}") from e

    def get_sorted_swimmers(self) -> dict:
        """
        Retrieve and sort swimmers by Rudolph points (descending) and then alphabetically by lastname and firstname.
        Separate swimmers into male and female groups.

        :return: A dictionary with two keys: 'male' and 'female', each containing a sorted list of swimmer dictionaries.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT firstname, lastname, birthyear, gender, points, id
                FROM swimmer
                ORDER BY gender ASC, points DESC, lastname ASC, firstname ASC
            ''')
            swimmers = cursor.fetchall()
            sorted_swimmers = {"male": [], "female": []}

            # Categorize swimmers by gender
            current_year = datetime.now().year
            for swimmer in swimmers:
                swimmer_data = {"firstname": swimmer[0], "lastname": swimmer[1], "age": current_year - swimmer[2],
                    # Calculate age
                    "gender": swimmer[3], "rudolph_points": swimmer[4], "id": swimmer[5]}
                if swimmer[3] == "male":
                    sorted_swimmers["male"].append(swimmer_data)
                elif swimmer[3] == "female":
                    sorted_swimmers["female"].append(swimmer_data)

            return sorted_swimmers
        except sqlite3.Error as e:
            raise RuntimeError("Fout bij het ophalen van de zwemmers")

    def update_points(self, firstname: str, lastname: str, gender: str, new_points: float) -> None:
        """
        Update the points of a swimmer in the database.
        :param firstname: First name of the swimmer
        :param lastname: Last name of the swimmer
        :param gender: Gender of the swimmer ('male' or 'female')
        :param new_points: New points value to update (must be > 0)
        """

        try:
            cursor = self.connection.cursor()
            # Update the points for the swimmer
            cursor.execute('''
                UPDATE swimmer
                SET points = ?
                WHERE firstname = ? AND lastname = ? AND gender = ?
            ''', (new_points, firstname, lastname, gender))
            self.connection.commit()

            if cursor.rowcount == 0:
                raise ValueError("Database connectie mislukt! Punten niet geüpdated!")
        except sqlite3.Error as e:
            raise RuntimeError("Punten updaten niet gelukt. Mogelijks is zwemmer niet gevonden in de database!")

    def close_connection(self) -> None:
        """
        Close the database connection
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed")
