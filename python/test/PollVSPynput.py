from psychopy import visual, core, event
from pynput import keyboard
import threading
import time

t0 = time.time()
psy_events = []
pynput_events = []

# --- Pynput thread: logs every keydown (no duplicate per frame) ---
def on_press(key):
    t = time.time()
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except Exception:
        k = str(key)
    # Log all key presses 
    pynput_events.append((k, t-t0, t))
    print(f"[pynput] {k} @ {t-t0:.4f}s")
    if k in ['Key.esc', 'esc']:
        return False  # Stop listener on escape

listener = keyboard.Listener(on_press=on_press)
listener.start()

# --- PsychoPy window (non-blocking, polling all keys) ---
win = visual.Window(color='black', size=(600, 300))
msg = visual.TextStim(win, text="TAP the SPACE (or any key) as FAST and SHORT as possible!\nESC to quit", pos=(0,0.3))
stats = visual.TextStim(win, text="", pos=(0,-0.1), height=0.07)
timer = core.Clock()
t_limit = 15
last_npsy = 0
last_npyn = 0

while timer.getTime() < t_limit:
    keys = event.getKeys(timeStamped=True)
    for k_tuple in keys:
        k, t_psy = k_tuple
        if k in ['escape', 'esc']:
            win.close()
            listener.stop()
            break
        psy_events.append((k, t_psy, time.time()))
        print(f"[psychopy] {k} @ {t_psy:.4f}s")
    # Live display
    npsy = len(psy_events)
    npyn = len(pynput_events)
    # Compute min interval between events for each method
    delta_psy = min([psy_events[i][1]-psy_events[i-1][1] for i in range(1, npsy)], default=0)
    delta_pyn = min([pynput_events[i][1]-pynput_events[i-1][1] for i in range(1, npyn)], default=0)
    stats.text = f"Psychopy : {npsy} events (min Δ: {delta_psy*1000:.1f} ms)\nPynput : {npyn} events (min Δ: {delta_pyn*1000:.1f} ms)"
    msg.draw(); stats.draw(); win.flip()
    core.wait(0.002)
    if npsy != last_npsy or npyn != last_npyn:
        last_npsy, last_npyn = npsy, npyn
    if not listener.running:
        break

win.close()
listener.stop()

print(f"\nTotal events: psychopy={len(psy_events)}  pynput={len(pynput_events)}")
if len(psy_events) > 1:
    print("Psychopy min intervals (ms):", [round((psy_events[i][1]-psy_events[i-1][1])*1000,2) for i in range(1,len(psy_events))][:10])
if len(pynput_events) > 1:
    print("Pynput min intervals (ms):", [round((pynput_events[i][1]-pynput_events[i-1][1])*1000,2) for i in range(1,len(pynput_events))][:10])

print("\n== Test finished ==")
