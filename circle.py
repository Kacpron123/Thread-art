# Circle.py
import logging
import math

logger = logging.getLogger(__name__)


class Circle:
    def __init__(self,canvas,get_image_rect):
        """
        initialize the circle drawn on image
        """
        self.canvas = canvas
        self.get_image_rect = get_image_rect
        self.num_pins = None
        self.center_point_coords = (0,0)
        self.radius_point_coords = (0,0)
        # for dragging points
        self.active_point_index = -1
        self.start_mouse_x = 0
        self.start_mouse_y = 0
        # these are for smooth dragging
        self.initial_point_x = 0
        self.initial_point_y = 0

    def set_num_pins(self,num_pins):
        self.num_pins = num_pins
        
    
    def draw_circle(self):
        """
        Draws the main circle, the two control points (center and radius),
        the line connecting them, and the pins around the circumference.
        """
        self.canvas.delete("circle_elements") # Delete previous circle, points, line, and pins
        if self.center_point_coords == (0,0) or self.radius_point_coords == (0,0):
            cx,cy=self.center_point_coords = self.canvas.winfo_width()//2, self.canvas.winfo_height()//2
            radius = min(cx,cy) * 0.2
            self.radius_point_coords = (cx - radius, cy)
            
        
        cx_control,cy_control=self.center_point_coords
        rx_control, ry_control = self.radius_point_coords
        
        
        # Calculate the actual circle's center and radius based on the control points
        cx = cx_control
        cy = cy_control
        radius = math.sqrt((rx_control - cx)**2 + (ry_control - cy)**2)

        # Draw the main circle
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                outline="gray", width=1, tags="circle_elements")

        # Draw the line connecting center and radius points (dashed)
        self.canvas.create_line(cx_control, cy_control, rx_control, ry_control,
                                fill="gray", width=1, dash=(4, 4), tags="circle_elements")

        # Draw the center control point (green dot)
        point_size = 5
        self.canvas.create_oval(cx_control - point_size, cy_control - point_size,
                                cx_control + point_size, cy_control + point_size,
                                fill="green", outline="green", tags="circle_elements")

        # Draw the radius control point (blue dot)
        self.canvas.create_oval(rx_control - point_size, ry_control - point_size,
                                rx_control + point_size, ry_control + point_size,
                                fill="blue", outline="blue", tags="circle_elements")

        # Calculate and draw pins
        self.pin_coords = []
        start_angle = math.atan2(ry_control - cy, rx_control - cx)
        if radius > 0:
            for i in range(1, self.num_pins):
                angle = start_angle + 2 * math.pi * i / self.num_pins
                pin_x = cx + radius * math.cos(angle)
                pin_y = cy + radius * math.sin(angle)
                self.pin_coords.append((pin_x, pin_y))
                # Draw pin as a small purple circle
                pin_dot_size = 3
                self.canvas.create_oval(pin_x - pin_dot_size, pin_y - pin_dot_size,
                                        pin_x + pin_dot_size, pin_y + pin_dot_size,
                                        fill="purple", outline="purple", tags="circle_elements")
        logger.debug(f"Drew circle with center {cx, cy}, radius {radius}, and {self.num_pins} pins.")


    def on_button_press(self,event):
        point_size = 5
        tolerance = 15

        # Check if the click is on the center control point
        dist_to_center_control = math.sqrt((event.x - self.center_point_coords[0])**2 + (event.y - self.center_point_coords[1])**2)
        if dist_to_center_control < point_size + tolerance:
            self.active_point_index = 0 # 0 for center point
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y
            self.initial_point_x, self.initial_point_y = self.center_point_coords
            logger.debug("Started dragging center control point.")
            return

        # Check if click is near the radius control point
        dist_to_radius_control = math.sqrt((event.x - self.radius_point_coords[0])**2 + (event.y - self.radius_point_coords[1])**2)
        if dist_to_radius_control < point_size + tolerance:
            self.active_point_index = 1 # 1 for radius point
            self.start_mouse_x = event.x
            self.start_mouse_y = event.y
            self.initial_point_x, self.initial_point_y = self.radius_point_coords
            logger.debug("Started dragging radius control point.")
            return
    
    def on_mouse_drag(self,event):
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

        if self.active_point_index == 0: # Dragging center point
            self.center_point_coords = (new_x, new_y)
            logger.debug(f"Dragging center point to {new_x, new_y}")
        elif self.active_point_index == 1: # Dragging radius point
            self.radius_point_coords = (new_x, new_y)
            logger.debug(f"Dragging radius point to {new_x, new_y}")

        self.draw_circle() # Redraw everything with the updated point(s)

    def on_button_release(self,event):
        """
        Handles mouse button release to stop dragging.
        """
        if self.active_point_index != -1:
            logger.debug(f"Stopped dragging point {self.active_point_index}.")
        self.active_point_index = -1 # Reset active point

        
        pass
