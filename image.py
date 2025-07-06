# image.py
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import logging

import circle

# Get a logger for this module
logger = logging.getLogger(__name__)


class AppImage:
    def __init__(self,canvas,console):
        self.canvas = canvas
        self._image = None
        self._path = None
        self.circle = circle.Circle(canvas,console)
        self.console = console

    def load_image(self):
        """
        Loads an image into the canvas.
        """
        self.canvas.delete("all")
        file_path = filedialog.askopenfilename()
        if self._path == file_path:
            logger.info("Image already loaded")
            return
        
        # Resize the image while maintaining aspect ratio\
        try:
            self._image = Image.open(file_path)
        except Exception as e:
            self.console.write("Error loading image\n")
            logger.error(f"Error loading image: {e}")
            return
        img_width, img_height = self._image.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width > 0 and canvas_height > 0: # Check for valid canvas size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            logger.debug(f"Resizing image to {new_width}x{new_height}")
            self._image = self._image.resize((new_width, new_height))

        changed = self._path is None
        self._path = file_path
        self.draw_image()
        
        if changed:
            logger.info(f"Image loaded from {file_path}")
            self.console.write("Image loaded successfully.\n")
        else:
            logger.info(f"Image changed to {file_path}")
            self.console.write("Image changed successfully.\n")


    def draw_image(self):
        """
        Draws the loaded image on the canvas.
        """
        
        if self._image:
            self.canvas.image = ImageTk.PhotoImage(self._image)
            # Center the image
            x_offset = (self.canvas.winfo_width() - self._image.width) // 2
            y_offset = (self.canvas.winfo_height() - self._image.height) // 2
            self.canvas.create_image(x_offset, y_offset, image=self.canvas.image, anchor=tk.NW)
        self.circle.draw_circle()       
        
    def set_circle_num_pins(self, num_pins):
        self.circle.set_num_pins(num_pins)
        if self._image:
            self.circle.draw_circle()

    def resize_image(self, new_width, new_height):
        if self._image:
            logger.debug(f"Resizing image to {new_width}x{new_height}")
            ratio = min(new_width / self._image.width, new_height / self._image.height)
            resized_image = self._image.resize((int(self._image.width * ratio), int(self._image.height * ratio)))
            self.canvas.image = ImageTk.PhotoImage(resized_image)
            # Center the image
            x_offset = (self.canvas.winfo_width() - resized_image.width) // 2
            y_offset = (self.canvas.winfo_height() - resized_image.height) // 2
            self.canvas.create_image(x_offset, y_offset, image=self.canvas.image, anchor=tk.NW)

def load_image_data(file_path):
    try:
        image = Image.open(file_path)
        return image
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        return None