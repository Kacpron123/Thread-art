import math
import random
import numpy as np
import thread_profile
from PIL import Image


class thread_calculator:
    """
    Class for calculating thread vector from image
    """
    IMAGE_SIZE=1000
    def __init__(self,image,start_angle, num_of_pins,profile=thread_profile.trapezoidal_profile):
        """
        Args:
            image (_type_): image to calculate threads, image need to be of size 1000x1000
            start_angle (_type_): angle of first pin
            num_of_pins (_type_): number of pins
            profile (_type_): profile of thread, default is trapezoidal
        """
        if image.width != self.IMAGE_SIZE or image.height != self.IMAGE_SIZE:
            raise ValueError("Image size must be 1000x1000")
        self.image=image.convert("L")
        # TODO use numpy
        self.vector=255-np.array(self.image,dtype=np.uint8)
        self.output_vector = np.full((self.IMAGE_SIZE,self.IMAGE_SIZE),255,dtype=np.uint8)
        self.num_of_pins=num_of_pins
        self._thread_profile=profile
        self._thread_width=1
        self._ignore_close_pins=10
        self._drawn_lines=set()
        self._selected_pins=[]

        # pin coords
        self.pin_coords = np.zeros((self.num_of_pins, 2), dtype=int)
        center_x = center_y = radius = self.IMAGE_SIZE / 2
        for i in range(self.num_of_pins):
            angle = start_angle + i * 2 * np.pi / self.num_of_pins
            x = int(center_x + radius * np.cos(angle))
            y = int(center_y + radius * np.sin(angle))
            # adding noise to minimize Moire effect
            rand=int(self.IMAGE_SIZE*0.008)
            if x > rand:
                x -= random.randint(1, rand)
            elif x < (2 * radius - rand):
                x += random.randint(1, rand)
            if y > rand:
                y -= random.randint(1, rand)
            elif y < (2 * radius - rand):
                y += random.randint(1, rand)
            self.pin_coords[i] = (x, y)


    @staticmethod
    def _create_image_from_vector(vector):
        return Image.fromarray(vector,mode="L")
    
    def calculate_thread(self,draw=False,limit=2000,save_pins=False):
        """main function for calculating threads"""
        current_pin=0
        # self._line(5,19)
        for w in range(limit):
            new_line=self._find_next_pin(current_pin)
            self._selected_pins.append(current_pin)
            if new_line is None:
                print("end")
                break
            self._drawn_lines.add(tuple(sorted(new_line)))
            self._line(*new_line)
            if draw and not w%40:
                image_from_vector = thread_calculator._create_image_from_vector(self.output_vector)
                image_from_vector.save("output.png")
            current_pin=new_line[1]
        if save_pins:
            with open("selected_pins.txt", "w") as file:
                for i,pin in enumerate(self._selected_pins):
                    file.write(f"{i}.\t{pin}\n")

        return self._create_image_from_vector(self.output_vector)

    def _line(self, pin1_idx: int, pin2_idx: int):
        """
        drawing lines with a help of thread_profile which determine how thread apply color
        especially needed for bigger resolutions
        """
        x1, y1 = self.pin_coords[pin1_idx]
        x2, y2 = self.pin_coords[pin2_idx]
        max_distance = self._thread_width / 2.0

        line_vec = np.array([x2 - x1, y2 - y1], dtype=np.float32)
        line_length_sq = np.sum(line_vec**2)

        # Bounding box
        min_x = max(0, int(min(x1, x2) - math.ceil(max_distance)))
        max_x = min(self.IMAGE_SIZE, int(max(x1, x2) + math.ceil(max_distance) + 1))
        min_y = max(0, int(min(y1, y2) - math.ceil(max_distance)))
        max_y = min(self.IMAGE_SIZE, int(max(y1, y2) + math.ceil(max_distance) + 1))

        x_coords_grid, y_coords_grid = np.meshgrid(np.arange(min_x, max_x), np.arange(min_y, max_y))
        P_coords = np.stack((x_coords_grid.flatten(), y_coords_grid.flatten()), axis=1).astype(np.float32)

        if line_length_sq == 0:
            distances = np.linalg.norm(P_coords - np.array([x1, y1], dtype=np.float32), axis=1)
        else:
            line_length = np.sqrt(line_length_sq)
            line_vec_normalized = line_vec / line_length
            AP = P_coords - np.array([x1, y1], dtype=np.float32)
            t = np.dot(AP, line_vec_normalized)
            
            t_clamped = np.clip(t, 0, line_length)
            
            closest_points_on_segment = np.array([x1, y1], dtype=np.float32) + np.outer(t_clamped, line_vec_normalized)
            distances = np.linalg.norm(P_coords - closest_points_on_segment, axis=1)

        within_distance_mask = distances <= max_distance
        
        relevant_P_coords = P_coords[within_distance_mask]
        relevant_distances = distances[within_distance_mask]

        if relevant_P_coords.size == 0:
            return

        x_for_profile_0_1 = relevant_distances / max_distance

        vectorized_profile_func = np.vectorize(self._thread_profile)
        densities = vectorized_profile_func(x_for_profile_0_1)
        
        densities = np.clip(densities, 0.0, thread_profile._MAX_DENSITY)
        
        applied_darkness_values = (densities * 255).astype(np.float32)

        pixel_y_indices = relevant_P_coords[:, 1].astype(int)
        pixel_x_indices = relevant_P_coords[:, 0].astype(int)

        current_pixel_values = self.output_vector[pixel_y_indices, pixel_x_indices].astype(np.float32)
        updated_values = np.clip(current_pixel_values - applied_darkness_values, 0, 255).astype(np.uint8)
        self.output_vector[pixel_y_indices, pixel_x_indices] = updated_values

    def _calculate_efficiency(self, pin1_idx: int, pin2_idx: int) -> float:
        """
        Calculates the efficiency of a line between two pins.
        A higher value indicates a better line (removes more "darkness" from the target image).
        """
        # TODO FEATURE: giving bigger score for threads that create edges
        x0, y0 = self.pin_coords[pin1_idx]
        x1, y1 = self.pin_coords[pin2_idx]
        length = int(np.hypot(x1 - x0, y1 - y0))
        # mask of line
        x = np.linspace(x0, x1, length).astype(np.int16)
        y = np.linspace(y0, y1, length).astype(np.int16)
        
        target=self.vector[y,x]
        current_color=self.output_vector[y,x]
        actual_added=np.minimum(current_color,255*thread_profile._MAX_DENSITY)
        return np.sum(actual_added*target)

    def _find_next_pin(self, current_pin_idx: int) -> tuple | None:
        """
        Finds the best line from current_pin_idx to another pin based on efficiency.
        Returns a tuple (current_pin_idx, best_next_pin_idx) or None if no effective line is found.
        """
        best_efficiency = -1.0
        best_next_pin_idx = -1

        
        for i in range(self.num_of_pins-1):
            searched_pin_idx=(current_pin_idx+i) % self.num_of_pins
            if tuple(sorted((searched_pin_idx,current_pin_idx))) in self._drawn_lines:
                continue
            if abs(current_pin_idx-searched_pin_idx)<self._ignore_close_pins:
                continue
            efficiency = self._calculate_efficiency(current_pin_idx, searched_pin_idx)

            if efficiency > best_efficiency:
                best_efficiency,best_next_pin_idx = efficiency,searched_pin_idx
        
        return (current_pin_idx, best_next_pin_idx)

if __name__ == "__main__":
    import sys
    from matplotlib import pyplot as plt
    
    image_path = sys.argv[1]
    image = Image.open(image_path)
    size=thread_calculator.IMAGE_SIZE=1000

    if image.width != size or image.height != size:
        image = image.resize((min(image.width,image.height),min(image.width,image.height)), resample=Image.BICUBIC)
        image = image.resize((size,size), resample=Image.BICUBIC)

    
    tc=thread_calculator(image,0, 200)
    tc._thread_width=1
    calculated_image=tc.calculate_thread(draw=True,limit=2000)
    plt.imshow(calculated_image,cmap='gray')
    plt.show()
    calculated_image.save("output.png")