# image.py
import math
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import logging

import circle

# Get a logger for this module
logger = logging.getLogger(__name__)


class AppImage:
    def __init__(self,canvas,console):
        self.canvas = canvas
        self._original_image = None # Store the full-res original image
        self._displayed_image = None # Store the currently scaled ImageTk.PhotoImage for display
        self._pil_image_for_display = None # Store the PIL Image object that is currently displayed (scaled)
        self._path = None
        #image offset on canvas
        self.offset_x = 0
        self.offset_y = 0

        # Changed: Pass a callback to Circle so it can get image display info
        self.circle = circle.Circle(canvas, self.get_current_image_display_info_callback)
        self.console = console

        # Changed: Debouncing variables
        self._resize_job = None
        self._resize_delay_ms = 50 # milliseconds

        # Changed: Bind canvas resize event to the debounced handler
        self.canvas.bind("<Configure>", self.on_canvas_resize_debounced)

    # Changed: New callback method for Circle class
    def get_current_image_display_info_callback(self):
        """
        Callback for the Circle class to get current image display information.
        Returns (x_offset, y_offset, display_width, display_height, original_width, original_height).
        """
        if self._pil_image_for_display and self._original_image:
            return (self.offset_x, self.offset_y,
                    self._pil_image_for_display.width, self._pil_image_for_display.height,
                    self._original_image.width, self._original_image.height)
        return (0, 0, 0, 0, 0, 0) # Default values if no image is loaded


    # Changed: Debounced handler for canvas resize events
    def on_canvas_resize_debounced(self, event):
        """
        Debounced handler for canvas resize events.
        It schedules the actual resize and redraw to happen after a short delay,
        and cancels any previous scheduled events.
        """
        if self._resize_job:
            self.canvas.after_cancel(self._resize_job)
        self._resize_job = self.canvas.after(self._resize_delay_ms, self._perform_resize_and_redraw)

    # Changed: New method for performing the debounced resize and redraw
    def _perform_resize_and_redraw(self):
        """
        The actual resize and redraw logic, called after the debounce delay.
        """
        if self._original_image:
            logger.debug("Performing debounced resize and redraw.")
            self._resize_and_display_image(self._original_image.size[0], self._original_image.size[1])
            self.draw_image()
            self.circle.reset_default_diameter_points_if_needed() # New method in Circle
        self._resize_job = None # Clear the job ID


    def load_image(self):
        """
        Loads an image into the canvas.
        """
        file_path = filedialog.askopenfilename()
        if not file_path:
            logger.info("No image selected")
            return
        
        # Changed: Check if the file path is the same AND image is already loaded (not just path)
        if self._path == file_path and self._original_image:
            logger.info("Image already loaded")
            self.console.write("Image already loaded.\n") # Changed: Add console message
            return
        
        # Changed: Ensure _original_image is set to None on error for robust state management
        try:
            self._original_image = Image.open(file_path)
            if self._original_image.mode != "RGBA":
                self._original_image = self._original_image.convert("RGBA")
        except Exception as e:
            self.console.write("Error loading image\n")
            logger.error(f"Error loading image: {e}")
            self._original_image = None # Changed: Set to None on error
            return
        
        # Changed: Update 'changed' flag based on actual path change
        changed = (self._path is None) or (self._path != file_path)
        self._path = file_path
        
        self.canvas.delete("all")
        self._resize_and_display_image(self._original_image.size[0], self._original_image.size[1])
        # Changed: Reset circle points to default only after image is loaded and displayed
        self.circle.reset_default_diameter_points() # This method will initialize based on image
        self.draw_image()

        if changed:
            logger.info(f"Image loaded from {file_path}")
            self.console.write("Image loaded successfully.\n")
        else:
            logger.info(f"Image changed to {file_path}")
            self.console.write("Image changed successfully.\n")

    def _resize_and_display_image(self, img_width, img_height):
        """
        Internal method to resize and display the image, setting self._pil_image_for_display.
        """
        if not self._original_image:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Changed: Added explicit checks for non-positive canvas dimensions
        if canvas_height <= 0 or canvas_width <= 0:
            logger.warning("Canvas dimensions are zero or negative, skipping image resize.") # Changed: Added log
            return
        
        # Changed: More robust aspect ratio calculation
        img_aspect = img_width / img_height
        canvas_aspect = canvas_width / canvas_height

        if img_aspect > canvas_aspect: # Image is wider than canvas ratio, scale by width
            new_width = canvas_width
            new_height = int(canvas_width / img_aspect)
        else: # Image is taller or same ratio, scale by height
            new_height = canvas_height
            new_width = int(canvas_height * img_aspect)

        # Changed: Added check for too small dimensions to prevent issues
        min_dim = 10 # or some other reasonable minimum
        if new_width < min_dim or new_height < min_dim:
            logger.debug(f"Calculated new dimensions ({new_width}x{new_height}) too small, skipping resize.") # Changed: Added log
            self._pil_image_for_display = None # Changed: Clear image if too small
            self._displayed_image = None
            return
        
        # Changed: Add try-except for image resizing
        try:
            self._pil_image_for_display = self._original_image.resize((new_width, new_height), Image.BICUBIC)
            self._displayed_image = ImageTk.PhotoImage(self._pil_image_for_display)

            # calculate offset
            self.offset_x = (canvas_width - new_width) // 2
            self.offset_y = (canvas_height - new_height) // 2
            logger.debug(f"Resized image for display to {new_width}x{new_height} with offset ({self.offset_x},{self.offset_y}).") # Changed: Added log
        except Exception as e: # Changed: Catch exceptions during resize
            logger.error(f"Error resizing image for display: {e}")
            self._pil_image_for_display = None
            self._displayed_image = None


    def draw_image(self):
        """
        Draws the loaded image on the canvas.
        """
        self.canvas.delete("image_elements")
        if self._displayed_image:
            self.canvas.create_image(self.offset_x, self.offset_y, image=self._displayed_image, anchor=tk.NW, tags="image_elements")
        self.circle.draw_circle()       
            
    def set_circle_num_pins(self, num_pins):
        """sets the number of pins on the circle"""
        self.circle.set_num_pins(num_pins)
        self.circle.draw_circle()

    def prepare_image_for_calculation(self):
        # Changed: Use _original_image for calculations
        if not self._original_image:
            logger.warning("No original image loaded for calculation.") # Changed: More specific log
            return None # Changed: Return None if no image

        logger.debug("Preparing image for calculation")
        # Changed: Use circle's original image coordinates
        x1_orig, y1_orig = self.circle.diameter_point1_orig_image_coords
        x2_orig, y2_orig = self.circle.diameter_point2_orig_image_coords
        
        center_x_orig = (x1_orig + x2_orig) / 2
        center_y_orig = (y1_orig + y2_orig) / 2
        radius_orig = math.sqrt((x2_orig - x1_orig)**2 + (y2_orig - y1_orig)**2) / 2
        
        # cut out the circle from the image
        mask = Image.new('L', self._original_image.size, 0)
        draw = ImageDraw.Draw(mask)
        # Changed: Use original image coordinates for ellipse
        draw.ellipse((center_x_orig-radius_orig, center_y_orig-radius_orig, center_x_orig+radius_orig, center_y_orig+radius_orig), fill=255)
        
        # apply mask
        background_color_rgb=Image.new("RGB", self._original_image.size, (0,0,0))
        image_rgb_with_black_corners=Image.composite(self._original_image.convert("RGB"),background_color_rgb,mask)
        cut_image=image_rgb_with_black_corners.convert("RGBA")
        cut_image.putalpha(mask)
        # Cut out the square from the image, circumscribing the circle
        square_size_orig = 2*radius_orig # Changed: Use original image radius
        # Changed: Use original image coordinates for crop bounds
        left = max(0, int(center_x_orig - square_size_orig / 2))
        top = max(0, int(center_y_orig - square_size_orig / 2))
        right = min(self._original_image.width, int(center_x_orig + square_size_orig / 2))
        bottom = min(self._original_image.height, int(center_y_orig + square_size_orig / 2))

        # Changed: Ensure crop coordinates are valid
        if left >= right: right = left + 1
        if top >= bottom: bottom = top + 1

        # Changed: Crop the already masked image
        cut_image = cut_image.crop((left, top, right, bottom))
        logger.info("Image prepared for calculation")
        return cut_image

def load_image_data(file_path):
    try:
        image = Image.open(file_path)
        return image
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        return None