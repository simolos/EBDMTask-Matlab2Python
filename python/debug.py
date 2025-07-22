#Test of global event key 
from psychopy import core, visual, event

win = visual.Window([600, 400], color='gray')
text = visual.TextStim(win, text="Click and hold a mouse button\nRelease to see duration\nPress Q or ESC to quit.")
mouse = event.Mouse()
clock = core.Clock()
clock.reset()  
prev_pressed = [0, 0, 0]
press_times = [None, None, None]
button_names = ['Left', 'Middle', 'Right']

while True:
    text.draw()
    win.flip()
    keys = event.getKeys()
    if 'q' in keys or 'escape' in keys:
        print("Experiment terminated.")
        win.close()
        core.quit()
    curr_pressed = mouse.getPressed()
    for i in range(3):  # 0: left, 1: middle, 2: right
        # Button just pressed
        if curr_pressed[i] and not prev_pressed[i]:
            press_times[i] = clock.getTime()
            print(f"{button_names[i]} button pressed at {press_times[i]:.3f} s")
        # Button just released
        elif not curr_pressed[i] and prev_pressed[i]:
            release_time = clock.getTime()
            pt = press_times[i]
            if pt is not None:
                print(f"{button_names[i]} button released after {release_time - pt:.3f} s")
            press_times[i] = None
        prev_pressed[i] = curr_pressed[i]
 