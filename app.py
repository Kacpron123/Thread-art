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
        self.calculate_thread_art_button = tk.Button(self.control_frame, text="Calculate Thread Art", )
        self.calculate_thread_art_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Store original stdout for restoration, but do NOT redirect here anymore
        self.original_stdout = sys.stdout

        # Bind mouse events for dragging points
        self.canvas.bind("<Button-1>", self.image_app.circle.on_button_press)
        self.canvas.bind("<B1-Motion>", self.image_app.circle.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.image_app.circle.on_button_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # temp=circle.Circle(self.canvas)
        # temp.draw_circle()
        # Print welcome message to console
        logger.info("app started")
        write_to_console("Welcome to Circle Thread Art Maker!\n")

    def update_num_pins(self, value):
        """
        Callback function for the pins slider. Updates self.num_pins and logs to console.
        """
        x=self.num_pins = int(value)
        self.image_app.set_circle_num_pins(x)
        logger.debug(f"Number of Pins updated to: {self.num_pins}")

    def on_canvas_resize(self, event):
        """Handles canvas resizing to redraw the image and elements."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.image_app.resize_image(canvas_width, canvas_height)
        logger.debug(f"Canvas resized to {canvas_width}x{canvas_height}")

    def on_button_press(self, event):
        # """Handles mouse button press to start dragging an existing point."""
        # point_size = 5
        # tolerance = 10
        
        # # Check if the click is on the center control point
        # dist_to_center_control = math.sqrt((event.x - self.points[0][0])**2 + (event.y - self.points[0][1])**2)
        # if dist_to_center_control < point_size + tolerance:
        #     self.active_point_index = 0 # 0 for center point
        #     self.start_mouse_x = event.x
        #     self.start_mouse_y = event.y
        #     self.initial_point_x, self.initial_point_y = self.points[0]
        #     logger.debug("Started dragging center control point.")
        #     return
        
        # # Check if click is near the radius control point
        # dist_to_radius_control = math.sqrt((event.x - self.points[1][0])**2 + (event.y - self.points[1][1])**2)
        # if dist_to_radius_control < point_size + tolerance:
        #     self.active_point_index = 1 # 1 for radius point
        #     self.start_mouse_x = event.x
        #     self.start_mouse_y = event.y
        #     self.initial_point_x, self.initial_point_y = self.points[1]
        #     logger.debug("Started dragging radius control point.")
        #     return
        # # logger.debug("No point was clicked.")
        # self.active_point_
        # index = -1 # No point was clicked
        pass

    def on_mouse_drag(self, event):
    #     """Handles mouse drag events to move the active control point."""
    #     if self.active_point_index == -1:
    #         return

    #     dx = event.x - self.start_mouse_x
    #     dy = event.y - self.start_mouse_y

    #     new_x = self.initial_point_x + dx
    #     new_y = self.initial_point_y + dy

    #     # Keep points within canvas bounds
    #     canvas_width = self.canvas.winfo_width()
    #     canvas_height = self.canvas.winfo_height()
    #     new_x = max(0, min(new_x, canvas_width))
    #     new_y = max(0, min(new_y, canvas_height))

    #     if self.active_point_index == 0: # Dragging center point
    #         self.points[0] = (new_x, new_y)
    #         logger.debug(f"Dragging center point to {new_x, new_y}")
    #     elif self.active_point_index == 1: # Dragging radius point
    #         self.points[1] = (new_x, new_y)
    #         logger.debug(f"Dragging radius point to {new_x, new_y}")

    #     self.draw_circle() # Redraw everything with the updated point(s)
        pass
    def on_button_release(self, event):
    #     """Handles mouse button release to stop dragging."""
    #     if self.active_point_index != -1:
    #         logger.debug(f"Stopped dragging point {self.active_point_index}.")
    #     self.active_point_index = -1 # Reset active point        # Coordinates for the two draggable control points (center and radius)
    #     # These will be initialized based on canvas size in on_canvas_resize
    #     self.center_point_coords = (0, 0)
    #     self.radius_point_coords = (0, 0)

    #     # Variable to track which point is being dragged: -1 (none), 0 (center), 1 (radius)
    #     self.active_point_index = -1
    #     self.start_mouse_x = 0
    #     self.start_mouse_y = 0
    #     self.initial_point_x = 0
    #     self.initial_point_y = 0
        pass