import time
from psychopy import visual, core
from psychopy.iohub import launchHubServer

# Function to run a hardware polling test for keypress timing using ioHub
# and compare ioHub timestamps to system time.time() timestamps.
def run_comparison_test(target_keys=['left', 'right'], t_limit=30.0):
    """
    Polls the keyboard via ioHub, records both ioHub and OS timestamps for
    press/release, and prints their durations and difference.

    Parameters:
    target_keys (list): Key names to detect (lowercase, e.g., ['left','right']).
    t_limit (float): Max time to wait for events, in seconds.
    """
    # Launch ioHub for high-precision input
    io = launchHubServer()
    kb = io.devices.keyboard

    # Create a PsychoPy window
    win = visual.Window(size=[800, 600], color=[0, 0, 0])
    instruction = visual.TextStim(
        win,
        text="Focus this window.\nPress and hold 'left' or 'right'.\nRelease to end.\n(30s timeout)",
        color=[1, 1, 1]
    )
    instruction.draw()
    win.flip()

    # Clear stale events and start timer
    kb.clearEvents()
    timer = core.Clock()

    print("Waiting for key press...")
    press_io = press_os = None
    key_name = None

    # Wait for key press
    while timer.getTime() < t_limit:
        events = kb.getEvents()
        for ev in events:
            if ev.type == 22 and ev.key in target_keys:
                key_name    = ev.key
                press_io    = ev.time       # ioHub timestamp
                press_os    = time.time()   # real OS timestamp
                print(f"PRESS  -> ioHub: {press_io:.5f}s | time.time(): {press_os:.5f}s")
                break
        if press_io is not None:
            break
        core.wait(0.001)

    if press_io is None:
        print("No key press detected within time limit.")
        win.close(); io.quit(); core.quit()
        return

    print("Waiting for key release...")
    release_io = release_os = None

    # Wait for key release
    while timer.getTime() < t_limit:
        events = kb.getEvents()
        for ev in events:
            if ev.type == 23 and ev.key == key_name:
                release_io  = ev.time
                release_os  = time.time()
                print(f"RELEASE-> ioHub: {release_io:.5f}s | time.time(): {release_os:.5f}s")
                break
        if release_io is not None:
            break
        core.wait(0.001)

    if release_io is None:
        print("No key release detected within time limit.")
    else:
        dur_io = release_io - press_io
        dur_os = release_os - press_os
        diff   = dur_os - dur_io
        print(f"\nDuration (ioHub):     {dur_io:.5f}s")
        print(f"Duration (time.time): {dur_os:.5f}s")
        print(f"Difference:           {diff:.5f}s")

    # Clean up
    win.close()
    io.quit()
    core.quit()


if __name__ == '__main__':
    run_comparison_test()
