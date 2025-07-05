# image.py
import tkinter as tk
from PIL import Image, ImageTk
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)


class AppImage:
    def __init__(self,canvas):
        self.canvas = canvas
        self._image = None
        self._path = None

    def set_image(self, image):
        if image:
            # Resize the image while maintaining aspect ratio
            img_width, img_height = image.size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width > 0 and canvas_height > 0: # Check for valid canvas size
                ratio = min(canvas_width / img_width, canvas_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                logger.debug(f"Resizing image to {new_width}x{new_height}")
                self._image = image.resize((new_width, new_height))
                self.canvas.image = ImageTk.PhotoImage(self._image)
                # Center the image
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                self.canvas.create_image(x_offset, y_offset, image=self.canvas.image, anchor=tk.NW)
            else:
                logger.warning("Canvas width or height is not valid. Skipping image display.")

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