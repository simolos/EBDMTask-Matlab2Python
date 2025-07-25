import pygame
import time
from psychopy import visual, core, event
# Warning cannot be synchronized with Psychopy, must be changed after 

def key_detector_pygame(target_keys, t_limit):
#target_keys: the list of keys you want to detect (e.g., [pygame.K_LEFT, pygame.K_RIGHT]).
#t_limit: the maximum time (in seconds) to wait for a key press before timing out.

    t_start = None
    current_key = None
    start_timer = time.time();

    running = True
    while running:

        if (time.time() - start_timer > t_limit):
            running = False;
            return  None, None 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in target_keys:
                    t_start = time.time()
                    current_key = event.key
            
            elif event.type == pygame.KEYUP:
                if event.key == current_key and t_start is not None:
                    t_pressed = time.time() - t_start;
                    running = False;
                    return event.key, t_pressed
        pygame.time.wait(5)                       # Stop Pygame for 5 ms, to not block the CPU

def key_detector_psychopy(target_keys, t_limit, win):
    """
    - target_keys: list of string names, e.g. ['left', 'right', 'q']
    - t_limit: maximum waiting time (in seconds)
    - win: PsychoPy Window object (for focus)
    """
    clock = core.Clock()
    t_start = None
    current_key = None

    clock.reset()
    while clock.getTime() < t_limit:

        keys = event.getKeys(keyList=target_keys + ['escape'], timeStamped=clock)
        if keys:
            # keys is a list of (keyname, timestamp)
            k, t_down = keys[0]
            if k == 'escape':
                win.close()
                core.quit()
            t_start = t_down
            current_key = k
    
            while True:
                still_pressed = event.getKeys(keyList=[current_key])
                if not still_pressed:
                    t_up = clock.getTime()
                    return current_key, t_up - t_start
                core.wait(0.01)

        core.wait(0.01)
    return None, None
