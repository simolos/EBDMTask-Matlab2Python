# Scripts/test_keyboard.py
from psychopy import visual, core
from Modules.keyboard import init_keyboard, clear_events, wait_for_keys

def main():
    # 1) Open a minimal PsychoPy window so that key events are captured
    win = visual.Window(size=(400, 300), units='pix', fullscr=False, color=(0, 0, 0))
    win.flip()  # make it visible and give it focus

    # 2) Initialize the keyboard via IOHub server
    kb, io = init_keyboard(use_iohub=False, use_hub=True)
    clear_events(kb, io)

    print("Press 'space' within 5 seconds...")
    # 3) Wait for space press+release
    name, rt, duration = wait_for_keys(['space'], timeout=5, kb=kb, io=io)

    if name:
        dur_str = f", Duration: {duration:.3f}s" if duration is not None else ""
        print(f"Key: {name}, RT: {rt:.3f}s{dur_str}")
    else:
        print("No key press detected.")

    # Clean up
    win.close()
    if io:
        io.quit()
    core.quit()

if __name__ == '__main__':
    main()
