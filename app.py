# app.py
import tkinter as tk
from tkinter import Scale, HORIZONTAL
import sys
import logging
import image

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

        # Canvas (inside left_frame)
        self.canvas = tk.Canvas(self.left_frame, bg="lightgray", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=0, pady=10) # Removed horizontal padding here as it's on left_frame

        # Control frame (inside left_frame)
        self.control_frame = tk.Frame(self.left_frame, bd=2, relief=tk.RAISED, padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        # Right frame for console output
        self.console_frame = tk.Frame(self.main_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10, pady=10) # expand=False to keep its width fixed

        self.console_label = tk.Label(self.console_frame, text="Console Output:", font=("Arial", 10, "bold"))
        self.console_label.pack(side=tk.TOP, pady=(0, 5))

        self.console_text = tk.Text(self.console_frame, wrap=tk.WORD, height=20, width=40,bg="black", fg="lightgray", font=("Consolas", 9))
        self.console_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def write_to_console(message):
            self.console_text.insert(tk.END, message)
            self.console_text.see(tk.END)
        self.console_text.write = write_to_console
        self.image_app = image.AppImage(self.canvas,self.console_text)


        # Button for loading image
        self.load_button = tk.Button(self.control_frame, text="Load Image", command=self.image_app.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Slider for Number of Pins
        self.pins_label = tk.Label(self.control_frame, text="Number of Pins:")
        self.pins_label.pack(side=tk.LEFT, padx=(15, 2), pady=5)

        self.pins_slider = Scale(self.control_frame, from_=10, to=120, orient=HORIZONTAL,length=200, resolution=1, command=self.update_num_pins)
        self.pins_slider.set(self.num_pins) # Set initial value
        self.pins_slider.pack(side=tk.LEFT, padx=5, pady=5)

        # Button for calculating thread art
        self.calculate_thread_art_button = tk.Button(self.control_frame, text="Calculate Thread Art", command=self.calculate_thread_art)
        self.calculate_thread_art_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Store original stdout for restoration, but do NOT redirect here anymore
        self.original_stdout = sys.stdout

        # Print welcome message to console
        logger.info("app started")
        write_to_console("Welcome to Circle Thread Art Maker!\n")

    def update_num_pins(self, value):
        """
        Callback function for the pins slider. Updates self.num_pins and logs to console.
        """
        self.num_pins = int(value)
        self.image_app.set_circle_num_pins(self.num_pins)
        logger.debug(f"Number of Pins updated to: {self.num_pins}")


    def calculate_thread_art(self):
        """calculating thread art"""
        prepared_image = self.image_app.prepare_image_for_calculation()
        if not prepared_image:
            self.console_text.write("No image to calculate. Please load an image first.\n")
            logger.warning("Calculation skipped: No image prepared.")
            return
        
        if prepared_image.mode != "L":
            prepared_image = prepared_image.convert("L")

        prepared_image.save("thread_art.jpg")
        logger.info("Thread art saved to thread_art.jpg")
        self.console_text.write("Thread art saved to thread_art.png\n")