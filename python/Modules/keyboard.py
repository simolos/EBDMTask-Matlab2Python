# Modules/keyboard.py
"""
Keyboard handling module using PsychoPy IOHub for precise key timing.
This module is responsible solely for keyboard initialization and event retrieval.
PsychoPy window creation and display management should be handled elsewhere (e.g., display.py).
"""
import logging
from typing import Optional, Tuple, List
from psychopy import visual, core, event

try:
    from psychopy.iohub import launchHubServer
    IOHUB_AVAILABLE = True
except ImportError:
    IOHUB_AVAILABLE = False

#=======CONSTANTS========
KEY_PRESS = 22
KEY_RELEASE = 23
#========================

class QuitSignal(Exception):
    """Raised when the user requests to quit (e.g., ESC or 'q')."""
    pass

def init_keyboard(use_iohub: bool = True, use_hub: bool = False) -> Tuple[Optional[object], Optional[object]]:
    """
    Initialize IOHub server keyboard interface.

    Args:
        use_iohub: if True, launch IOHub server.
        use_hub: alias for use_iohub compatibility.

    Returns:
        kb: IOHub keyboard device or None
        io: IOHub connection object or None
    """
    if IOHUB_AVAILABLE and (use_hub or use_iohub):
        io = launchHubServer()
        kb = io.devices.keyboard
        kb.clearEvents()
        logging.info("IOHub keyboard initialized.")
        return kb, io
    else:
        logging.warning("IOHub not available: falling back to PsychoPy event module.")
        return None, None


def clear_events(kb: Optional[object], io: Optional[object]) -> None:
    """
    Clear previous keyboard events.
    """
    if io:
        io.clearEvents()
    elif kb:
        try:
            kb.clearEvents()
        except Exception:
            pass
    else:
        event.clearEvents(eventType='keyboard')


def wait_for_keys(
    keys: List[str],
    timeout: float,
    kb: Optional[object],
    io: Optional[object]
) -> Tuple[Optional[str], Optional[float], Optional[float]]:
    """
    Wait for a key press followed by release within timeout.

    Args:
        keys: list of key names to listen for
        timeout: maximum time in seconds
        kb: IOHub keyboard device
        io: IOHub connection

    Returns:
        name: key name or None
        rt: time of key press or None
        duration: time between press and release or None
    """
    clock = core.Clock()
    end_time = clock.getTime() + timeout
    start_time = clock.getTime()

    # Use IOHub keyboard events if available
    if io and kb:
        press_time = None
        while clock.getTime() < end_time:
            for ev in kb.getEvents():
                if ev.key == 'escape' and ev.type == KEY_PRESS:
                    win.close()
                    core.quit()
                    return None, None, None
                if ev.key in keys and ev.type == KEY_PRESS and press_time is None:
                    press_time = clock.getTime() 
#                   return ev.key, ev.time, None
                elif ev.key in keys and ev.type == KEY_RELEASE and press_time is not None:
                    rt = press_time
                    duration = clock.getTime() - press_time
                    logging.debug(f"Key {ev.key}: rt={rt:.4f}, dur={duration:.4f}")
                    return ev.key, rt, duration
            core.wait(0.001)
        return None, None, None

    # Fallback to PsychoPy event module
    result = event.waitKeys(
        keyList=keys,
        maxWait=timeout,
        timeStamped=core.Clock()
    )
    if result:
        name, rt = result[0]
        logging.debug(f"Fallback key: {name}, rt={rt:.4f}")
        return name, rt, None
    return None, None, None


def poll_keys(kb: Optional[object], io: Optional[object]) -> List[object]:
    """
    Poll keyboard events without blocking.

    Returns:
        List of event objects.
    """

    if io and kb:
        events = kb.getEvents()
        for ev in events:
            key = ev.key if hasattr(ev, 'key') else ev
            if key == 'escape':
                raise QuitSignal()
                return 0
        return events
    return event.getKeys()

"""
def check_quit_events(kb, io):
    #Poll keys and raise QuitSignal if quit key is pressed.
    events = poll_keys(kb, io)  # your existing helper
    for ev in events:
        key = ev.key if hasattr(ev, 'key') else ev
        if key in ('escape', 'q'):
            raise QuitSignal()
    return events
"""
"""
if __name__ == "__main__":
    # Create a PsychoPy window for event capture
    win = visual.Window(
        size=(800, 600),
        color=[0, 0, 0],
        units='pix',
        fullscr=False
    )

    # Initialize keyboard (fallback to PsychoPy event module)
    kb, io = init_keyboard(use_iohub=True, use_hub=True)
    
        # Display instructions
    instructions = visual.TextStim(
        win,
        text="Press one of the keys ['a', 'b', 'escape'] within 5 seconds...",
        color=[1, 1, 1]
    )
    instructions.draw()
    win.flip()

    key, rt, duration = wait_for_keys(
        keys=['a', 'b', 'escape'],
        timeout=10.0,
        kb=kb,
        io=io
    )

    # Close window before printing results
    win.close()

    if key:
        print(f"Key pressed: {key}")
        print(f"Reaction time: {rt:.4f} seconds")
        if duration is not None:
            print(f"Key held duration: {duration:.4f} seconds")
    else:
        print("No key press detected within timeout.")

    core.quit()
"""
