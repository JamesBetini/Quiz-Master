import threading
import time
import tkinter as tk

class QuizTimer:
    def __init__(self, duration_minutes=10, callback=None):
        """
        Initialize the QuizTimer with a duration in minutes and an optional callback function.
        The callback will be called when the timer reaches zero.
        """
        self.duration_seconds = duration_minutes * 60
        self.remaining_seconds = self.duration_seconds
        self.is_running = False
        self.callback = callback
        self.timer_thread = None
        self.lock = threading.Lock()

    def start_timer(self):
        """
        Start the countdown timer in a separate thread.
        """
        if not self.is_running:
            self.is_running = True
            self.timer_thread = threading.Thread(target=self._countdown, daemon=True)
            self.timer_thread.start()

    def stop_timer(self):
        """
        Stop the timer.
        """
        with self.lock:
            self.is_running = False

    def reset_timer(self, duration_minutes=10):
        """
        Reset the timer to a new duration.
        """
        with self.lock:
            self.is_running = False
            self.duration_seconds = duration_minutes * 60
            self.remaining_seconds = self.duration_seconds

    def get_remaining_time(self):
        """
        Get the remaining time as a formatted string (MM:SS).
        """
        with self.lock:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"

    def _countdown(self):
        """
        Internal method to handle the countdown in a loop.
        Calls the callback when time reaches zero.
        """
        while self.is_running and self.remaining_seconds > 0:
            time.sleep(1)
            with self.lock:
                self.remaining_seconds -= 1

        if self.is_running and self.callback:
            self.callback()  # Call the callback when time is up
            self.is_running = False

    def update_gui_label(self, label):
        """
        Update a Tkinter label with the remaining time every second.
        This should be called in the main thread.
        """
        if self.is_running:
            label.config(text=f"Time Remaining: {self.get_remaining_time()}")
            label.after(1000, lambda: self.update_gui_label(label))
        else:
            label.config(text="Time's Up!")

# Example usage (for testing)
if __name__ == "__main__":
    def time_up_callback():
        print("Time's up! Quiz submitted automatically.")

    timer = QuizTimer(duration_minutes=1, callback=time_up_callback)
    timer.start_timer()

    # Simulate GUI update (in a real app, this would be in the Tkinter main loop)
    root = tk.Tk()
    time_label = tk.Label(root, text="Time Remaining: 01:00", font=("Arial", 16))
    time_label.pack()
    timer.update_gui_label(time_label)
    root.mainloop()
