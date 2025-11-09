import rumps
import threading
import time
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pynput.mouse import Controller
from AppKit import NSScreen


def safe_notify(self, title, subtitle, message):
    try:
        rumps.notification(title=title, subtitle=subtitle, message=message)
    except Exception as e:
        print(f"[Notification skipped: {e}] {title} — {subtitle}: {message}")


class MouseJigglerApp(rumps.App):
    def __init__(self):
        super(MouseJigglerApp, self).__init__("🖱️  Jiggler")

        self.distance = 100
        self.jiggling = False
        self.stop_time = None
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

        # Create Stop-In submenu
        self.stop_in_menu = rumps.MenuItem("Stop In ⏱")
        for hrs in range(1, 6):
            self.stop_in_menu.add(rumps.MenuItem(
                title=f"{hrs} hour{'s' if hrs > 1 else ''}",
                callback=lambda sender, h=hrs: self.set_stop_timer(h)
            ))

        self.menu = [
            rumps.MenuItem(title="Start Jiggling", callback=self.toggle_jiggling),
            self.stop_in_menu,
            None,
            rumps.MenuItem(title="Quit", callback=rumps.quit_application)
        ]

    def set_stop_timer(self, hours):
        """Schedule stop time"""
        self.stop_time = datetime.now(ZoneInfo("US/Eastern")) + timedelta(hours=hours)
        rumps.notification(
            title="Mouse Jiggler",
            subtitle="Timer Set",
            message=f"Will stop in {hours} hour{'s' if hours > 1 else ''}."
        )
        print(f"🕒 Stop scheduled for {self.stop_time.strftime('%I:%M %p EST')}")

    def toggle_jiggling(self, sender):
        if not self.jiggling:
            sender.title = "Stop Jiggling"
            self.jiggling = True
            threading.Thread(target=self._jiggle_loop, daemon=True).start()
        else:
            sender.title = "Start Jiggling"
            self.jiggling = False
            self.stop_time = None
            print("🛑 Jiggling manually stopped.")

    def _jiggle_loop(self):
        while self.jiggling:
            now_est = datetime.now(ZoneInfo("US/Eastern"))

            # --- Stop after 5 PM EST automatically ---
            if now_est.hour >= 17:
                print("🕔 It's after 5 PM EST — stopping jiggler.")
                self._stop_jiggling("Stopped automatically after 5 PM EST.")
                break

            # --- Stop if timer is reached ---
            if self.stop_time and now_est >= self.stop_time:
                print("⏰ Timer reached — stopping jiggler.")
                self._stop_jiggling("Timer reached — jiggler stopped.")
                break

            # --- Move the mouse ---
            x, y = self.mouse.position
            dx = random.randint(-self.distance, self.distance)
            dy = random.randint(-self.distance, self.distance)
            new_x = min(max(x + dx, self.region_x1), self.region_x2)
            new_y = min(max(y + dy, self.region_y1), self.region_y2)

            print(f"Moving to ({new_x}, {new_y})")
            self.mouse.position = (new_x, new_y)

            # Random delay
            time.sleep(random.uniform(10, 20))

    def _stop_jiggling(self, message):
        """Handle stopping logic"""
        self.jiggling = False
        self.stop_time = None
        rumps.notification(
            title="Mouse Jiggler",
            subtitle="Stopped",
            message=message
        )
        # Reset menu button title
        self.menu["Start Jiggling"].title = "Start Jiggling"


if __name__ == "__main__":
    MouseJigglerApp().run()

