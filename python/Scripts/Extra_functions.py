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

    Actually not used in the code but can be helpful
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


def calibration(win, screens, kb, io, expClock):
    """Quick tapping calibration: counts taps on 'lctrl' over 3 s and derives GV."""
    clock = core.Clock()
    t0 = clock.getTime()
    t1 = 0
    endTime = 3000  # ms
    tap_key = 'lctrl'
    count = 0

    while clock.getTime() - t0 < endTime / 1000:
        _ = poll_keys(kb, io)  # catch ESC early
        for elem in screens.bCalib:
            elem.draw()
        win.flip()

        events = poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if key_name == tap_key and ev.type == 22 and t1 == 0:
                count += 1
                t1 = clock.getTime()
            elif key_name == tap_key and ev.type == 22 and t1 != 0:
                count += 1
            elif key_name == 'escape':
                win.close()
                core.quit()

    GV = count / (endTime / 1000 - t1) * 0.95
    print(f' GV : {GV}')
    return GV
