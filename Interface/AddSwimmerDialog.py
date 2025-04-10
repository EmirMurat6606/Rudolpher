import sqlite3

from PyQt5.QtWidgets import (QDialog, QGridLayout, QLabel, QRadioButton, QLineEdit, QPushButton, QButtonGroup,
                             QHBoxLayout, QVBoxLayout, QMessageBox)

from Src.HTMLParser import HTMLParser
from Src.SwimmerDatabase import SwimmerDatabase
from Src.WebScraper import WebScraper


class AddSwimmerDialog(QDialog):
    def __init__(self, data_base: SwimmerDatabase, parent=None, width: int = 600, height: int = 800):
        super().__init__()
        self.data_base = data_base
        self.web_scraper = WebScraper()

        self.setMinimumSize(width, height)

        self.first_name: QLineEdit = QLineEdit()
        self.last_name: QLineEdit = QLineEdit()
        self.gender_group: QButtonGroup = QButtonGroup()

        self.add_button: QPushButton = QPushButton()
        self.remove_button: QPushButton = QPushButton()
        self.cancel_button: QPushButton = QPushButton()

        self.setup_ui()
        self.create_events()

    def setup_ui(self) -> None:
        """
        Sets up the graphical elements of the dialog
        """
        # Set dialog properties
        self.setWindowTitle("Zwemmer Toevoegen")
        self.setStyleSheet("background-color: lightblue;")

        # Create a grid layout
        gridlayout = QGridLayout()
        gridlayout.setSpacing(10)

        # Create labels and text fields
        first_name_label = QLabel("Voornaam:")

        last_name_label = QLabel("Achternaam:")

        self.first_name.setStyleSheet("border: 2px solid black;")
        self.last_name.setStyleSheet("border: 2px solid black;")

        # Add labels and text fields to the grid layout
        gridlayout.addWidget(first_name_label, 0, 0)
        gridlayout.addWidget(self.first_name, 0, 1)
        gridlayout.addWidget(last_name_label, 1, 0)
        gridlayout.addWidget(self.last_name, 1, 1)

        # Gender selection (radio buttons)
        gender_label = QLabel("Geslacht:")
        gender_male = QRadioButton("Man")
        gender_male.setObjectName("male")
        gender_female = QRadioButton("Vrouw")
        gender_female.setObjectName("female")

        # Group the radio buttons to ensure only one can be selected at a time
        self.gender_group = QButtonGroup()
        self.gender_group.addButton(gender_male)
        self.gender_group.addButton(gender_female)

        # Add gender widgets
        gridlayout.addWidget(gender_label, 2, 0)
        gridlayout.addWidget(gender_male, 2, 1)
        gridlayout.addWidget(gender_female, 3, 1)

        # Create buttons
        button_layout = QHBoxLayout()
        self.add_button.setText("Toevoegen")
        self.remove_button.setText("Verwijderen")
        self.cancel_button.setText("Annuleren")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.cancel_button)

        # Create a vertical layout and add grid and buttons
        main_layout = QVBoxLayout()
        main_layout.addLayout(gridlayout)
        main_layout.addLayout(button_layout)

        # Set the dialog layout
        self.setLayout(main_layout)

    def create_events(self) -> None:
        """
        Creates events for the dialog
        :return: None
        """
        # Connect button signals
        self.add_button.clicked.connect(self.add_swimmer)  # Add swimmer to database
        self.remove_button.clicked.connect(self.remove_swimmer)  # Remove swimmer from database
        self.cancel_button.clicked.connect(self.reject)  # Close dialog

        pass

    def add_swimmer(self) -> None:
        """
        Add a swimmer to the database
        :return: None
        """
        self.setEnabled(False)  # Disable the dialog while processing
        try:
            # Return the request to the website
            request = self.web_scraper.create_request(self.first_name.text(), self.last_name.text(),
                                                      self.gender_group.checkedButton().objectName())

            # Get data about the swimmer from the website
            html_text = self.web_scraper.swimmer_data(request)

            # Parse the HTML to get the athlete ID and birth year
            info = HTMLParser.get_athlete_info(html_text)

            # Add the swimmer to the database
            try:
                self.data_base.add_swimmer(self.first_name.text(), self.last_name.text(), info[1],
                                           self.gender_group.checkedButton().objectName(), info[0])
                QMessageBox.information(self, "Succes", "Zwemmer succesvol toegevoegd!", QMessageBox.Ok)
                self.accept()  # Close the dialog
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Fout", f"Databasefout: {e}", QMessageBox.Ok)
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Waarschuwing", "De zwemmer staat al in de database.", QMessageBox.Ok)


        except ValueError as e:
            QMessageBox.warning(self, "Waarschuwing", f"Zwemmer toevoegen niet gelukt: {e}", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Onverwachte fout: {e}", QMessageBox.Ok)

        finally:
            self.setEnabled(True)  # Re-enable the dialog

    def remove_swimmer(self) -> None:
        """
        Remove a swimmer from the database.
        :return: None
        """
        self.setEnabled(False)

        # Ask the user if they are sure they want to delete the swimmer
        response = QMessageBox.question(self, "Verwijderen", "Wil je deze zwemmer verwijderen?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # If the user clicks 'No', do nothing
        if response == QMessageBox.No:
            self.setEnabled(True)
            return

        try:
            # Remove the swimmer from the database
            self.data_base.remove_swimmer(self.first_name.text(), self.last_name.text(),
                                          self.gender_group.checkedButton().objectName())
            QMessageBox.information(self, "Succes", "Zwemmer succesvol verwijderd!", QMessageBox.Ok)
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Waarschuwing", f"Zwemmer verwijderen niet gelukt: {e}", QMessageBox.Ok)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Fout", f"Databasefout: {e}", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Onverwachte fout: {e}", QMessageBox.Ok)

        finally:
            self.setEnabled(True)
