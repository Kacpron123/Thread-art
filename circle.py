import logging
import math
logger = logging.getLogger(__name__)


class Circle:
    """
    Class to represent the circle drawn on the image using two points that define its diameter.
    """
    def __init__(self, canvas, get_image_display_info_callback):
        """
        Initialize the circle drawn on the image using two points that define its diameter.
        """
        self.canvas = canvas
        self.get_image_display_info = get_image_display_info_callback
        self.num_pins = None


        # for dragging points (these are always in CANVAS coordinates)
        self.diameter_point1_orig_image_coords = (0.0, 0.0)
        self.diameter_point2_orig_image_coords = (0.0, 0.0)
        self._user_moved_circle = False
        self.active_point_index = -1  # 0 for point1, 1 for point2
        self.start_mouse_x = 0
        self.start_mouse_y = 0
        # points where the drag started
        self.initial_point_x = 0
        self.initial_point_y = 0
        self._circle1 = {"fill": "plum", "outline": "black", "width": 1}
        self._circle2 = {"fill": "plum", "outline": "black", "width": 1}
        self._other_circles={"fill": "magenta", "width": 1}


        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)


    def set_num_pins(self, num_pins):
        self.num_pins = num_pins

    def reset_default_diameter_points(self):
        """
        Sets default diameter points in *original image coordinates* based on initial canvas proportions.
        This is called *only* when a new image is loaded, to give a sensible initial circle position.
        It also resets the _user_moved_circle flag.
        """
        # Get current display info (including original image dimensions)
        x_offset, y_offset, img_display_width, img_display_height, original_img_width, original_img_height = self.get_image_display_info()

        if original_img_width <= 0 or original_img_height <= 0:
            # Fallback if no original image dimensions available, use canvas dimensions directly
            # and set original_image_coords to match, implying a 1:1 map initially
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            p1_orig_x = canvas_width * 0.3
            p1_orig_y = canvas_height * 0.5
            p2_orig_x = canvas_width * 0.7
            p2_orig_y = canvas_height * 0.5
            logger.warning("No original image dimensions for default circle reset, using canvas dims as fallback.")
        else:
            # Set default diameter points relative to the original image's dimensions
            # Place the default circle roughly in the middle 40% of the image
            p1_orig_x = original_img_width * 0.3
            p1_orig_y = original_img_height * 0.5
            p2_orig_x = original_img_width * 0.7
            p2_orig_y = original_img_height * 0.5
            
        self.diameter_point1_orig_image_coords = (p1_orig_x, p1_orig_y)
        self.diameter_point2_orig_image_coords = (p2_orig_x, p2_orig_y)
        self._user_moved_circle = False # Reset flag when circle is initialized by system
        logger.debug(f"Reset circle to default original image coords: {self.diameter_point1_orig_image_coords}, {self.diameter_point2_orig_image_coords}")

    def reset_default_diameter_points_if_needed(self):
        """
        This method is called on canvas resize.
        It only resets the circle's position if the user hasn't explicitly moved it yet.
        """
        if not self._user_moved_circle:
            self.reset_default_diameter_points()

    def _original_image_to_canvas_coords(self, ox, oy):
        """Converts original image coordinates to current canvas coordinates."""
        x_offset, y_offset, img_display_width, img_display_height, original_img_width, original_img_height = self.get_image_display_info()

        if not (img_display_width > 0 and img_display_height > 0 and original_img_width > 0 and original_img_height > 0):
            # If no image or invalid dimensions, return the original coords as is, or handle gracefully
            return ox, oy

        scale_x = img_display_width / original_img_width
        scale_y = img_display_height / original_img_height

        cx = ox * scale_x + x_offset
        cy = oy * scale_y + y_offset
        return cx, cy

    def _canvas_to_original_image_coords(self, cx, cy):
        """Converts canvas coordinates to original image coordinates."""
        x_offset, y_offset, img_display_width, img_display_height, original_img_width, original_img_height = self.get_image_display_info()

        if not (img_display_width > 0 and img_display_height > 0 and original_img_width > 0 and original_img_height > 0):
            # If no image or invalid dimensions, return canvas coords as is.
            return cx, cy

        scale_x = img_display_width / original_img_width
        scale_y = img_display_height / original_img_height

        if scale_x == 0: scale_x = 1e-9
        if scale_y == 0: scale_y = 1e-9

        ox = (cx - x_offset) / scale_x
        oy = (cy - y_offset) / scale_y
        return ox, oy


    def draw_circle(self):
        """
        Draws the main circle, the diameter line, the two control points (diameter endpoints),
        and the pins around the circumference, all in CANVAS coordinates.
        """
        self.canvas.delete("circle_elements")

        x_offset, y_offset, img_display_width, img_display_height, original_img_width, original_img_height = self.get_image_display_info()

        if not (img_display_width > 0 and img_display_height > 0 and original_img_width > 0 and original_img_height > 0):
            logger.debug("Cannot draw circle: No image displayed or invalid dimensions.")
            return

        x1_canvas, y1_canvas = self._original_image_to_canvas_coords(
            self.diameter_point1_orig_image_coords[0], self.diameter_point1_orig_image_coords[1]
        )
        x2_canvas, y2_canvas = self._original_image_to_canvas_coords(
            self.diameter_point2_orig_image_coords[0], self.diameter_point2_orig_image_coords[1]
        )

        # Calculate the circle's center and radius based on the two diameter points (now in canvas coords)
        center_x_canvas = (x1_canvas + x2_canvas) / 2
        center_y_canvas = (y1_canvas + y2_canvas) / 2
        radius_canvas = math.sqrt((x2_canvas - x1_canvas)**2 + (y2_canvas - y1_canvas)**2) / 2

        # Draw the main circle
        self.canvas.create_oval(center_x_canvas - radius_canvas, center_y_canvas - radius_canvas,
                                center_x_canvas + radius_canvas, center_y_canvas + radius_canvas,
                                outline="gray", width=1, tags="circle_elements")

        # Draw the diameter line connecting the two control points
        self.canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas,
                                fill="gray", width=1, tags="circle_elements")

        # Draw the first diameter control point (green dot)
        point_size = 6
        self.canvas.create_oval(x1_canvas - point_size, y1_canvas - point_size,
                                x1_canvas + point_size, y1_canvas + point_size,
                                **self._circle1, tags="circle_elements")

        # Draw the second diameter control point (blue dot)
        self.canvas.create_oval(x2_canvas - point_size, y2_canvas - point_size,
                                x2_canvas + point_size, y2_canvas + point_size,
                                **self._circle2, tags="circle_elements")

        # Calculate and draw pins
        self.pin_coords = []
        
        if radius_canvas > 0 and self.num_pins is not None:
            if x2_canvas == center_x_canvas and y2_canvas == center_y_canvas:
                start_angle = 0 # Default if radius point is at center (circle collapsed)
            else:
                start_angle = math.atan2(y1_canvas - center_y_canvas, x1_canvas - center_x_canvas)
            tolerance = 3
            for i in range(1,self.num_pins):
                angle = start_angle + 2 * math.pi * i / self.num_pins
                pin_x = center_x_canvas + radius_canvas * math.cos(angle)
                pin_y = center_y_canvas + radius_canvas * math.sin(angle)
                # if wanted ignore drawing pin on moveable point
                # if (pin_x-x2_canvas)**2 + (pin_y-y2_canvas)**2 < tolerance**2:
                #     continue
                self.pin_coords.append((pin_x, pin_y))
                # Draw pin as a small purple circle
                pin_dot_size = 2
                self.canvas.create_oval(pin_x - pin_dot_size, pin_y - pin_dot_size,
                                        pin_x + pin_dot_size, pin_y + pin_dot_size,
                                        self._other_circles, tags="circle_elements")

    def on_button_press(self, event):
        point_size = 5
        tolerance = 15

        x_offset, y_offset, img_display_width, img_display_height, original_img_width, original_img_height = self.get_image_display_info()
        if not (img_display_width > 0 and img_display_height > 0 and original_img_width > 0 and original_img_height > 0):
            return # No image displayed, so no points to drag

        x1_canvas, y1_canvas = self._original_image_to_canvas_coords(
            self.diameter_point1_orig_image_coords[0], self.diameter_point1_orig_image_coords[1]
        )
        x2_canvas, y2_canvas = self._original_image_to_canvas_coords(
            self.diameter_point2_orig_image_coords[0], self.diameter_point2_orig_image_coords[1]
        )

        # Check if the click is on the first diameter control point
        dist_to_point1 = math.sqrt((event.x - x1_canvas)**2 + (event.y - y1_canvas)**2)
        if dist_to_point1 < point_size + tolerance:
            self.active_point_index = 0  # 0 for diameter_point1
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y
        
            self.initial_point_x, self.initial_point_y = x1_canvas, y1_canvas
            self._user_moved_circle = True
            logger.debug("Started dragging diameter point 1.")
            return

        # Check if click is near the second diameter control point
        dist_to_point2 = math.sqrt((event.x - x2_canvas)**2 + (event.y - y2_canvas)**2)
        if dist_to_point2 < point_size + tolerance:
            self.active_point_index = 1  # 1 for diameter_point2
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y

            self.initial_point_x, self.initial_point_y = x2_canvas, y2_canvas
            self._user_moved_circle = True
            logger.debug("Started dragging diameter point 2.")
            return

    def on_mouse_drag(self, event):
        if self.active_point_index == -1:
            return

        dx = event.x - self.start_mouse_x
        dy = event.y - self.start_mouse_y

        new_x_canvas = self.initial_point_x + dx
        new_y_canvas = self.initial_point_y + dy

        x_offset, y_offset, img_display_width, img_display_height, _, _ = self.get_image_display_info()
        
        # Calculate bounds for point *inside* the displayed image region
        clamp_left = x_offset
        clamp_top = y_offset
        clamp_right = x_offset + img_display_width
        clamp_bottom = y_offset + img_display_height

        new_x_canvas = max(clamp_left, min(new_x_canvas, clamp_right))
        new_y_canvas = max(clamp_top, min(new_y_canvas, clamp_bottom))

        new_orig_x, new_orig_y = self._canvas_to_original_image_coords(new_x_canvas, new_y_canvas)

        if self.active_point_index == 0:  # Dragging diameter_point1
            self.diameter_point1_orig_image_coords = (new_orig_x, new_orig_y)
        elif self.active_point_index == 1:  # Dragging diameter_point2
            self.diameter_point2_orig_image_coords = (new_orig_x, new_orig_y)

        self.draw_circle()  # Redraw everything with the updated point(s)

    def on_button_release(self, event):
        """
        Handles mouse button release to stop dragging.
        """
        if self.active_point_index != -1:
            logger.debug(f"Stopped dragging point {self.active_point_index}.")
        self.active_point_index = -1  # Reset active point