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

    # Use IOHub keyboard events if available
    if io and kb:
        press_time = None
        while clock.getTime() < end_time:
            for ev in kb.getEvents():
                if ev.key == 'escape' and ev.type == ev.KEYBOARD_PRESS:
                    win.close()
                    core.quit()
                    return None, None, None
                if ev.key in keys and ev.type == ev.KEYBOARD_PRESS:
                    press_time = ev.time
                    return ev.key, ev.time, None
                elif ev.key in keys and ev.type == ev.KEYBOARD_RELEASE and press_time is not None:
                    rt = press_time
                    duration = ev.time - press_time
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
        return kb.getEvents()
    return event.getKeys()
