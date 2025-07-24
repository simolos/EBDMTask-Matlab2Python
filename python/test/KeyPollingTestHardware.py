from psychopy.iohub import launchHubServer
from psychopy import visual, core

def polling_precision_test(poll_interval=0.001, t_limit=10, target_keys=['left', 'right']):
    io = launchHubServer()
    kb = io.devices.keyboard
    win = visual.Window(size=[600, 400], color=[0, 0, 0])
    msg = visual.TextStim(
        win,
        text=f"Polling every {poll_interval*1000:.1f} ms.\nPress/release 'left' or 'right'.\n\nQuit: ESC",
        color=[1, 1, 1]
    )
    msg.draw(); win.flip()

    kb.clearEvents()
    timer = core.Clock()
    data = []

    print(f"Polling interval: {poll_interval*1000:.2f} ms")

    while timer.getTime() < t_limit:
        # Poll for keyboard events at each loop
        events = kb.getEvents()
        loop_now = timer.getTime()
        for ev in events:
            if ev.key in target_keys or ev.key == 'escape':
                diff = loop_now - ev.time
                data.append((ev.key, ev.type, ev.time, loop_now, diff))
                if ev.key == 'escape':
                    # Display results before exiting if ESC is pressed
                    if data:
                        base_diff = data[0][4]
                        print("Event      Type    ts_ioHub     ts_loop      diff_adj (s)")
                        for entry in data:
                            key, typ, ts_io, ts_loop, diff = entry
                            diff_adj = diff - base_diff
                            print(f"{key:<10}{typ:<8}{ts_io:.5f}   {ts_loop:.5f}   {diff_adj:+.6f}")
                    win.close(); io.quit(); core.quit()
                    return data
        core.wait(poll_interval)

    # Display results at the end if time limit is reached
    if data:
        base_diff = data[0][4]
        print("Event      Type    ts_ioHub     ts_loop      diff_adj (s)")
        for entry in data:
            key, typ, ts_io, ts_loop, diff = entry
            diff_adj = diff - base_diff
            print(f"{key:<10}{typ:<8}{ts_io:.5f}   {ts_loop:.5f}   {diff_adj:+.6f}")

    win.close()
    io.quit()
    core.quit()
    return data

if __name__ == '__main__':
    polling_precision_test(poll_interval=0.010, t_limit=15)
