import pygame
import time
from psychopy import visual, core
from psychopy.hardware import keyboard
from key_tool import key_detector_psychopy
from key_tool import key_detector_pygame
#import tkinter as tk

#Test keyboard_pygame
debug_keyboard_pygame = False;
if debug_keyboard_pygame:
    pygame.init()
    screen = pygame.display.set_mode((400, 300))     # Necessary to use Pygame  
    keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_q]   
    keycode, duration = key_detector_pygame(keys, t_limit=20)
    if keycode:
        print(f"{pygame.key.name(keycode)} pressed during {duration:.4f} s")
    pygame.quit()


#Test psychopy_keyboard
"""
debug_keyboard_psychopy = False;
if debug_keyboard_psychopy:
    win = visual.Window(size=(400, 300))
    target_keys = ['left', 'right', 'q']
    key, duration = key_detector_psychopy(target_keys, t_limit=30, win=win)
    if key is not None:
        print(f"{key} pressed during {duration:.4f} s")
    else:
        print("Not")
    win.close()
"""

debug_keyboard_psychopy = False;
if debug_keyboard_psychopy:
    win = visual.Window([800, 600])
    clock = core.Clock()
    timeout = 5.0

    kb = keyboard.Keyboard()
    press_times = {}
    release_times = {}

    clock.reset()
    while clock.getTime() < timeout:
        
        win.flip()
        
        # 2. Poll keyboard for all events (press and release)
        events = kb.getEvents()
        for ev in events:
            if ev.type == 'KEYDOWN':
                press_times[ev.name] = ev.rt
                print(f"Key {ev.name} pressed at {ev.rt:.3f} s")
            elif ev.type == 'KEYUP':
                release_times[ev.name] = ev.rt
                print(f"Key {ev.name} released at {ev.rt:.3f} s")
                # Calculate and print duration if available
                if ev.name in press_times:
                    duration = ev.rt - press_times[ev.name]
                    print(f"Key {ev.name} held for {duration:.3f} s")


""" Callback function test
def on_key(event):
    print("Key pressed:", event.keysym)

root = tk.Tk()
root.bind("<Key>", on_key_press)  # <-- callback
root.mainloop()
"""
