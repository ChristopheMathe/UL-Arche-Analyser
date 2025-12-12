"""
    This module defines the `ToolBar` class, a custom QToolBar used to host action inside the application.

    The toolbar currently provides one button: "OPEN", which is used to trigger CSV file loading through `open_csv()`.

    Each action is added using `add_button()`, and callback functions can be attached to actions using `on_triggered()`.

    Actions are stored as QObject children of the toolbar, enabling lookup by name via `findChild()`.
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
from PyQt6.QtGui          import QAction
from PyQt6.QtWidgets      import QToolBar
from typing               import Callable

# ==================================================================================================================== #
# PROJECT LIBRARIES
# ==================================================================================================================== #
from lib.csv_file_manager import open_csv

# ==================================================================================================================== #
# MAIN
# ==================================================================================================================== #
class ToolBar(QToolBar):
    """
        A toolbar containing actions.

        :param parent: the parent widget, here the MainWindow
    """
    def __init__(self, parent=None) -> None:
        """
            Initialize the toolbar.

            This constructor sets up the initial button ("OPEN") and places it inside the toolbar.

            Additional actions can later be added using `add_action()`.

            :param parent: the parent widget, here the MainWindow
        """
        super().__init__(parent)

        # Add the initial toolbar button dedicated to opening CSV files
        self.add_action(action_name='OPEN')


    def add_action(self, action_name: str) -> None:
        """
            Create a new QAction and add it to the toolbar.

            The created QAction is parented to the toolbar (`self`), so it can be accessed later using
            `findChild(QAction, button_name)`.

            :param action_name: the name of the new action
        """
        # Create the action, setting the toolbar as parent so findChild can locate it
        button = QAction(action_name, self)

        # Assign object name for lookup
        button.setObjectName(action_name)

        # Display the action on the toolbar
        self.addAction(button)


    def on_triggered(self, action_name: str, function: Callable) -> None:
        """
            Connect a function to the `triggered` signal of the specified toolbar 'button_name' action.

            :param action_name: name of the action
            :param function: a function that takes a keyword argument `parent` and will be executed when the action is
                             triggered.

            :raise: ValueError - If no QAction with the given name is found on the toolbar.
        """
        # Retrieve the action object by name
        button = self.findChild(QAction, action_name)

        # If the action is not found, raise it
        if button is None:
            raise ValueError(f"Action '{action_name}' not found in toolbar.")

        # Connect the action to the provided function. `_` receives the QAction's triggered signal argument (unused).
        button.triggered.connect(lambda _: function(parent=self.parent()))
