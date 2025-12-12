"""
    This module provides the `supervisor` decorator, which wraps functions in a try/except block and displays a critical
    QMessageBox if an exception occurs.

    It is primarily intended to be used on GUI callback functions to prevent the application from crashing and to show
    a readable traceback to the user.
"""
# ==================================================================================================================== #
# PYTHON LIBRARIES
# ==================================================================================================================== #
from functools       import wraps
from PyQt6.QtWidgets import QMessageBox
from traceback       import format_exc
from typing          import Callable

# ==================================================================================================================== #
# MAIN
# ==================================================================================================================== #
def supervisor(func: Callable)  -> Callable:
    """
        Decorator that wraps a function in a try/except block and shows a QMessageBox with the full traceback if an
        exception occurs.

        This decorator is useful for GUI applications where exceptions in signal/slot handlers can otherwise fail
        silently or crash the program.

        The original function's metadata (name, docstring, etc.) is preserved using functools.wraps().

        :param func: the function to wrap.

        :return: a wrapped version of the function that catches exceptions and reports them through a critical error
                 message box.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
            Execute the decorated function and handle any exceptions. If an exception is raised, a QMessageBox is
            displayed showing the full traceback to help with debugging.


            :return: the return value of the wrapped function, if it executes successfully. If an exception occurs, no
                     value is returned.
        """
        try:
            # Execute the original function normally
            return func(*args, **kwargs)

        except Exception:
            # If any exception occurs, display it in a critical message box
            QMessageBox().critical(None, "Error", f"{format_exc()}")

    return wrapper
