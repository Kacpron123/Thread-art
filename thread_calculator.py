import thread_profile

class thread_calculator:
    def __init__(self,image,start_angle, num_of_pins,profile):
        self.image=image
        self.start_angle=start_angle
        self.num_of_pins=num_of_pins
        self.thread_profile=profile

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
        image = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                image.putpixel((x, y), vector[y * width + x])
        return image

    def calculate_thread(self):
        vector = thread_calculator._prepare_vector_from_image(self.image)
        drawn_lines=[]
        current_pin=0
        while(True):
            drawn_lines.append(thread_calculator._find_best_line(self.image))
            break
        return vector
    def _drawn_line(image):
        pass
    def _find_best_line(image):
        pass


if __name__ == "__main__":
    import sys
    from PIL import Image
    image_path = sys.argv[1]
    image = Image.open(image_path)
    tc=thread_calculator(image,0, 60)
    vector=tc.calculate_thread()
    image_from_vector = thread_calculator._create_image_from_vector(vector, image.width, image.height)
    image_from_vector.save("output.jpg")