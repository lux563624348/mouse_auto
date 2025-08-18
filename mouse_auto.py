import pyautogui
import time

def mouse_joggler(interval=15, distance=10):
    """
    Move the mouse slightly every `interval` seconds.
    
    :param interval: time between jiggles in seconds
    :param distance: how far to move the mouse in pixels
    """
    print(f"Mouse jiggler started. Moving every {interval} seconds. Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()  # Get current position
            pyautogui.moveTo(x + distance, y)  # Move right
            time.sleep(0.2)
            pyautogui.moveTo(x, y)  # Move back
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMouse jiggler stopped.")

if __name__ == "__main__":
    mouse_joggler(15, 10)

