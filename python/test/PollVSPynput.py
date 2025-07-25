from psychopy import visual, core, event
from pynput import keyboard
import time

# ——————————————————————————————————————————————————————
# CONSTANTS (all timings in seconds)
POLL_INTERVAL = 0.001       # PsychoPy polling interval
T0 = time.time()            # common reference clock
T_LIMIT = 15                # total test duration
# ——————————————————————————————————————————————————————

# storage for absolute-event timestamps
psy_events = []     # list of (key, t_sys)
pynput_events = []  # list of (key, t_sys)

# --- Pynput listener: record absolute time.time() for each keydown ---
def on_press(key):
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except Exception:
        k = str(key)
    t_sys = time.time()
    pynput_events.append((k, t_sys - T0))
    print(f"[pynput] {k} @ {t_sys - T0:.4f}s")
    if k in ['Key.esc', 'esc']:
        return False

listener = keyboard.Listener(on_press=on_press)
listener.start()

# --- PsychoPy window + polling: record absolute time.time(), not core.Clock() ---
win = visual.Window(color='black', size=(600, 300))
msg   = visual.TextStim(win, text="TAP any key FAST & SHORT!\nESC to quit", pos=(0,0.3))
stats = visual.TextStim(win, text="", pos=(0,-0.1), height=0.07)
timer = core.Clock()

while timer.getTime() < T_LIMIT:
    keys = event.getKeys()  # no timestamp here
    for k in keys:
        if k in ['escape', 'esc']:
            win.close()
            listener.stop()
            break
        t_sys = time.time()
        psy_events.append((k, t_sys - T0))
        print(f"[psychopy] {k} @ {t_sys - T0:.4f}s")

    # live stats on absolute–relative deltas
    npsy = len(psy_events)
    npyn = len(pynput_events)
    psy_deltas = [(psy_events[i][1] - psy_events[i-1][1])*1000
                  for i in range(1, npsy)]
    pyn_deltas = [(pynput_events[i][1] - pynput_events[i-1][1])*1000
                  for i in range(1, npyn)]
    psy_min = min(psy_deltas) if psy_deltas else 0
    pyn_min = min(pyn_deltas) if pyn_deltas else 0

    stats.text = (
        f"Psychopy: {npsy} events (min Δ {psy_min:.1f} ms)\n"
        f"Pynput:  {npyn} events (min Δ {pyn_min:.1f} ms)"
    )
    msg.draw(); stats.draw(); win.flip()

    core.wait(POLL_INTERVAL)

win.close()
listener.stop()

# final summary (absolute times relative to T0)
print(f"\nTotal events: psychopy={len(psy_events)}  pynput={len(pynput_events)}")
if len(psy_events)>1:
    psy_avg = sum(psy_deltas)/len(psy_deltas)
    print(f"Psychopy mean interval: {psy_avg:.2f} ms over {len(psy_deltas)} gaps")
if len(pynput_events)>1:
    pyn_avg = sum(pyn_deltas)/len(pyn_deltas)
    print(f"Pynput mean interval: {pyn_avg:.2f} ms over {len(pyn_deltas)} gaps")

print("\n== Test finished ==")
