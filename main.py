""""
@Author: Emir Murat
@Description: This is the main entry point of the application.
@Warning: DO NOT CHANGE THIS FILE
@Date: 2025-01-17
"""

from Interface.MainWindow import *
import sys

if __name__ == "__main__":
    # Create the swimmer database and connect to it
    swimmer_db = SwimmerDatabase()

    # Create the application and main window
    app = QApplication(sys.argv)
    window = MainWindow(swimmer_db)
    window.show()

    exit_code = app.exec()

    # Close the database connection
    swimmer_db.close_connection()

    # Exit the application
    sys.exit(exit_code)


