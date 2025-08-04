# display.py
from psychopy import visual, core


class Display:
    """
    Manage PsychoPy window and stimulus presentation.
    """
    def __init__(self, debug=False):
        # Window parameters
        self.win = visual.Window(
            size=(800, 600) if debug else (1920, 1080),
            units='pix',
            fullscr=not debug,
            color=(0, 0, 0)
        )
        self.debug = debug
        self.fixation = visual.TextStim(self.win, text='+', height=50, color='white')
        # Define other stimulus templates here (e.g., text, image)

    def show_fixation(self, duration: float):
        """
        Display a fixation cross for a given duration (in seconds).
        """
        self.fixation.draw()
        self.win.flip()
        core.wait(duration)

    def show_text(self, text: str, duration: float, height: int = 40, color: str = 'white'):
        """
        Display a text stimulus for a given duration.
        """
        stim = visual.TextStim(self.win, text=text, height=height, color=color)
        stim.draw()
        self.win.flip()
        core.wait(duration)

    def clear(self):
        """
        Clear the window buffer without flipping to the screen.
        """
        self.win.clearBuffer()

    def flip_and_wait(self, duration: float):
        """
        Flip the window to show drawn stimuli and wait for duration.
        """
        self.win.flip()
        core.wait(duration)

    def close(self):
        """
        Close the PsychoPy window and quit.
        """
        self.win.close()
        core.quit()