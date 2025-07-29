import faulthandler; faulthandler.enable()     # enable C-level backtraces on crash

# imports for PsychoPy and pynput
from psychopy import visual, core, event
from pynput import keyboard

# small asyncio WebSocket client
import asyncio, websockets, json, time

# constants
T_LIMIT = 10        # durée du test (s)
URI     = "ws://127.0.0.1:8000/ws"

# ——————————————————————————————————————————————————————
# stockage des timestamps
pynput_events = []  # (key, t)
psy_events    = []  # (key, t)

# — pynput callback — 
def on_press(key):
    t = time.time()
    try:
        k = key.char
    except AttributeError:
        k = str(key)
    pynput_events.append((k, t))
    print(f"[pynput] {k} @ {t:.4f}")
    if k in ['Key.esc', 'esc']:
        return False

# — wrapper asyncio pour envoyer un ping après test —
async def send_summary():
    async with websockets.connect(URI) as ws:
        # juste un ping
        await ws.send(json.dumps({"type":"ping", "timestamp":time.time()}))
        print("Ping envoyé, je ferme la connexion WS")
        await ws.close()

# — main —
def main():
    # start pynput listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # create PsychoPy window
    win = visual.Window([400,200], color='black')
    msg = visual.TextStim(win, text="Press any key...\nESC to quit", color='white')
    timer = core.Clock()

    while timer.getTime() < T_LIMIT:
        # PsychoPy polling
        keys = event.getKeys()
        for k in keys:
            t = time.time()
            psy_events.append((k, t))
            print(f"[psychopy] {k} @ {t:.4f}")
            if k in ['escape', 'esc']:
                timer.add(T_LIMIT)  # force exit
        msg.draw(); win.flip()
        core.wait(0.01)

    win.close()
    listener.stop()

    # finally send a WS summary
    asyncio.run(send_summary())

    print("Terminé sans crash")

if __name__ == "__main__":
    main()
