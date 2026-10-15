import rumps
import threading
import time
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pynput.mouse import Controller
from AppKit import NSScreen

class MouseJigglerApp(rumps.App):
    def __init__(self):
        super(MouseJigglerApp, self).__init__("🖱️  Jiggler")

        self.distance = 100
        self.jiggling = False
        self.stop_time = None
        self.mouse = Controller()

        # Screen information may not be ready when launched. Resolve it when
        # the user starts the jiggler so the menu app can still launch cleanly.
        self.screen_width = self.screen_height = None
        self.region_x1 = self.region_x2 = None
        self.region_y1 = self.region_y2 = None

        # Create "Start for" submenu (1..5 hours)
        self.start_for_menu = rumps.MenuItem("Start for ⏱")
        for hrs in range(1, 6):
            self.start_for_menu.add(rumps.MenuItem(
                title=f"{hrs} hour{'s' if hrs > 1 else ''}",
                callback=lambda sender, h=hrs: self.start_for(h)
            ))

        # Manual stop item (always present so user can stop early)
        self.stop_now_item = rumps.MenuItem(title="Stop Now", callback=self.manual_stop)

        # Build menu
        self.menu = [
            self.start_for_menu,
            self.stop_now_item,
            None,
            rumps.MenuItem(title="Quit", callback=rumps.quit_application)
        ]

    def start_for(self, hours):
        """Start jiggling for a fixed number of hours (1..5). If already jiggling, extend/restart timer."""
        if not self._update_screen_bounds():
            self._notify(
                title="Mouse Jiggler",
                subtitle="Display unavailable",
                message="No display is available yet. Try starting again after the desktop loads."
            )
            return

        now_est = datetime.now(ZoneInfo("US/Eastern"))
        stop_time = now_est + timedelta(hours=hours)
        self.stop_time = stop_time

        # If not currently jiggling, start the thread
        if not self.jiggling:
            self.jiggling = True
            threading.Thread(target=self._jiggle_loop, daemon=True).start()
            self._notify(
                title="Mouse Jiggler",
                subtitle="Started",
                message=f"Jiggling for {hours} hour{'s' if hours > 1 else ''}."
            )
            print(f"▶️ Started jiggling; will stop at {stop_time.strftime('%I:%M %p EST')}")
        else:
            # already jiggling: update stop_time to new value
            self._notify(
                title="Mouse Jiggler",
                subtitle="Timer Updated",
                message=f"Will now stop in {hours} hour{'s' if hours > 1 else ''}."
            )
            print(f"🔁 Timer updated; will stop at {stop_time.strftime('%I:%M %p EST')}")

    def _update_screen_bounds(self):
        """Refresh the movement area, returning False when no display is ready."""
        try:
            screens = NSScreen.screens()
            screen_info = NSScreen.mainScreen() or (screens[0] if screens else None)
            if screen_info is None:
                return False

            screen = screen_info.frame()
            self.screen_width = int(screen.size.width)
            self.screen_height = int(screen.size.height)
            self.region_x1 = self.screen_width // 3
            self.region_x2 = 2 * self.screen_width // 3
            self.region_y1 = self.screen_height // 3
            self.region_y2 = 2 * self.screen_height // 3
            return self.screen_width > 0 and self.screen_height > 0
        except Exception as exc:
            print(f"⚠️ Could not read display bounds: {exc}")
            return False

    def manual_stop(self, sender=None):
        """User requested an immediate stop."""
        if self.jiggling:
            self._stop_jiggling("Stopped manually.")
            print("🛑 Jiggling manually stopped.")
        else:
            self._notify(title="Mouse Jiggler", subtitle="Not running", message="Jiggler is not currently running.")
            print("ℹ️ Manual stop requested but jiggler was not running.")

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

            # --- Move the mouse within center 1/3 region ---
            x, y = self.mouse.position
            dx = random.randint(-self.distance, self.distance)
            dy = random.randint(-self.distance, self.distance)
            new_x = min(max(x + dx, self.region_x1), self.region_x2)
            new_y = min(max(y + dy, self.region_y1), self.region_y2)

            print(f"Moving to ({new_x}, {new_y})")
            try:
                self.mouse.position = (new_x, new_y)
            except Exception as e:
                # Some environments can throw when setting mouse position; log and continue
                print(f"⚠️ Failed to move mouse: {e}")

            # Random delay between moves
            time.sleep(random.uniform(10, 20))

        # ensure flags are cleared if loop exits
        self.jiggling = False
        self.stop_time = None

    def _stop_jiggling(self, message):
        """Handle stopping logic and notify the user."""
        self.jiggling = False
        self.stop_time = None
        self._notify(
            title="Mouse Jiggler",
            subtitle="Stopped",
            message=message
        )

    def _notify(self, title, subtitle, message):
        """Send a notification without letting a missing Info.plist break the app."""
        try:
            rumps.notification(title=title, subtitle=subtitle, message=message)
        except RuntimeError as exc:
            # rumps requires an Info.plist next to sys.executable. Plain script
            # launches (for example, from a conda interpreter) may not have one.
            print(f"⚠️ Notification unavailable: {exc}")

if __name__ == "__main__":
    MouseJigglerApp().run()

