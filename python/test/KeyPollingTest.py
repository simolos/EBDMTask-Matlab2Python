import unittest
import random

# Configuration constants
N_EVENTS = 30               # Number of simulated key press events
T_MAX = 5                   # Maximum simulation time in seconds
POLLING_INTERVAL = 0.005    # Polling interval in seconds
KEYS = "abc"                # Keys available for simulation
MIN_DURATION = 0.030        # Minimum duration of a key press (s)
MAX_DURATION = 0.100        # Maximum duration of a key press (s)
MIN_GAP = 0.005             # Minimum gap between consecutive presses of the same key (s)

class FakeEvent:
    """
    Simulates key press events using a virtual time counter and a predefined schedule.
    """
    def __init__(self, schedule):
        self.schedule = schedule  # List of tuples: (key, press_time, release_time)
        self.pressed = set()      # Track keys currently considered pressed
        self.detected_up = set()  # Track keys already reported as released
        self.time = 0.0           # Virtual current time

    def advance_time(self, delta):
        """Advance the virtual clock by the given delta (s)."""
        self.time += delta

    def getKeys(self):
        """
        Return a list of events that occur at the current virtual time:
          - Keydown when time enters press window
          - Keyup when time reaches or passes release time
        Each event: ("down"/"up", key, theoretical_time, detected_time)
        """
        events = []
        for k, t_down, t_up in self.schedule:
            # Report keydown once when entering press window
            if t_down <= self.time < t_up and k not in self.pressed:
                events.append(("down", k, t_down, self.time))
                self.pressed.add(k)
            # Report keyup once when passing release time
            if self.time >= t_up and (k, t_up) not in self.detected_up:
                events.append(("up", k, t_up, self.time))
                self.detected_up.add((k, t_up))
                self.pressed.discard(k)
        return events


def random_schedule_nonoverlap(n_events, t_max, keys, min_dur, max_dur, min_gap):
    """
    Generate a non-overlapping schedule of key press events:
      - Each key press occurs after the previous release + min_gap
      - Press durations are between min_dur and max_dur
    Returns sorted list of (key, press_time, release_time).
    """
    schedule = []
    key_last_up = {k: 0.0 for k in keys}
    for _ in range(n_events):
        k = random.choice(keys)
        earliest_down = key_last_up[k] + min_gap
        # Skip if cannot fit within t_max
        if earliest_down >= t_max - max_dur:
            continue
        t_down = random.uniform(earliest_down, t_max - max_dur)
        duration = random.uniform(min_dur, max_dur)
        t_up = t_down + duration
        schedule.append((k, t_down, t_up))
        key_last_up[k] = t_up
    schedule.sort(key=lambda tup: tup[1])
    return schedule


def polling_fake(schedule, polling_interval, t_max):
    """
    Simulate polling of FakeEvent at regular intervals:
      - Advance virtual time by polling_interval each iteration
      - Collect down/up events only once per theoretical event
    Returns list of detected events.
    """
    fake_event = FakeEvent(schedule)
    detected = []
    seen_down = set()
    seen_up = set()
    # Continue until virtual time reaches t_max
    while fake_event.time < t_max:
        events = fake_event.getKeys()
        for evtype, k, t_theo, t_poll in events:
            if evtype == "down" and (k, t_theo) not in seen_down:
                detected.append((evtype, k, t_theo, t_poll))
                seen_down.add((k, t_theo))
            elif evtype == "up" and (k, t_theo) not in seen_up:
                detected.append((evtype, k, t_theo, t_poll))
                seen_up.add((k, t_theo))
        fake_event.advance_time(polling_interval)
    return detected

class TestPollingRandomized(unittest.TestCase):
    """
    Test detection of simulated key press events under a single polling frequency.
    """
    def test_one_polling_freq(self):
        random.seed()
        # Generate a random schedule of non-overlapping key events
        schedule = random_schedule_nonoverlap(
            n_events=N_EVENTS,
            t_max=T_MAX,
            keys=KEYS,
            min_dur=MIN_DURATION,
            max_dur=MAX_DURATION,
            min_gap=MIN_GAP
        )
        # Perform polling simulation
        detected = polling_fake(
            schedule,
            polling_interval=POLLING_INTERVAL,
            t_max=T_MAX
        )

        n_generated = 2 * len(schedule)
        n_detected = len(detected)
        missed = n_generated - n_detected

        # Print ground truth and detected events
        print("\n=== Generated KeyDown/KeyUp Events (ground truth) ===")
        for idx, (k, t_down, t_up) in enumerate(schedule, 1):
            print(f"{idx:2d}. {k:<3} down: {t_down:.4f}s | up: {t_up:.4f}s | dur: {t_up-t_down:.3f}s")
        print("\n=== Events Detected by Polling ===")
        for evtype, k, t_theo, t_poll in detected:
            err_ms = (t_poll - t_theo) * 1000
            print(f"{evtype.upper():<4} {k} | real: {t_theo:.4f}s | polling: {t_poll:.4f}s | Δ {err_ms:+.1f}ms")
        print(f"\nPolling {POLLING_INTERVAL*1000:.0f}ms | Events: generated={n_generated}, detected={n_detected}, missed={missed}")

        # Assert that not all events are missed
        self.assertTrue(missed < n_generated)

if __name__ == '__main__':
    unittest.main()
