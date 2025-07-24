import unittest

class FakeEvent:
    """Simulates key press events using a virtual time counter."""
    def __init__(self, schedule):
        # schedule: list of tuples (key, press_time, release_time)
        self.schedule = schedule
        self.time = 0.0  # virtual simulated time
        self.pressed_keys = set()

    def reset(self):
        # Reset the virtual time and key press states
        self.time = 0.0
        self.pressed_keys.clear()

    def advance_time(self, delta):
        # Advance the virtual time by delta seconds
        self.time += delta

    def getKeys(self, keyList=None, timeStamped=None):
        # Check if any keys are pressed exactly at the current virtual time
        pressed_now = []
        for k, t_down, _ in self.schedule:
            if abs(self.time - t_down) < 0.001 and k not in self.pressed_keys:
                pressed_now.append((k, t_down))
                self.pressed_keys.add(k)
        return pressed_now

    def isKeyDown(self, k):
        # Check if a given key is currently pressed at the virtual time
        for k0, t_down, t_up in self.schedule:
            if k0 == k and t_down <= self.time < t_up:
                return True
        return False

def key_detector_psychopy_fake(target_keys, t_limit, fake_event, time_step=0.001):
    """Detects key presses within a simulated time window using virtual time."""
    elapsed = 0.0
    while elapsed < t_limit:
        # Get key events at the current simulated time
        keys = fake_event.getKeys(keyList=target_keys + ['escape'], timeStamped=None)
        if keys:
            k, t_down = keys[0]
            if k == 'escape':
                return None, None

            t_start = t_down
            current_key = k

            # Find the release time (t_up) for the current key event
            t_up = next((t_u for k_sched, t_d, t_u in fake_event.schedule
                         if k_sched == current_key and t_d == t_start), None)

            if t_up is None:
                return None, None

            # Advance the virtual time until the key is released
            while fake_event.time < t_up:
                elapsed += time_step
                fake_event.advance_time(time_step)

            duration = t_up - t_start
            return current_key, duration

        # Advance virtual time if no key event detected yet
        elapsed += time_step
        fake_event.advance_time(time_step)

    # No key press detected within time limit
    return None, None

class TestKeyDetectorPsychopy(unittest.TestCase):
    def test_keypress_and_release(self):
        expected_key = 'left'
        expected_duration = 0.4
        tolerance = 1e-5

        # Schedule simulates pressing 'left' at 0.25s and releasing at 0.65s
        schedule = [(expected_key, 0.25, 0.65)]
        fake_event = FakeEvent(schedule)
        fake_event.reset()

        key, duration = key_detector_psychopy_fake(
            ['left', 'right'],
            t_limit=1.0,
            fake_event=fake_event,
            time_step=0.001
        )

        # Assert detected key and timing match expected values
        self.assertEqual(key, expected_key, f"Key should be '{expected_key}' but got '{key}'")
        self.assertAlmostEqual(duration, expected_duration, delta=tolerance,
                               msg=f"Duration {duration} differs from expected {expected_duration}")

if __name__ == '__main__':
    unittest.main()
