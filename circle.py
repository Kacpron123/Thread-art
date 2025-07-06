import logging
import math

logger = logging.getLogger(__name__)


class Circle:
    def __init__(self, canvas, get_image_rect):
        """
        Initialize the circle drawn on the image using two points that define its diameter.
        """
        self.canvas = canvas
        self.get_image_rect = get_image_rect
        self.num_pins = None
        # Two points defining the diameter
        self.diameter_point1_coords = (0, 0)
        self.diameter_point2_coords = (0, 0)
        # for dragging points
        self.active_point_index = -1  # 0 for point1, 1 for point2
        self.start_mouse_x = 0
        self.start_mouse_y = 0
        # these are for smooth dragging
        self.initial_point_x = 0
        self.initial_point_y = 0

    def set_num_pins(self, num_pins):
        self.num_pins = num_pins

    def draw_circle(self):
        """
        Draws the main circle, the diameter line, the two control points (diameter endpoints),
        and the pins around the circumference.
        """
        self.canvas.delete("circle_elements")  # Delete previous circle, points, line, and pins

        # Initialize diameter points if they are at (0,0)
        if self.diameter_point1_coords == (0, 0) or self.diameter_point2_coords == (0, 0):
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            # Set initial points to define a sensible diameter in the center
            self.diameter_point1_coords = (canvas_width * 0.3, canvas_height * 0.5)
            self.diameter_point2_coords = (canvas_width * 0.7, canvas_height * 0.5)

        x1, y1 = self.diameter_point1_coords
        x2, y2 = self.diameter_point2_coords

        # Calculate the circle's center and radius based on the two diameter points
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 2

        # Draw the main circle
        self.canvas.create_oval(center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius,
                                outline="gray", width=1, tags="circle_elements")

        # Draw the diameter line connecting the two control points
        self.canvas.create_line(x1, y1, x2, y2,
                                fill="gray", width=1, tags="circle_elements")

        # Draw the first diameter control point (green dot)
        point_size = 5
        self.canvas.create_oval(x1 - point_size, y1 - point_size,
                                x1 + point_size, y1 + point_size,
                                fill="green", outline="green", tags="circle_elements")

        # Draw the second diameter control point (blue dot)
        self.canvas.create_oval(x2 - point_size, y2 - point_size,
                                x2 + point_size, y2 + point_size,
                                fill="blue", outline="blue", tags="circle_elements")

        # Calculate and draw pins
        self.pin_coords = []
        # Determine a starting angle for pins (e.g., align with diameter line)
        start_angle = math.atan2(y2 - center_y, x2 - center_x)
        if radius > 0 and self.num_pins is not None:
            for i in range(self.num_pins):
                angle = start_angle + 2 * math.pi * i / self.num_pins
                pin_x = center_x + radius * math.cos(angle)
                pin_y = center_y + radius * math.sin(angle)
                self.pin_coords.append((pin_x, pin_y))
                # Draw pin as a small purple circle
                pin_dot_size = 3
                self.canvas.create_oval(pin_x - pin_dot_size, pin_y - pin_dot_size,
                                        pin_x + pin_dot_size, pin_y + pin_dot_size,
                                        fill="purple", outline="gray", tags="circle_elements")
        logger.debug(f"Drew circle with diameter points {self.diameter_point1_coords} and {self.diameter_point2_coords}, radius {radius}, and {self.num_pins} pins.")

    def on_button_press(self, event):
        point_size = 5
        tolerance = 15

        # Check if the click is on the first diameter control point
        dist_to_point1 = math.sqrt((event.x - self.diameter_point1_coords[0])**2 + (event.y - self.diameter_point1_coords[1])**2)
        if dist_to_point1 < point_size + tolerance:
            self.active_point_index = 0  # 0 for diameter_point1
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y
            self.initial_point_x, self.initial_point_y = self.diameter_point1_coords
            logger.debug("Started dragging diameter point 1.")
            return

        # Check if click is near the second diameter control point
        dist_to_point2 = math.sqrt((event.x - self.diameter_point2_coords[0])**2 + (event.y - self.diameter_point2_coords[1])**2)
        if dist_to_point2 < point_size + tolerance:
            self.active_point_index = 1  # 1 for diameter_point2
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y
            self.initial_point_x, self.initial_point_y = self.diameter_point2_coords
            logger.debug("Started dragging diameter point 2.")
            return

    def on_mouse_drag(self, event):
        if self.active_point_index == -1:
            return

        dx = event.x - self.start_mouse_x
        dy = event.y - self.start_mouse_y

        new_x = self.initial_point_x + dx
        new_y = self.initial_point_y + dy

        # Keep points within canvas bounds
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        new_x = max(0, min(new_x, canvas_width))
        new_y = max(0, min(new_y, canvas_height))

        if self.active_point_index == 0:  # Dragging diameter_point1
            self.diameter_point1_coords = (new_x, new_y)
            logger.debug(f"Dragging diameter point 1 to {new_x, new_y}")
        elif self.active_point_index == 1:  # Dragging diameter_point2
            self.diameter_point2_coords = (new_x, new_y)
            logger.debug(f"Dragging diameter point 2 to {new_x, new_y}")

        self.draw_circle()  # Redraw everything with the updated point(s)

    def on_button_release(self, event):
        """
        Handles mouse button release to stop dragging.
        """
        if self.active_point_index != -1:
            logger.debug(f"Stopped dragging point {self.active_point_index}.")
        self.active_point_index = -1  # Reset active point