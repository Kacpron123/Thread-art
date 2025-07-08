import math
from PIL import Image # Upewnij się, że PIL Image jest zaimportowane
import sys
import time # Dodane do mierzenia czasu wykonania

# --- MOCK PROFILU (na wypadek, gdyby thread_profile.py nie było dostępne) ---
try:
    import thread_profile
except ImportError:
    print("Warning: thread_profile.py not found. Using a DummyProfile.")
    class DummyTrapezoidalProfile:
        def __call__(self, normalized_offset: float) -> float:
            return 1.0 # Prosty profil, który zawsze zwraca 1.0 (pełna gęstość)

    thread_profile = type('module', (object,), {'trapezoidal_profile': DummyTrapezoidalProfile()})()
# --- KONIEC MOCK PROFILU ---


class thread_calculator:
    """
    Class for calculating thread vector from image
    """
    def __init__(self,image: Image.Image,start_angle: float, num_of_pins: int,profile=thread_profile.trapezoidal_profile):
        """
        Args:
            image (PIL.Image.Image): obraz do obliczenia nici. Zostanie przekonwertowany do 'L' (skala szarości).
            start_angle (float): kąt pierwszego pina
            num_of_pins (int): liczba pinów
            profile (callable, optional): profil nici, domyślnie trapezoidalny
        """
        self.image = image.convert("L")
        # --- POPRAWKA: Przechowuj wymiary obrazu dla spójnego dostępu ---
        self.image_width = self.image.width
        self.image_height = self.image.height
        
        # --- LOGIKA DLA CZARNYCH NICI: self.vector ODWRACA OBRAZ ---
        # Ciemne miejsca w oryginalnym obrazie stają się wysokimi wartościami w self.vector,
        # co oznacza, że te miejsca są "celem ciemności" do pokrycia czarnymi nićmi.
        # --- POPRAWKA: Użyj self.image, aby zapewnić, że obraz jest już L ---
        self.vector = [255 - p for p in thread_calculator._prepare_vector_from_image(self.image)]
        
        # --- LOGIKA DLA CZARNYCH NICI: output_vector ZACZYNA SIĘ OD BIELI (255) ---
        self.output_vector = [255 for _ in range(len(self.vector))]
        
        self.num_of_pins=num_of_pins
        self.thread_profile=profile
        
        self.thread_density_value = 10 # Siła pojedynczej nici (ile ciemności dodaje)
        
        self._drawn_lines=[]
        self.pin_coords=[]
        
        # --- POPRAWKA: Robustne i spójne obliczanie promienia pinów ---
        center_x = self.image_width / 2
        center_y = self.image_height / 2
        # Użyj 98% min. promienia (szerokości lub wysokości) dla lepszego rozmieszczenia
        radius = min(self.image_width, self.image_height) / 2 * 0.98 
        
        for i in range(self.num_of_pins):
            angle=start_angle+i*2*math.pi/self.num_of_pins
            x=int(center_x+radius*math.cos(angle))
            y=int(center_y+radius*math.sin(angle))
            # Użyj zapisanych wymiarów do ograniczenia
            x=max(0,min(x,self.image_width-1))
            y=max(0,min(y,self.image_height-1))
            self.pin_coords.append((x,y))

    @staticmethod
    def _prepare_vector_from_image(image: Image.Image) -> list[int]:
        """Konwertuje obraz na wektor wartości pikseli."""
        vector = []
        for y in range(image.height):
            for x in range(image.width):
                vector.append(image.getpixel((x, y)))
        return vector

    @staticmethod
    def _create_image_from_vector(vector: list[float], width: int, height: int) -> Image.Image:
        """Tworzy obraz PIL z wektora wartości pikseli."""
        imageres = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                # --- POPRAWKA: Zapewnij, że wartości są w zakresie [0, 255] ---
                pixel_val = max(0, min(255, int(vector[y * width + x]))) 
                imageres.putpixel((x, y), pixel_val)
        return imageres
    
    @staticmethod
    def line_algorithm(x0: int,y0: int,x1: int,y1: int):
        """Generator dla algorytmu linii (Bresenham's)"""
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

    def calculate_thread(self, limit=3000): # Przywrócono parametr limit
        """Główna funkcja do obliczania nici"""
        print(f"Starting thread calculation for {limit} lines...")
        start_time = time.time()

        current_pin=0
        for line_num in range(limit): # Używamy parametru limit
            if line_num % 100 == 0 and line_num > 0: # Drukuj postęp i zapisuj obrazy pośrednie
                print(f"  Drawing line {line_num}/{limit}...")
                # --- POPRAWKA: Użyj self.image_width/height ---
                intermediate_img = thread_calculator._create_image_from_vector(self.output_vector, self.image_width, self.image_height)
                intermediate_img.save(f"debug_output_{line_num:04d}.jpg")

            new_line=self._find_best_line(current_pin)
            if new_line is None:
                print(f"end: No more effective lines found after {line_num} lines.")
                break
            self._drawn_lines.append(new_line)
            self._draw_line(*new_line)
            current_pin=new_line[1]

        end_time = time.time()
        print(f"Thread calculation finished in {end_time - start_time:.2f} seconds.")

        # Zapisz końcowy obraz
        # --- POPRAWKA: Użyj self.image_width/height ---
        image_from_vector = thread_calculator._create_image_from_vector(self.output_vector, self.image_width, self.image_height)
        image_from_vector.save("output.jpg")
        print("Final output image saved to output.jpg")
        
        return self.output_vector
    
    def _draw_line(self,pin1: int,pin2: int):
        x1,y1=self.pin_coords[pin1]
        x2,y2=self.pin_coords[pin2]
        for x,y in thread_calculator.line_algorithm(x1,y1,x2,y2):
            # --- POPRAWKA: Użyj self.image_width ---
            pixel_index=y*self.image_width+x
            applied_color=self.thread_density_value*self.thread_profile(0)
            # --- POPRAWKA: Prawidłowe odejmowanie jasności z ograniczeniem do 0 ---
            self.output_vector[pixel_index] = max(0, self.output_vector[pixel_index] - applied_color)

    def _calculate_efficiency(self, pin1_idx: int, pin2_idx: int) -> float:
        """
        Oblicza efektywność linii między dwoma pinami dla czarnych nici na białym tle.
        Wyższa wartość oznacza lepszą linię (usuwa więcej "ciemności" z docelowego obrazu).
        """
        x0, y0 = self.pin_coords[pin1_idx]
        x1, y1 = self.pin_coords[pin2_idx]

        efficiency_score = 0.0
        applied_density = self.thread_density_value * self.thread_profile(0) # Ile ciemności może dodać nić
        
        for x, y in thread_calculator.line_algorithm(x0, y0, x1, y1):
            # --- POPRAWKA: Użyj self.image_width/height ---
            if 0 <= x < self.image_width and 0 <= y < self.image_height:
                pixel_index = y * self.image_width + x
                
                # darkness_target pochodzi z self.vector (odwrócony oryginalny obraz)
                # Im wyższa wartość, tym ciemniejsze powinno być to miejsce
                darkness_target=self.vector[pixel_index] 
                
                # current_brightness_at_pixel to aktualna jasność na kanwie wyjściowej
                current_brightness_at_pixel = self.output_vector[pixel_index]
                
                # --- POPRAWKA: actual_darkness_applied - Ile ciemności faktycznie doda ta linia ---
                # Ograniczone przez gęstość nici i aktualną jasność piksela (nie możemy "usunąć" więcej niż jest)
                actual_darkness_applied = min(applied_density, current_brightness_at_pixel)
                
                # Efektywność: Priorytetyzuj linie, które dodają dużo ciemności (actual_darkness_applied)
                # do obszarów, które potrzebują być ciemne (darkness_target jest wysokie).
                efficiency_score += actual_darkness_applied * darkness_target
        
        return efficiency_score

    def _find_best_line(self, current_pin_idx: int) -> tuple | None:
        """
        Znajduje najlepszą linię od current_pin_idx do innego pina na podstawie efektywności.
        Zwraca krotkę (current_pin_idx, best_next_pin_idx) lub None, jeśli nie znaleziono efektywnej linii.
        """
        best_efficiency = -1.0 
        best_next_pin_idx = -1

        for searched_pin_idx in range(self.num_of_pins):
            if searched_pin_idx == current_pin_idx:
                continue

            efficiency = self._calculate_efficiency(current_pin_idx, searched_pin_idx)

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_next_pin_idx = searched_pin_idx
        
        # --- POPRAWKA: Zmiana progu zatrzymania na niższy i użycie self.image_width/height ---
        if best_next_pin_idx == -1 or best_efficiency < (self.image_width * self.image_height * self.thread_density_value * 0.000005): 
            return None
        
        return (current_pin_idx, best_next_pin_idx)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python3 your_script_name.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    
    try:
        image_pil = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)
        
    class DummyConstProfile: 
        def __call__(self, x):
            return 1.0 # Profil zawsze zwracający 1.0 dla uproszczenia
    
    # --- PRZYKŁADOWE PARAMETRY: Zwiększona liczba pinów i linii dla lepszych wyników ---
    NUM_PINS = 200 
    NUM_LINES = 2500 

    tc = thread_calculator(image_pil, 0, NUM_PINS, DummyConstProfile())
    
    start_run_time = time.time()
    vector = tc.calculate_thread(limit=NUM_LINES) 
    end_run_time = time.time()

    print(f"Total script execution time: {end_run_time - start_run_time:.2f} seconds.")
    # Końcowy obraz jest zapisywany przez metodę calculate_thread