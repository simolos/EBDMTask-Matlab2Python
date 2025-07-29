#enable C-level backtraces
import faulthandler; faulthandler.enable()

# PsychoPy imports
from psychopy import core, visual, event
#asyncio + websockets
import asyncio, websockets, time, json

# --- parameters ---
DURATION = 8.0
WS_URI   = "ws://127.0.0.1:8000/ws"

async def run_test():
    #  connect to WS
    async with websockets.connect(WS_URI) as ws:
        #  open PsychoPy window
        win = visual.Window([800,600], color='black')
        intro = visual.TextStim(
            win,
            text="Tap any key to start\nThen tap as fast as possible for 8s",
            color='white'
        )
        intro.draw(); win.flip()
        event.waitKeys()

        first_tap_time = None
        count = 0
        counter = visual.TextStim(win, text="0", color='white')

        # loop until DURATION after first tap
        while True:
            keys = event.getKeys()
            now = time.time()

            for k in keys:
                #quit immediately if ESC
                if k in ['escape','esc']:
                    win.close()
                    return

                # first tap → set origin t0
                if first_tap_time is None:
                    first_tap_time = now
                    rel = 0.0
                else:
                    rel = now - first_tap_time

                #  increment and send tap info
                count += 1
                await ws.send(json.dumps({
                    "type":       "tap",
                    "tap_number": count,
                    "timestamp":  rel
                }))

                #  update PsychoPy counter
                counter.text = str(count)
                counter.draw(); win.flip()

            #  break 8s after first tap
            if first_tap_time is not None and now - first_tap_time >= DURATION:
                break

            core.wait(0.005)

        #  signal trial end with total duration
        await ws.send(json.dumps({
            "type":      "trial_end",
            "timestamp": DURATION
        }))

        #  feedback
        freq = count / DURATION
        feedback = visual.TextStim(
            win,
            text=f"Total taps: {count}\nFrequency: {freq:.2f} taps/s",
            color='white'
        )
        feedback.draw(); win.flip()

        # wait for ESC to quit
        exit_msg = visual.TextStim(
            win,
            text="Press ESC to exit",
            pos=(0,-0.3), color='white'
        )
        exit_msg.draw(); win.flip()
        while 'escape' not in event.getKeys():
            core.wait(0.1)

        win.close()

if __name__ == "__main__":
    asyncio.run(run_test())
