# pure pynput logger with relative timestamps
from pynput import keyboard
import time

first_tap = None
count     = 0

print("🔔 Ready. Press any key to start logging (ESC to quit).")

def on_press(key):
    global first_tap, count  # <— declare count as global too
    t = time.time()
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if first_tap is None:
        # first tap: set origin
        first_tap = t
        rel       = 0.0
        count    += 1
        print(f"[origin] {k} @ {rel:.4f}s")
    else:
        # compute relative time for every subsequent tap
        rel = t - first_tap
        if rel <= 8.0:
            count += 1
            print(f"[pynput] {count:02d} : {k} @ {rel:.4f}s")
        else:
            freq = count / 8.0
            print(f"[freq = {freq:.3f} taps/s]")
            return False   # stop after 8s

    # stop on ESC
    if k in ['Key.esc', 'esc']:
        return False

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print("✅ Logging finished.")
