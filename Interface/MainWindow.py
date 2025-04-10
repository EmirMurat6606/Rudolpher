from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QApplication
from Interface.AddSwimmerDialog import AddSwimmerDialog
from Interface.SwimmerTable import SwimmerTableDialog
from Src.SwimmerDatabase import SwimmerDatabase


class MainWindow(QMainWindow):
    def __init__(self, data_base: SwimmerDatabase, parent=None):
        super().__init__()
        self.data_base: SwimmerDatabase = data_base
        self.__setup_ui()
        self.__create_events()
        self.button1 = None
        self.button2 = None
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.resize(screen_geometry.width(), screen_geometry.height())

    def __setup_ui(self) -> None:
        """
        Sets up the graphical elements of the main window
        """
        self.setWindowTitle("Rudolpher")
        self.setStyleSheet("background-color: cyan;")

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()  # Separate horizontal layout for buttons

        # Create buttons
        self.button1 = QPushButton("Voeg zwemmer toe", self)
        self.button2 = QPushButton("Zwemmer tabellen", self)
        self.button1.setFixedSize(300, 100)
        self.button2.setFixedSize(300, 100)
        self.button1.setStyleSheet("background-color: lightblue; color: black; border: 4px solid black;")
        self.button2.setStyleSheet("background-color: lightblue; color: black; border: 4px solid black;")

        # Add spacing between buttons
        button_layout.addStretch(1)  # Stretch left
        button_layout.addWidget(self.button1)
        button_layout.addStretch(1)  # Stretch center
        button_layout.addWidget(self.button2)
        button_layout.addStretch(1)  # Stretch right

        # Add the button layout to the main vertical layout
        layout.addStretch(1)  # Stretch above buttons
        layout.addLayout(button_layout)
        layout.addStretch(1)  # Stretch below buttons

        # Place the layout in the central widget
        central_widget.setLayout(layout)

    def __create_events(self) -> None:
        """
        Creates events for the main window
        """
        self.button1.clicked.connect(self.__to_add_swimmer)
        self.button2.clicked.connect(self.__to_swimmer_table)

    def __to_add_swimmer(self) -> None:
        """
        Open the AddSwimmerDialog
        """
        dialog = AddSwimmerDialog(self.data_base, self)
        dialog.exec()

    def __to_swimmer_table(self) -> None:
        """
        Open the SwimmerTableDialog
        """
        dialog = SwimmerTableDialog(self.data_base, self)
        dialog.show()
