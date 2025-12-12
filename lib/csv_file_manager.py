"""
    This module provides:
        - 'PandasModel' class: a Qt table model wrapper for a pandas DataFrame
        - 'open_csv' method: open a CSV file via a file dialog and load it into the application
        - 'load_data' method: load and preprocess data from the CSV file selected in the GUI
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
from os              import environ, getcwd
from pandas          import DataFrame, read_csv, to_datetime
from PyQt6.QtCore    import Qt, QAbstractTableModel, pyqtSignal, QVariant, QModelIndex
from PyQt6.QtWidgets import QFileDialog, QWidget
from typing          import Any

# ==================================================================================================================== #
# PROJECT LIBRARIES
# ==================================================================================================================== #
from lib.parameters  import EXPECTED_COLUMNS
from lib.supervisor  import supervisor

# ==================================================================================================================== #
# CLASS PandasModel
# ==================================================================================================================== #
class PandasModel(QAbstractTableModel):
    """
        A Qt table model wrapper for a pandas DataFrame.

        This class allows a DataFrame to be displayed and edited inside Qt's model/view framework.

        Signals
        -------
        dataFrameUpdated : pyqtSignal(DataFrame)
            Emitted whenever the DataFrame is replaced through updateDataFrame().
    """
    # Signal emitted when the entire DataFrame is updated
    dataFrameUpdated = pyqtSignal(DataFrame)

    def __init__(self, data: DataFrame, header: list[str], parent=None) -> None:
        """
            Initialize the model.

            :param data: the pandas DataFrame to expose in the model
            :param header: list of column headers (column names)
            :param parent: parent Qt object [optional]
        """
        super().__init__(parent)

        # Internal DataFrame storage
        self._data = data

        # Column headers for display
        self._header = header

    def rowCount(self, parent=None) -> int:
        """
            Return the number of rows in the DataFrame.
        """
        return len(self._data.values)

    def columnCount(self, parent=None) -> int:
        """
            Return the number of columns in the DataFrame.
        """
        return self._data.columns.size

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> QVariant:
        """
            Return the data to display in a given cell.

            :param index: position of the data cell
            :param role: requested data role (DisplayRole, EditRole, etc.)
            :return: the value displayed in the table.
        """
        if index.isValid():

            if role == Qt.ItemDataRole.DisplayRole:

                # Convert cell value to string for display
                return QVariant(str(self._data.iloc[index.row(), index.column()]))

        # Default empty value
        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role=Qt.ItemDataRole.EditRole) -> bool:
        """
            Handle edits made in the view and update the DataFrame.

            :param index: the index of the edited cell
            :param value: new value entered by the user
            :param role: the item role (EditRole when editing)
            :return: true if the data was successfully updated.
        """
        if role == Qt.ItemDataRole.EditRole:

            # Update the DataFrame at the given row/column
            self._data.iloc[index.row()][index.column()] = value

            # 🔥 Emit signal to notify the view (and connected slots)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

            return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> QVariant | str:
        """
            Return the text for horizontal or vertical headers.

            :param section: index of the row/column
            :param orientation: horizontal for columns, vertical for rows
            :param role: display role for rendering
            :return: QVariant or str
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:

            # Display custom headers for columns
            return '{}'.format(self._header[section])

        # Fallback to default
        return super().headerData(section, orientation, role)

    # ================================================================================================================ #
    # Convenience methods
    # ================================================================================================================ #
    def getDataFrame(self) -> DataFrame:
        """
            Return a *copy* of the current DataFrame.

            :return: DataFrame
        """
        return self._data.copy()

    def updateDataFrame(self, new_df: DataFrame):
        """
            Replace the model's DataFrame with a new one.

            Emits `dataFrameUpdated` after resetting the model.

            Ensures the view refreshes all its contents.

            :param new_df: the updated DataFrame
        """
        # Notify views that the model will change
        self.beginResetModel()

        # Replace the underlying DataFrame
        self._data = new_df.copy()

        # Notify that reset is finished
        self.endResetModel()

        # Emit updated DataFrame
        self.dataFrameUpdated.emit(self._data.copy())


# ==================================================================================================================== #
# FUNCTIONS
# ==================================================================================================================== #
@supervisor
def open_csv(parent: QWidget | None = None) -> None:
    """
        Open a CSV file via a file dialog and load it into the application.

        :param parent: the parent widget that owns the file dialog and provides 'widget_input_file' (QLineEdit)
    """
    # Determine a safe starting directory: HOMEPATH may not exist on all systems (e.g., Linux, macOS), so we fall back
    # to the current working directory.
    start_dir = environ.get('HOMEPATH', getcwd())

    # Open a file dialog for CSV files.
    filename, _ = QFileDialog.getOpenFileName(parent=parent,
                                              caption="Open",
                                              directory=start_dir,
                                              filter="CSV Files (*.csv)")

    # If the user cancels the dialog, `filename` will be an empty string.
    if not filename:
        return

    # Ensure the file is a CSV (case-insensitive check).
    if not filename.lower().endswith('.csv'):
        raise ValueError(f"Unsupported file type: {filename}")

    # Update the GUI with the chosen filename
    parent.widget_input_file.setText(f"File: {filename}")

    # Call load_data function
    load_data(parent=parent)


@supervisor
def load_data(parent=None) -> None:
    """
        Load and preprocess data from the CSV file selected in the GUI.

        :param parent: the parent widget that manages the UI
    """
    # Load CSV data into DataFrame
    parent.data = read_csv(parent.widget_input_file.text())

    # Validate required columns in the CSV
    #   - get the items difference between the two lists
    missing_cols = set(EXPECTED_COLUMNS).difference(parent.data.columns.to_list())

    #   - if there is at least a missing column
    if missing_cols:

        # Raise an error
        raise ValueError(f"Missing required column(s): {missing_cols}")

    # Data type conversions:
    #   - convert date columns using the expected French date format
    parent.data['Commencé'] = to_datetime(parent.data['Commencé'], format='%d %B %Y %X', errors='raise')

    parent.data['Terminé'] = to_datetime(parent.data['Terminé'], format='%d %B %Y %X', errors='raise')

    #   - Convert "Note/20,00" column: convert "xx,yy" → float(xx.yy)
    parent.data['Note/20,00'] = parent.data['Note/20,00'].apply(lambda x: float(x.replace(',', '.')))

    # Reorder columns
    #   - list of target columns
    list_col = ['Statut', 'Commencé', 'Terminé', 'Note/20,00']

    #   - list of indexes to insert each
    list_idx = [2, 3, 4, 5]

    #   - loop to reorder the DataFrame
    for col, idx in zip(list_col, list_idx):

        # remove the col
        removed_col = parent.data.pop(col)

        # insert the removed col at the new idx
        parent.data.insert(idx, col, removed_col)

    # Update model data
    parent.model = PandasModel(parent.data, header=parent.data.columns.to_list())

    # Set the model to the WidgetFileContent.widget_table_data widget in order to display
    parent.widget_plot_info.widget_table_data.setModel(parent.model)

    # Clear the student filter widget in order to update it
    parent.widget_query.widget_student_filter.clear()

    # Update the student filter widget by last name + first name to get distinct students
    for name, _ in parent.data.groupby(['Nom de famille', 'Prénom']):
        parent.widget_query.widget_student_filter.add_checkable_item(text=f"{name[0]} {name[1]}", checked=True)
