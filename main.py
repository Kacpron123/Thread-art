# main.py
import tkinter as tk
from app import CircleThreadArtApp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()
    # Instantiate the CircleThreadArtApp
    app = CircleThreadArtApp(root)
    # Start the Tkinter event loop
    root.mainloop()
    