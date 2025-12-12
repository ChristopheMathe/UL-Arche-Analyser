"""
    This module defines the WidgetFileContent class, a PyQt6 widget used to display file-related information alongside
    the table preview that contains the CSV file. It expects the parent widget to provide a `widget_input_file`
    attribute.

    The widget layout is structured as:

        +--------------------------------------+
        | super, layout                        |
        | +----------------------------------+ |
        | | parent.widget_input_file         | |
        | +----------------------------------+ |
        | +----------------------------------+ |
        | | widget_table_data                | |
        | +----------------------------------+ |
        +--------------------------------------+
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QHeaderView

# ==================================================================================================================== #
# MAIN
# ==================================================================================================================== #
class WidgetFileContent(QWidget):
    """
        A widget that displays the file name and a table view showing the contents of the file.

        :param parent: The parent widget to provide a `widget_input_file` attribute.
    """

    def __init__(self, parent=None) -> None:
        """
            Initialize the WidgetFileContent layout and UI components.

            The layout of WidgetFileContent is set vertically, from top to bottom:
                - File information:
                    * The parent's `widget_input_file` widget
                - CSV content: a QTableView widget
                - A stretch at the bottom to keep everything aligned nicely.
        """
        super().__init__(parent)
        # ------------------------------------------------------------------------------------------------------------ #
        # Main layout
        # ------------------------------------------------------------------------------------------------------------ #

        # Main vertical layout that stacks all subwidgets
        self.layout = QVBoxLayout()

        # Set the layout to the WidgetFileContent
        self.setLayout(self.layout)

        # ------------------------------------------------------------------------------------------------------------ #
        # "File" label + parent's widget_input_file
        # ------------------------------------------------------------------------------------------------------------ #

        # Wrapper widget for the file information
        widget_filename = QWidget()

        # Layout of the file information widget
        layout_filename = QHBoxLayout()

        # Set the layout to the file information widget
        widget_filename.setLayout(layout_filename)

        # Add the file input widget coming from the parent widget
        layout_filename.addWidget(parent.widget_input_file)

        # Add the complete file-selection row to our main layout
        self.layout.addWidget(widget_filename)

        # ------------------------------------------------------------------------------------------------------------ #
        # Table view for file content / preview
        # ------------------------------------------------------------------------------------------------------------ #
        self.widget_table_data = QTableView()

        # Minimum height ensure the table is large enough to be readable
        self.widget_table_data.setMinimumHeight(500)

        # Minimum width ensure the table is large enough to be readable
        self.widget_table_data.setMinimumWidth(800)

        # Make the last column expand to fill available space
        self.widget_table_data.horizontalHeader().setStretchLastSection(True)

        # Automatically resize columns to fit their content
        self.widget_table_data.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Add the table widget to the layout
        self.layout.addWidget(self.widget_table_data)

        # Add stretch to push elements upward and give spacing at the bottom
        self.layout.addStretch()