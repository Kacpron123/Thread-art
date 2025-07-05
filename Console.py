# Console.py
import io
import sys
import tkinter as tk

class Console(io.StringIO):
    """
    A custom StringIO object to redirect stdout to a Tkinter Text widget.
    """

    def write(self, s):
        """
        Writes the string 's' to the Text widget and ensures it's visible.
        """
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END) # Scroll to the end to show new output
        # Also call original write to keep output in console for debugging
        sys.__stdout__.write(s)

    def flush(self):
        """
        Flushes the buffer (required for sys.stdout redirection).
        """
        sys.__stdout__.flush() # Flush original stdout as well    
    def __exit__(self, *args):
        sys.stdout = sys.__stdout__
