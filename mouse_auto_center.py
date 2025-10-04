import rumps
import threading
import time
import random
from pynput.mouse import Controller
from AppKit import NSScreen

class MouseJigglerApp(rumps.App):
    def __init__(self):
        super(MouseJigglerApp, self).__init__("🖱️  Jiggler")
        self.distance = 100   # max pixels per move
        self.jiggling = False
        self.mouse = Controller()

        # Get screen dimensions
        screen = NSScreen.mainScreen().frame()
        self.screen_width = int(screen.size.width)
        self.screen_height = int(screen.size.height)

        # Define center 1/3 region
        self.region_x1 = self.screen_width // 3
        self.region_x2 = 2 * self.screen_width // 3
        self.region_y1 = self.screen_height // 3
        self.region_y2 = 2 * self.screen_height // 3

        self.menu = [
            rumps.MenuItem(title="Start Jiggling", callback=self.toggle_jiggling),
            None,  # separator
            rumps.MenuItem(title="Quit", callback=rumps.quit_application)
        ]

    def toggle_jiggling(self, sender):
        if not self.jiggling:
            sender.title = "Stop Jiggling"
            self.jiggling = True
            threading.Thread(target=self._jiggle_loop, daemon=True).start()
        else:
            sender.title = "Start Jiggling"
            self.jiggling = False

    def _jiggle_loop(self):
        while self.jiggling:
            x, y = self.mouse.position

            # Random step in X and Y direction
            dx = random.randint(-self.distance, self.distance)
            dy = random.randint(-self.distance, self.distance)

            new_x = x + dx
            new_y = y + dy

            # Constrain to center region
            new_x = min(max(new_x, self.region_x1), self.region_x2)
            new_y = min(max(new_y, self.region_y1), self.region_y2)

            print(f"Moving to ({new_x}, {new_y})")
            self.mouse.position = (new_x, new_y)

            # Random sleep between 10 and 20 seconds
            sleep_time = random.uniform(10, 20)
            time.sleep(sleep_time)


if __name__ == "__main__":
    MouseJigglerApp().run()

