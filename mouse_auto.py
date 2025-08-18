import rumps
import threading
import time
from pynput.mouse import Controller

class MouseJigglerApp(rumps.App):
    def __init__(self):
        super(MouseJigglerApp, self).__init__("🖱️ Jiggler")
        self.interval = 15   # seconds
        self.distance = 10   # pixels
        self.jiggling = False
        self.mouse = Controller()
        
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
            self.mouse.position = (x + self.distance, y)
            time.sleep(0.2)
            self.mouse.position = (x, y)
            time.sleep(self.interval)

if __name__ == "__main__":
    MouseJigglerApp().run()
