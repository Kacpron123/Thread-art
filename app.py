# app.py
import tkinter as tk
from tkinter import Scale, HORIZONTAL
import sys
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)


class CircleThreadArtApp:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("Circle Thread Art Maker")
        self.root.geometry("1200x700") # Increased width to accommodate the new panel

        # Initialize instance variables
        self.num_pins = 30 # Default value for the number of pins
        # Main frame to hold controls, canvas, and console panel
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for controls and canvas
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control frame (inside left_frame)
        self.control_frame = tk.Frame(self.left_frame, bd=2, relief=tk.RAISED, padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.load_button = tk.Button(self.control_frame, text="Load Image", )
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Slider for Number of Pins
        self.pins_label = tk.Label(self.control_frame, text="Number of Pins:")
        self.pins_label.pack(side=tk.LEFT, padx=(15, 2), pady=5)

        self.pins_slider = Scale(self.control_frame, from_=10, to=80, orient=HORIZONTAL,
                                 length=200, resolution=2, command=self.update_num_pins)
        self.pins_slider.set(self.num_pins) # Set initial value
        self.pins_slider.pack(side=tk.LEFT, padx=5, pady=5)

        # Button for calculating thread art
        self.calculate_thread_art_button = tk.Button(self.control_frame, text="Calculate Thread Art", )
        self.calculate_thread_art_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Canvas (inside left_frame)
        self.canvas = tk.Canvas(self.left_frame, bg="lightgray", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=10) # Removed horizontal padding here as it's on left_frame

        # Right frame for console output
        self.console_frame = tk.Frame(self.main_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10, pady=10) # expand=False to keep its width fixed

        self.console_label = tk.Label(self.console_frame, text="Console Output:", font=("Arial", 10, "bold"))
        self.console_label.pack(side=tk.TOP, pady=(0, 5))

        self.console_text = tk.Text(self.console_frame, wrap=tk.WORD, height=20, width=40,
                                    bg="black", fg="lightgray", font=("Consolas", 9))
        self.console_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Store original stdout for restoration, but do NOT redirect here anymore
        self.original_stdout = sys.stdout

        # Bind mouse events for dragging points
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Use logger for welcome message
        # Print welcome message to console
        self.console_text.insert(tk.END, "Welcome to Circle Thread Art Maker!\n")
        self.console_text.insert(tk.END, "Load an image, define a circle, and click 'Calculate Thread Art'.\n")

    def __del__(self):
        """
        No longer responsible for restoring sys.stdout, as main.py handles it.
        """
        pass # sys.stdout restoration is handled in main.py

    def update_num_pins(self, value):
        """
        Callback function for the pins slider. Updates self.num_pins and logs to console.
        """
        self.num_pins = int(value)
        logger.debug(f"Number of Pins updated to: {self.num_pins}")

    def display_image_on_canvas(self):
        pass

    def on_canvas_resize(self, event):
        """Handles canvas resizing to redraw the image and elements."""
        logger.debug(f"Canvas resized to {event.width}x{event.height}")

    def on_button_press(self, event):
        """Handles mouse button press to start dragging an existing point."""
        pass

    def on_mouse_drag(self, event):
        """Handles mouse drag events to move points."""
        pass

    def on_button_release(self, event):
        """Handles mouse button release to stop dragging."""
        pass
