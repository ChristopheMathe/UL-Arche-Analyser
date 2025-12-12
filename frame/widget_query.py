"""
    This module provides:
        - the `TwoColumnWidget` class, a PyQt6-based widget that manages class schedules consisting of start and end
          datetime pairs.

        - the `CheckableComboBox` class, a custom QComboBox that allows each item in the dropdown list to have a
          checkbox

        - the `WidgetQuery` class, a widget that displays a small query interface
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
import locale

from dateutil.parser import parse
from json            import load, dump
from os              import path, remove
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QBrush, QColor, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (QLabel, QComboBox, QInputDialog, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton)

# ==================================================================================================================== #
# PROJECT LIBRARIES
# ==================================================================================================================== #
from lib.parameters import SAVE_FILE

# ==================================================================================================================== #
# CLASS TwoColumnWidget
# ==================================================================================================================== #
class TwoColumnWidget(QWidget):
    """
        A QWidget to manage class schedules with start and end times.

        Features:
            - Load/save schedule JSON data.
            - Add/remove classes.
            - Add/remove rows in a 2-column schedule table.
            - Validate datetime input in table cells.

        Here a schema to describe widgets and layout:

        +----------------------------------------------------------+
        | 'Select_class', schedule_selection                       |
        |----------------------------------------------------------|
        | button_new_class, button_save_class, button_remove_class |
        |----------------------------------------------------------|
        | table                                                    |
        +----------------------------------------------------------+
        | button_add_schedule, button_remove_schedule              |
        +----------------------------------------------------------+
    """
    def __init__(self):
        super().__init__()

        # Set local format date to french format
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

        # Main vertical layout for the widget
        layout = QVBoxLayout(self)

        # Row containing label + combo box for class selection
        layout_load_class = QHBoxLayout()

        # Add the QLabel("Select class")
        layout_load_class.addWidget(QLabel("Select class"))

        # Dictionary storing all class schedules
        self.class_info = {}

        # Dropdown to select class
        self.class_selection = QComboBox()

        # Add the class selection dropdown to the layout_load_class
        layout_load_class.addWidget(self.class_selection)

        # Load existing JSON data if SAVE_FILE exists
        if path.exists(SAVE_FILE):

            with open(SAVE_FILE, 'r') as f:

                # Read JSON into dict
                self.class_info = load(f)

                # List of class names
                list_classes = self.class_info.keys()

        else:

            # No saved classes
            list_classes = []

        # Populate dropdown with classes
        self.class_selection.addItems(list_classes)

        # Add class section to main layout
        layout.addLayout(layout_load_class)

        # Row for new/save/remove class buttons
        layout_managed_class = QHBoxLayout()

        # Button to create a new class
        button_new_class = QPushButton("New class")

        # Add button to the layout_managed_class
        layout_managed_class.addWidget(button_new_class)

        # Connect to method self.class_add
        button_new_class.clicked.connect(self.class_add)

        # Button to save current class schedule
        button_save_class = QPushButton("Save class")

        # Add button to the layout_managed_class
        layout_managed_class.addWidget(button_save_class)

        # Connect to method self.class_save
        button_save_class.clicked.connect(self.class_save)

        # Button to delete selected class
        button_remove_class = QPushButton("Remove class")

        # Add button to the layout_managed_class
        layout_managed_class.addWidget(button_remove_class)

        # Connect to method self.class_remove
        button_remove_class.clicked.connect(self.class_remove)

        # Add button row to layout
        layout.addLayout(layout_managed_class)

        # Create table with 2 columns
        self.table = QTableWidget(0, 2)

        # Set column headers
        self.table.setHorizontalHeaderLabels(["Start", "End"])

        # Add table to layout
        layout.addWidget(self.table)

        # Enable copy/paste
        self.table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

        # Enable cells selection
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

        # Enable contiguous selection
        self.table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)

        # Row for add/remove schedule row buttons
        layout_schedule_manage = QHBoxLayout()

        # Add the layout_schedule to the main layout
        layout.addLayout(layout_schedule_manage)

        # Adds an empty row
        button_add_schedule = QPushButton("Add schedule")

        # Add button_add_schedule to the layout_schedule_manage
        layout_schedule_manage.addWidget(button_add_schedule)

        # When the button_add_schedule is clicked, trigger the method self.add_row
        button_add_schedule.clicked.connect(self.add_row)

        # Removes selected row
        button_remove_schedule = QPushButton("Remove schedule")

        # Add button_remove_schedule to the layout_schedule_manage
        layout_schedule_manage.addWidget(button_remove_schedule)

        # When the button_remove_schedule is clicked, trigger the method self.remove_selected_row
        button_remove_schedule.clicked.connect(self.remove_selected_row)

        # Validate cells whenever edited
        self.table.itemChanged.connect(self.validate_cell)

        # Load schedule when class changes
        self.class_selection.currentTextChanged.connect(self.load_data)

        # Load initial data for dropdown selection
        self.load_data()

    def add_row(self) -> None:
        """
            Insert a new empty row at the end of the table.
        """
        # Current number of rows
        row = self.table.rowCount()

        # Insert new empty row
        self.table.insertRow(row)

    def class_add(self) -> None:
        """
            Prompt user to add a new class and update dropdown.
        """
        # Open a new window asking a name of the added class
        name, ok = QInputDialog.getText(None, "Add class", "Enter the name of the class")

        # If user confirmed and provided a name
        if ok and name:

            # Create new class entry
            self.class_info[name] = []

            # Add to dropdown
            self.class_selection.addItem(name)

            # Automatically select it
            self.class_selection.setCurrentText(name)

            # Load empty schedule
            self.load_data()

    def class_remove(self) -> None:
        """
            Remove currently selected class and update dropdown.
        """
        # Check if the schedule selection is not empty
        if self.class_selection.currentText() != '':

            # Remove class from internal dict
            self.class_info.pop(self.class_selection.currentText())

            # Remove from dropdown
            self.class_selection.removeItem(self.class_selection.currentIndex())

            # Save updated data
            self.class_save()

    def class_save(self) -> None:
        """
            Save table data of selected class to JSON file.
        """
        # Update entry
        self.class_info[self.class_selection.currentText()] = self.get_data()

        # Only save if not an empty placeholder
        if self.class_info != {'': []}:

            # Open the SAVE_FILE
            with open(SAVE_FILE, "w", encoding="utf-8") as f:

                # Write JSON
                dump(self.class_info, f, indent=4)
        else:
            # Check if file exists before remove it
            if path.exists(SAVE_FILE):
                # Remove file if all data is empty
                remove(SAVE_FILE)

    def get_data(self) -> list[tuple]:
        """
            Extract all schedule rows from the table.

            :return: list of tuple contains start_time and end_time of the schedule
        """
        # Initialize the list of schedule
        list_schedule = []

        # Loop over table row
        for row in range(self.table.rowCount()):

            # Get the start_time of the schedule
            col1 = self.table.item(row, 0).text() if self.table.item(row, 0) else ""

            # Get the end_time of the schedule
            col2 = self.table.item(row, 1).text() if self.table.item(row, 1) else ""

            # Add tuple to list
            list_schedule.append((col1, col2))

        return list_schedule

    @staticmethod
    def is_datetime(text) -> bool:
        """
            Return True if the given text can be parsed as a datetime.

            :return: True if valid datetime, False otherwise.
        """
        # Attempt parsing
        try:
            parse(text)
            return True

        # Parsing failed
        except Exception:
            return False

    def load_data(self) -> None:
        """
            Populate table with schedule data of selected class.
        """
        # Check if the class selected is listed in the dictionary self.class_info
        if self.class_selection.currentText() in self.class_info:

            # Retrieve schedule list
            schedule_list = self.class_info[self.class_selection.currentText()]

            # Clear table
            self.table.setRowCount(0)

            # Loop over schedule
            for col1, col2 in schedule_list:

                # Get the number of row
                row = self.table.rowCount()

                # Insert a new row at the 'row' index
                self.table.insertRow(row)

                # Edit the start_time column of this row
                self.table.setItem(row, 0, QTableWidgetItem(col1))

                # Edit the end_time column of this row

                self.table.setItem(row, 1, QTableWidgetItem(col2))
        else:
            # If class has no data, clear table
            self.table.setRowCount(0)

            # Edit the start_time column with an empty string
            self.table.setItem(0, 0, QTableWidgetItem(""))

            # Edit the end_time column with an empty string
            self.table.setItem(0, 0, QTableWidgetItem(""))

    def remove_selected_row(self) -> None:
        """
            Remove the currently selected row.
        """
        # Get selected row index
        row = self.table.currentRow()

        # Check if the row index is strictly superior to 0
        if row >= 0:

            # Delete that row
            self.table.removeRow(row)

    def validate_cell(self, item) -> None:
        """
            Check if the cell contains a valid datetime string.

            Highlights invalid cells in red and provides tooltip.
        """
        # Get edited cell content
        text = item.text()

        # Check if the datetime in the cell is a datetime format
        if self.is_datetime(text):

            # Clear error background
            item.setBackground(QBrush(QColor("transparent")))

            # Helpful tooltip
            item.setToolTip("Valid datetime")

        else:

            # Highlight invalid datetime
            item.setBackground(QBrush(QColor("red")))

            # Helpful tooltip
            item.setToolTip("Invalid datetime format (expected YYYY-MM-DD HH:MM)")


# ==================================================================================================================== #
# CLASS CheckableComboBox
# ==================================================================================================================== #
class CheckableComboBox(QComboBox):
    """
        A custom QComboBox that allows each item in the dropdown list to have a checkbox. Multiple selections can be
        made, and the widget keeps the menu open when clicking items by handling the pressed signal manually.
    """
    def __init__(self):
        """
            Initialize the combo box and set up the internal model.
        """
        # Initialize the parent QComboBox
        super().__init__()

        # Use a QStandardItemModel to store checkable items
        self.setModel(QStandardItemModel(self))

        # needed to avoid disappearing menu after clicking
        self.view().pressed.connect(self.handle_item_pressed)

    def add_checkable_item(self, text: str, checked: bool = False) -> None:
        """
            Add an item to the combo box with an associated checkbox

            :param text: The displayed text for the item
            :param checked: Whether the checkbox should start checked
        """
        # Create a new item with the given text
        item = QStandardItem(text)

        # Set item to be checkable and enabled
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)

        # Store the item's initial check state
        item.setData(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

        # Add the item to the combo box's model
        self.model().appendRow(item)

    def handle_item_pressed(self, index: int) -> None:
        """
            Toggle the check state of an item when it is clicked.

            :param index: The index of the pressed item.
        """
        # Retrieve the item clicked by the user
        item = self.model().itemFromIndex(index)

        # Toggle the item's check state
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def checked_items(self) -> list[str]:
        """
            :return: a list containing the text of all checked items.
        """
        # List of checked item texts
        items = []

        # Iterate over all items
        for i in range(self.model().rowCount()):

            # Get item by row index
            item = self.model().item(i)

            # Check if item is checked
            if item.checkState() == Qt.CheckState.Checked:

                # Collect text if checked
                items.append(item.text())

        return items


# ==================================================================================================================== #
# CLASS WidgetQuery
# ==================================================================================================================== #
class WidgetQuery(QWidget):
    """
        A widget that displays a small query interface consisting of:
        - A class label
        - A two-column widget (likely for schedule or class selection)
        - A checkable combo box for student filtering
        - A compute button

        This widget acts as a container for assembling and organizing UI components that allow the user to select
        class-related options and trigger computations.
    """

    def __init__(self, parent=None):
        """
            Initialize the query widget.

            :param parent: parent widget [Optional]
        """
        # Initialize the base QWidget class
        QWidget.__init__(self, parent)

        # Main vertical layout for the entire widget
        self.layout_query = QVBoxLayout()

        # Add a label describing the next section
        self.layout_query.addWidget(QLabel('Class'))

        # Two-column widget for class/schedule info
        self.widget_json_schedule = TwoColumnWidget()

        # Add it to the layout
        self.layout_query.addWidget(self.widget_json_schedule)

        # Section label for filtering students
        self.layout_query.addWidget(QLabel("Student selection"))

        # Instantiate the checkable combo box
        self.widget_student_filter = CheckableComboBox()

        # Give it an object name for styling or lookup
        self.widget_student_filter.setObjectName("student_filter")

        # Add it to the layout
        self.layout_query.addWidget(self.widget_student_filter)

        # Button users click to compute the query
        self.button_compute = QPushButton('Compute')

        # Add button to layout
        self.layout_query.addWidget(self.button_compute)

        # Push previous widgets up and add spacing at bottom
        self.layout_query.addStretch()

        # Apply the layout to the widget
        super().setLayout(self.layout_query)