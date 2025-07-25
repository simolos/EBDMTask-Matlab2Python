from pynput import keyboard
import time

# ——————————————————————————————————————————————————————
# CONSTANTS
START_TIME = time.time()  # reference clock at start
# ——————————————————————————————————————————————————————

events = []  # will store tuples of the form ('down'/'up', key, t_rel)

def on_press(key):
    """
    Callback invoked on key press.  
    Records relative timestamp since START_TIME.
    """
    t_rel = time.time() - START_TIME
    events.append(('down', key, t_rel))
    # debug print
    print(f"[pynput] DOWN {key} @ {t_rel:.4f}s")

def on_release(key):
    """
    Callback invoked on key release.  
    Records relative timestamp and stops listener on ESC.
    """
    t_rel = time.time() - START_TIME
    events.append(('up', key, t_rel))
    print(f"[pynput] UP   {key} @ {t_rel:.4f}s")
    if key == keyboard.Key.esc:
        # stop the listener
        return False

if __name__ == '__main__':
    # launch the listener (blocking) that calls our callbacks
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # once stopped, print a summary of all captured events
    print("\nSummary of recorded events:")
    for evtype, key, t in events:
        print(f"{evtype.upper():<4} {key:<8} | {t:.4f}s")

