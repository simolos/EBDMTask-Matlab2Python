import pygame
import time
from psychopy import visual
from key_tool import key_detector_psychopy
from key_tool import key_detector_pygame


#Test key_tool
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
debug_keyboard_psychopy = True;
if debug_keyboard_psychopy:
    win = visual.Window(size=(400, 300))
    target_keys = ['left', 'o', 'q']
    key, duration = key_detector_psychopy(target_keys, t_limit=10, win=win)
    if key is not None:
        print(f"{key} pressed during {duration:.4f} s")
    else:
        print("Not")
    win.close()

