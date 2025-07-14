import math

"""
Thread profiles
defined as functions that take a normalized x value (-1.0 to 1.0) and return a density value (0.0 to 1.0).
"""

_MAX_DENSITY = 0.2
def rectangular_profile(x: float) -> float:
    """
    Rectangular profile: Uniform density across the entire width (max. 50%).
    """
    if -1.0 <= x <= 1.0:
        return _MAX_DENSITY
    return 0.0

def circular_profile(x: float) -> float:
    """
    Circular profile: Maximum density in the center,decreasing towards the edges.
    """
    if -1.0 <= x <= 1.0:
        return _MAX_DENSITY * math.sqrt(1.0 - x**2)
    return 0.0

def trapezoidal_profile(x: float, core_width_normalized: float = 0.5) -> float:
    """
    Trapezoidal profile: Uniform density in the center, linearly decreasing towards the edges.
    """
    if not (0.0 <= core_width_normalized <= 1.0):
        raise ValueError("core_width_normalized must be in the range [0, 1].")

    abs_x = abs(x)
    if abs_x <= core_width_normalized:
        return _MAX_DENSITY # Full density in the core (max. 50%)
    elif abs_x <= 1.0:
        return _MAX_DENSITY * (1.0 - (abs_x - core_width_normalized) / (1.0 - core_width_normalized))
    return 0.0

def gaussian_profile(x: float, sigma_normalized: float = 0.3) -> float:
    """
    Gaussian profile: Soft, blurred edges.
    """
    if not (x >= -1.0 and x <= 1.0):
        return 0.0

    if sigma_normalized <= 0:
        raise ValueError("sigma_normalized must be greater than 0.")

    density_unscaled = math.exp(-(x**2) / (2 * sigma_normalized**2))
    
    # Scale the result to _MAX_DENSITY
    return _MAX_DENSITY * density_unscaled


# --- Example usage and visualization (requires matplotlib) ---
if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
        print("Matplotlib imported. Generating profile plots.")

        x_values = [i / 100.0 for i in range(-100, 101)]

        plt.figure(figsize=(10, 7))

        y_rect = [100*rectangular_profile(x) for x in x_values]
        plt.plot(x_values, y_rect, label="Rectangular", linestyle='--')

        y_circ = [100*circular_profile(x) for x in x_values]
        plt.plot(x_values, y_circ, label="Circular")

        y_trap = [100*trapezoidal_profile(x, core_width_normalized=0.6) for x in x_values]
        plt.plot(x_values, y_trap, label="Trapezoidal (core 0.6)", linestyle=':')

        y_gauss = [100*gaussian_profile(x, sigma_normalized=0.3) for x in x_values]
        plt.plot(x_values, y_gauss, label="Gaussian (sigma 0.3)", linestyle='-.')

        plt.title(f"Normalized Thread Profiles (Max. Density: {_MAX_DENSITY*100:.0f}%)")
        plt.xlabel("Normalized position (x) [-1, 1]")
        plt.ylabel("Density / Coverage precentage %") # Changed y-axis label
        plt.grid(True)
        plt.legend()
        plt.axhline(y=_MAX_DENSITY, color='green', linestyle=':', linewidth=0.8, label=f"Max. density ({_MAX_DENSITY})") # Added max. density line
        plt.axvline(x=0, color='gray', linestyle='--', linewidth=0.8, label="Thread center")
        plt.axvline(x=-1, color='red', linestyle=':', linewidth=0.8, label="Thread edge")
        plt.axvline(x=1, color='red', linestyle=':', linewidth=0.8)
        plt.ylim(0, 100) # Still set y-axis range to 1.0, but values are up to 0.5
        plt.show()

    except ImportError:
        print("Matplotlib not found. Cannot generate example plots.")
        print("You can install: pip install matplotlib")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("\nExample usage (max. 0.5):")
    print(f"Rectangular (x=0.5): {rectangular_profile(0.5):.2f}")
    print(f"Circular (x=0.5): {circular_profile(0.5):.2f}")
    print(f"Trapezoidal (x=0.8, core=0.6): {trapezoidal_profile(0.8, 0.6):.2f}")
    print(f"Gaussian (x=0.0, sigma=0.3): {gaussian_profile(0.0, 0.3):.2f}")
    print(f"Gaussian (x=0.9, sigma=0.3): {gaussian_profile(0.9, 0.3):.2f}")

