"""
    This module defines the 'WidgetResult' class, which computes student results based on a pandas DataFrame and displays
    them in a PyQt6 dialog window.

    The computation filters data by expected columns, student selection, and schedule ranges, then calculates averages
    and displays them in a grid layout.
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
from PyQt6.QtWidgets import QWidget, QDialog, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtGui     import QFont
from pandas          import DataFrame, concat

# ==================================================================================================================== #
# PROJECT LIBRARIES
# ==================================================================================================================== #
from lib.parameters import EXPECTED_COLUMNS
from lib.supervisor import supervisor


class WidgetResult(QWidget):
    """
        A QWidget subclass that computes and displays student results in a PyQt6 dialog.

        Attributes:
            data (DataFrame): The pandas DataFrame containing student results.
            dialog (QDialog): The PyQt6 dialog window to display the results.
            dialog_layout (QHBoxLayout): Layout manager for the dialog.
            widget_result (QWidget): The QWidget containing the grid of results.
            layout_result (QGridLayout): Grid layout for organizing result labels.
    """
    def __init__(self, parent=None):
        """
            Initialize the WidgetResult.

            :param parent: Parent widget containing the data [optional].
        """
        super().__init__(parent)

        # Create a dialog window to display results
        self.dialog = QDialog()

        # Set the dialog title
        self.dialog.setWindowTitle("Result")

        # Set a horizontal layout for the dialog
        self.dialog_layout = QHBoxLayout()

        # Apply the layout to the dialog window
        self.dialog.setLayout(self.dialog_layout)

        # Create a QWidget to hold the grid of results
        self.widget_result = QWidget()

        # Grid layout for results
        self.layout_result = QGridLayout()

        # Apply the grid layout to the widget
        self.widget_result.setLayout(self.layout_result)

        # Column headers for the result grid
        list_header = ["STUDENT", "MAX.", "NOTES"]

        # Add headers to the first row of the grid
        for h, header in enumerate(list_header):

            # Create a QLabel for the header
            header_student = QLabel(header)

            # Bold font for headers
            header_student.setFont(QFont('Arial', 10, QFont.Weight.Bold))

            # Place header in grid (row 0)
            self.layout_result.addWidget(header_student, 0, h)

    @supervisor
    def compute(self):
        """
            Compute and display student results filtered by selection and schedule.

            This method:
                - Validates the DataFrame and expected columns.
                - Groups data by student name.
                - Filters by student selection and schedule ranges.
                - Calculates max scores and individual notes.
                - Populates the result grid and shows the dialog.
        """
        # Validate that 'parent.data' is a DataFrame
        if type(self.parent().data) != DataFrame:

            # Raise an error since there is no data
            raise ValueError("There is no data to compute")

        # Check that all expected columns exist in the DataFrame
        if not set(EXPECTED_COLUMNS).issubset(self.parent().data.columns.to_list()):

            # Store missing columns
            missing_columns = set(EXPECTED_COLUMNS).difference(self.parent().data.columns.to_list())

            # Raise an error that shows missing column in the CSV
            raise ValueError(f"Missing column name {missing_columns}")

        # Group the DataFrame by student last name and first name
        student = self.parent().data.groupby(['Nom de famille', 'Prénom'])

        # Row counter for grid layout (start after header row)
        cpt = 1

        # Loop over students
        for name, group in student:

            # Combine last and first name
            full_name = f"{name[0]} {name[1]}"

            # Check if student is selected in the parent widget filter
            if full_name in self.parent().widget_query.widget_student_filter.checked_items():

                # Filter rows with status 'Terminée'
                row_first_checked = group.query("Statut == 'Terminée'")

                # Get schedule ranges from JSON schedule widget
                schedule_data = self.parent().widget_query.widget_json_schedule.get_data()

                # Empty DataFrame with same columns
                df = DataFrame(columns=row_first_checked.columns)

                # Filter rows by schedule start and end times
                for start, end in schedule_data:
                    df = concat([df, row_first_checked[(row_first_checked['Commencé'] >= start) &
                                                       (row_first_checked['Terminé'] <= end)]])

                # Set QLabel with student name
                widget = QLabel(full_name)

                # Add student name to the first column
                self.layout_result.addWidget(widget, cpt, 0)

                # Set QLabel max score for the student
                widget = QLabel(f"{df['Note/20,00'].max():.2f}" if df['Note/20,00'].max() > 0 else '')

                # Add max score to the second column
                self.layout_result.addWidget(widget, cpt, 1)

                # Set QLabel with all individual notes or empty if no notes for the student
                widget = QLabel(f"{', '.join([f'{values:.2f}' for values in df['Note/20,00'].values])
                                   if df['Note/20,00'].values.size
                                   else ''}")

                # Add all individual notes in the third column
                self.layout_result.addWidget(widget, cpt, 2)

                # Move to the next row in the grid
                cpt += 1

        # Add the result grid widget to the dialog layout
        self.dialog_layout.addWidget(self.widget_result)

        # Show the dialog window
        self.dialog.exec()
