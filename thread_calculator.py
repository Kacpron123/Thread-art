import math
import numpy as np
import thread_profile

class thread_calculator:
    """
    Class for calculating thread vector from image
    """
    IMAGE_WIDTH=1000
    def __init__(self,image,start_angle, num_of_pins,profile=thread_profile.trapezoidal_profile):
        """
        Args:
            image (_type_): image to calculate threads, image need to be of size 1000x1000
            start_angle (_type_): angle of first pin
            num_of_pins (_type_): number of pins
            profile (_type_): profile of thread, default is trapezoidal
        """
        if image.width != self.IMAGE_WIDTH and image.height != self.IMAGE_WIDTH:
            raise ValueError("Image size must be 1000x1000")
        self.image=image.convert("L")
        # TODO use numpy
        self.vector=np.array([255 - p for p in thread_calculator._prepare_vector_from_image(self.image)],dtype=np.uint8)
        self.output_vector = np.array([255 for _ in range(self.IMAGE_WIDTH**2)],dtype=np.uint8)
        self.num_of_pins=num_of_pins
        self.thread_profile=profile
        self.thread_width=10
        self._drawn_lines=[]
        # pin coords
        self.pin_coords=[]
        center_x=center_y=radius = self.IMAGE_WIDTH / 2
        for i in range(self.num_of_pins):
            angle=start_angle+i*2*math.pi/self.num_of_pins
            x=int(center_x+radius*math.cos(angle))
            y=int(center_y+radius*math.sin(angle))
            x=max(0,min(x,self.IMAGE_WIDTH-1))
            y=max(0,min(y,self.IMAGE_WIDTH-1))
            self.pin_coords.append((x,y))

    @staticmethod
    def _prepare_vector_from_image(image):
        """Converts an image to a vector of pixel values."""
        vector = []
        for y in range(image.height):
            for x in range(image.width):
                vector.append(image.getpixel((x, y)))
        return vector

    @staticmethod
    def _create_image_from_vector(vector, width, height):
        imageres = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                imageres.putpixel((x, y), int(vector[y * width + x]))
        return imageres
    @staticmethod
    def line_algorithm(x0,y0,x1,y1):
        """Generator for line algorithm (Bresenham's)"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            yield x0, y0
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def calculate_thread(self,draw=False):
        """main function for calculating threads"""
        current_pin=0
        w=0
        while True:
            new_line=self._find_best_line(current_pin)
            # print(current_pin)
            if new_line is None:
                print("end")
                break
            self._drawn_lines.append(new_line)
            self._draw_line(*new_line)
            w+=1
            if draw and not w%40:
                image_from_vector = thread_calculator._create_image_from_vector(self.output_vector, self.IMAGE_WIDTH, self.IMAGE_WIDTH)
                image_from_vector.save("output.jpg")
            current_pin=new_line[1]

        return self.output_vector
    
    def _draw_line(self,pin1,pin2):
        x1,y1=self.pin_coords[pin1]
        x2,y2=self.pin_coords[pin2]
        for x,y in thread_calculator.line_algorithm(x1,y1,x2,y2):
            pixel_index=y*self.IMAGE_WIDTH+x
            applied_color=255*self.thread_profile(0)
            self.output_vector[pixel_index] = max(0,self.output_vector[pixel_index]-applied_color)

    def _calculate_efficiency(self, pin1_idx: int, pin2_idx: int) -> float:
        """
        Calculates the efficiency of a line between two pins.
        A higher value indicates a better line (removes more "darkness" from the target image).
        """
        x0, y0 = self.pin_coords[pin1_idx]
        x1, y1 = self.pin_coords[pin2_idx]

        efficiency_score = 0.0
        
        for x, y in thread_calculator.line_algorithm(x0, y0, x1, y1):
            if 0 <= x < self.IMAGE_WIDTH and 0 <= y < self.IMAGE_WIDTH:
                pixel_index = y * self.IMAGE_WIDTH + x 
                target=float(self.vector[pixel_index])
                current_color=float(self.output_vector[pixel_index])
                applied_color=255*self.thread_profile(0)
                actual_added=min(applied_color,current_color)
                efficiency_score+=actual_added*target

        return efficiency_score

    def _find_best_line(self, current_pin_idx: int) -> tuple | None:
        """
        Finds the best line from current_pin_idx to another pin based on efficiency.
        Returns a tuple (current_pin_idx, best_next_pin_idx) or None if no effective line is found.
        """
        best_efficiency = -1.0 # Initialize for maximizing (efficiency score won't be negative)
        best_next_pin_idx = -1

        max_best_efficiency=self.IMAGE_WIDTH**2*255*self.thread_profile(0)
        
        for searched_pin_idx in range(self.num_of_pins):
            if searched_pin_idx == current_pin_idx:
                continue
            if (searched_pin_idx,current_pin_idx) in self._drawn_lines or (current_pin_idx,searched_pin_idx) in self._drawn_lines:
                continue
            # TODO Optional: Adding conditions to avoid very short lines or connecting to already covered areas
            # For example, avoid connecting to immediate neighbors unless there are few pins

            efficiency = self._calculate_efficiency(current_pin_idx, searched_pin_idx)

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_next_pin_idx = searched_pin_idx
        
        if best_next_pin_idx == -1 or best_efficiency < (max_best_efficiency * 0.002): 
            return None
        
        return (current_pin_idx, best_next_pin_idx)

if __name__ == "__main__":
    import sys
    from PIL import Image
    image_path = sys.argv[1]
    image = Image.open(image_path)
    def const_profile(x):
        return 255*0.1
    tc=thread_calculator(image,0, 40,const_profile)
    vector=tc.calculate_thread(draw=True)
    image_from_vector = thread_calculator._create_image_from_vector(vector, image.width, image.height)
    image_from_vector.save("output.jpg")