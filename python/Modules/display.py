# utils/display.py

from psychopy import visual, monitors

def create_window(cfg):

    mon = monitors.Monitor("MyMonitor")

    if cfg.fullscreen == "Y":
        win = visual.Window(
            monitor=mon,
            screen=1,
            fullscr=True,
            color=(0.8, 0.8, 0.8),
            units="pix",
        )
        gain_screen = 1

    else:
        win = visual.Window(
            size=(1280, 720),
            monitor=mon,
            screen=0,
            fullscr=False,
            color=(0.8, 0.8, 0.8),
            units="pix",
        )
        gain_screen = 1

    return win, gain_screen