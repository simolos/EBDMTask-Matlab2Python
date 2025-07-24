from pynput import keyboard
import time
from datetime import datetime

events = []
t0 = time.time()  # Reference clock at start

def on_press(key):
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except AttributeError:
        k = str(key)
    t = time.time()
    t_rel = t - t0  # Relative time since start
    t_str = datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:-3]
    print(f"[pynput] Key DOWN: {k} at {t_str} (relative: {t_rel:.3f}s)")
    events.append(('down', k, t, t_rel, t_str))

def on_release(key):
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except AttributeError:
        k = str(key)
    t = time.time()
    t_rel = t - t0
    t_str = datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:-3]
    print(f"[pynput] Key UP  : {k} at {t_str} (relative: {t_rel:.3f}s)")
    events.append(('up', k, t, t_rel, t_str))
    if k in ['Key.esc', 'esc']:
        print("Quit (esc) pressed.")
        return False  # Stop listener on escape

print("Press any key (ESC to quit)...")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# Readable summary
print("\nSummary of recorded events:")
for ev in events:
    print(f"{ev[0].upper():<4} {ev[1]:<10} | {ev[4]} | rel {ev[3]:.3f}s")
