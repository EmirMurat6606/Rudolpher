import sqlite3

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidgetItem, QTableWidget, QPushButton, QMessageBox, QLabel

from Src.HTMLParser import HTMLParser
from Src.RudolphTable import Rudolpher
from Src.WebScraper import WebScraper


class SwimmerTableDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.rudolph_calculator = Rudolpher()
        self.web_scraper = WebScraper()
        self.setMinimumSize(600, 800)

        # Define the table
        self.table: QTableWidget = QTableWidget()

        # Define buttons
        self.refresh_button: QPushButton = QPushButton()

        # Info label for extra swimmer info
        self.info_label: QLabel = QLabel()

        # Set up the UI
        self.__setup_ui()

        # Create events
        self.__create_events()

        # Initial setup of the table
        self.__refresh_table()

    def __setup_ui(self):
        """
        Sets up the graphical elements of the SwimmerTableDialog
        """
        self.setWindowTitle("Zwemmer tabellen")
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        # Mouse tracking mode on + no editing allowed
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Label customization
        self.info_label.setText("Klik voor extra info")
        self.info_label.setStyleSheet("font-size: 20px; color: gray;")

        # Customize the buttons
        self.refresh_button.setText("Ververs tabel")
        self.refresh_button.setStyleSheet("background-color: lightblue; color: black; border: 4px solid black;")

        # Add all widgets to the layout
        layout.addWidget(self.table)
        layout.addWidget(self.info_label)
        layout.addWidget(self.refresh_button)

        # Set the layout
        self.setLayout(layout)

    def __create_events(self) -> None:
        """
        Creates events for the SwimmerTableDialog
        """
        self.refresh_button.clicked.connect(self.__refresh_table)
        self.table.cellDoubleClicked.connect(self.__calc_rudolph_points)
        self.table.cellClicked.connect(self.__show_swimmer_info)

    def __refresh_table(self) -> None:
        """
        Refreshes the table with the current data from the database
        """

        swimmers: dict = {}

        try:
            swimmers = self.database.get_sorted_swimmers()
        except sqlite3.Error:
            QMessageBox.critical(self, "Database Error", "Er is een fout opgetreden bij het ophalen van de zwemmers")

        max_rows = max(len(swimmers["male"]), len(swimmers["female"]))
        self.table.setRowCount(max_rows)
        self.table.setColumnCount(6)

        # Set up the headers
        self.table.setHorizontalHeaderLabels(
            ["Voornaam (M)", "Achternaam (M)", "RudolphPunten (M)", "Voornaam (F)", "Achternaam (F)",
             "RudolphPunten (F)"])

        # Fill table with data
        for row in range(max_rows):
            if row < len(swimmers["male"]):
                male = swimmers["male"][row]
                self.table.setItem(row, 0, QTableWidgetItem(male["firstname"]))
                self.table.setItem(row, 1, QTableWidgetItem(male["lastname"]))
                self.table.setItem(row, 2, QTableWidgetItem(f"{male['rudolph_points']:.2f}"))

            if row < len(swimmers["female"]):
                female = swimmers["female"][row]
                self.table.setItem(row, 3, QTableWidgetItem(female["firstname"]))
                self.table.setItem(row, 4, QTableWidgetItem(female["lastname"]))
                self.table.setItem(row, 5, QTableWidgetItem(f"{female['rudolph_points']:.2f}"))

        self.table.resizeColumnsToContents()

    def __cur_table_data(self, row: int, col: int) -> dict:
        """
        Get the data of the cell in the table
        :param row: The row of the cell
        :param col: The column of the cell
        :return: A dictionary with the swimmer data (firstname, lastname, gender)
        """
        return {"firstname": self.table.item(row, 0 if col < 3 else 3).text(),
            "lastname": self.table.item(row, 1 if col < 3 else 4).text(), "gender": "male" if col < 3 else "female"}

    def __show_swimmer_info(self, row: int, col: int) -> None:
        """
        Shows additional information about the swimmer when the cell is entered
        :param row: The row of the cell
        :param col: The column of the cell
        """
        # Get the swimmer data from the table
        data = self.__cur_table_data(row, col)

        try:
            # Get swimmer information from the local database
            swimmer_info: dict = self.database.get_swimmer(data["firstname"], data["lastname"], data["gender"])

            # Show the swimmer information in the info label
            self.info_label.setText(
                f"Naam: {swimmer_info['firstname']} {swimmer_info['lastname']}, Geslacht: {swimmer_info['gender']},"
                f" Categorie: {swimmer_info['age']} jaar, Rudolph punten: {swimmer_info['rudolph_points']},"
                f" Swimrankings ID: {swimmer_info['id']}")

        except ValueError:
            QMessageBox.critical(self, "Databasefout", "Zwemmer niet gevonden in de database")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Fout", f"Databasefout: {e}", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Onverwachte fout: {e}", QMessageBox.Ok)

    def __calc_rudolph_points(self, row: int, col: int) -> None:
        """
        Calculates the Rudolph points for every swimmer in the database
        :param row: The row of the cell
        :param col: The column of the cell
        """
        # Disable any action while processing calculation
        # This is to prevent multiple calculations at the same time
        self.setEnabled(False)

        # Get the swimmer data from the table
        data = self.__cur_table_data(row, col)

        try:
            # Get swimmer information from the local database
            swimmer_info: dict = self.database.get_swimmer(data["firstname"], data["lastname"], data["gender"])

            # Get the html structure of the swimrankings page of the swimmer (using its unique ID)
            # It will redirect automatically to the current season webpage
            website = self.web_scraper.swimmer_website(swimmer_info["id"])

            # Parse the website and extract the season bests of the swimmer
            season_bests = HTMLParser.parse_results(website)

            # Calculate the total rudolph points of the swimmer
            # Total = highest in short course + highest in long course
            total = self.rudolph_calculator.get_max_points(swimmer_info["age"], swimmer_info["gender"], season_bests)
            new_total = round(total[0] + total[1], 3)

            # Show the total rudolph points in a message box
            QMessageBox.information(self, "Rudolph Punten",
                                    f"Rudolph punten: 25m bad: {total[0]}, 50m bad: {total[1]}, Totaal: "
                                    f"{new_total}", QMessageBox.Ok)

            self.database.update_points(data["firstname"], data["lastname"], data["gender"], new_total)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Databasefout", str(e), QMessageBox.Ok)

        except ValueError as e:
            QMessageBox.critical(self, "Fout", f"{e}. !!!", QMessageBox.Ok)

        except Exception as e:
            QMessageBox.critical(self, "Onbekende fout", str(e), QMessageBox.Ok)

        finally:
            self.__refresh_table()
            self.setEnabled(True)
