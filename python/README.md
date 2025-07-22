# Python

GOAL: implement a structured version of the EBDM task in Python based on the matlab implementation.

## Setup

This project uses `pipenv` to configure the local development in a virtual environment.
This ensures that dependencies are managed correctly across different installations.

First, make sure [Python version 3.10](https://www.python.org/downloads/release/python-3100/) is configured and [Pipenv](https://pipenv.pypa.io/en/latest/) is installed.

Then, go to this directory in a terminal and run `pipenv install`.

To add further dependencies, use `pipenv install <package>` with the necessary package - for example, `pipenv install pygame` would add the dependency for the [pygame](https://github.com/pygame/pygame) library which makes certain things like keyboard interactions very simple.

## Structure

TODO: define the main modules and functions of the task. As first version, only the logic, timings and log of the matlab version need to be implemented in python. This means that the graphical components will be handled in a second stage, as they are not strictly required for the VR implementation (the screen buffers will be developed by ENG). 

Example of structure definition - Decision-making phase
1. For Dur_PrepDM (e.g. 1s): check if either the left or right arrow are pressed
   1.1 If so, log the time of press and mark anticipation for the current trial
2. For maximum Dur_DM (e.g. 4s): check if either the left or right arrow are pressed
   2.1 If one of the keys has been pressed, log the time of press and the decision encoded
   2.2 Stop checking if the keys are pressed
3. For Dur_PostDecision (e.g. 1s): wait (in further development this will be the moment of displaying the selection)
4. Wait Dur_ITI

- Effort production phase
1. For Dur_PrepEP (e.g. 1s)
   1.1 During this time, check if any effort key is pressed, if a key is pressed, 
   log anticipation for the current trial
   1.2 If anticipation was detected, mark the trial as "anticipation error" -> next trial
2. For Dur_EP (e.g. 3s)
   2.2 Log the reaction time of the first key press
   2.1 Continuously record the relevant key presses, log the timestamp and update 
3. At the end of Dur_EP, calculate the performance for the current trial
   3.1 Compute the total number of key presses
   3.2 Calculate the average frequency during the effort window
4. Determine the outcome
   4.1 If the performance meets or exceeds the required threshold, mark the trial as "success"
   4.2 If the performance is below the threshold but above the MIN_THRESHOLD, mark as "failure"
   4.3 If the performance is far below the MIN_THRESHOLD, mark as "big failure"
5. Wait DUR_ITI

- Feedback phase
1. Based on the trial outcome (success, failure, big failure, or anticipation)
   1.1 Prepare the feedback message and visual (e.g. text, color, reward/penalty)
2. For Dur_Feedback (e.g. 2s)
   2.1 Show the result and earned/lost amount to the participant
3. Log the feedback type and any associated values (e.g. gain/loss) in the trial data
4. Wait Dur_ITI

- Trial generation 
1. Set the total number of trials and number of effort trials for the block
2. Generate all possible combinations of effort and reward levels, according to the experimental design
3. Assign trials as "effort" or "decision-only" based on n_Effort_Trials and flags (e.g. population type)
4. Randomize the order of trials
5. For each trial, define and store:
   5.1 Trial index
   5.2 Effort level
   5.3 Reward level
   5.4 Trial type (effort or decision-only)
   5.5 Any relevant flags or conditions (e.g. language, population, etc.)
6. Prepare the full list (or DataFrame) of trials for the experiment

- General trial loop
1. For each trial in the list of trials:
   1.1 Display fixation or inter-trial screen for Dur_Fixation
   1.2 Run Decision-making phase
   1.3 If decision is "accept" and the trial is an effort trial:
       1.3.1 Run Effort-making phase
   1.4 Otherwise, skip effort phase
   1.5 Save trial data (decision, performance, outcome, timings, etc.)
   1.6 Run Feedback phase
2. Give the final result (gain)
3. Save all experiment data


###
Keyboard detection requirements:

1.  Must be non-blocking (should not interrupt or freeze other processes)
2.  Must accurately measure key press timing (precise timestamp for each key event)
3.  Must be precise and reliable (suitable for experimental timing)

Ideas: 

1. Polling the keyboard in the main experiment loop is non-blocking:
   the loop continuously checks for key presses each frame,
   but the rest of the code (display, timers, data recording) keeps running at the same time.
   Nothing freezes while waiting for a key press.
   Limits:
   Polling only detects events during each loop iteration, so very brief or simultaneous key presses might be missed;
   it can increase CPU usage and depends on the program’s focus and timing.
   In effort production phase, fast tapping cannot be detected. 

   pseudo-code : 

   WHILE (elapsed time < timeout):
    // 1. Draw and update stimuli
    Draw stimuli (if needed)
    Update the display (flip window)

    // 2. Poll keyboard for new key events this frame
    Get list of key events from keyboard
    FOR each event in key events:
        IF event is key press ("KEYDOWN"):
            Record the time of key press for this key
            Print which key was pressed and when
        ELSE IF event is key release ("KEYUP"):
            Record the time of key release for this key
            Print which key was released and when
            IF key was previously pressed:
                Calculate duration as (release time - press time)
                Print how long the key was held

    // 3. (Optional) Do other operations, such as check sensors or update data
    END WHILE

    

2. A callback function lets the code automatically react to events (like a key press) 
   without constantly checking for them—ideal  for GUI apps or when asynchronous response is needed.
   Limits:
   Callbacks are less precise for timing, can introduce unpredictable delays (if the OS queue is busy), and are harder to synchronize with experimental events compared to polling in a controlled main loop.
   Can not be synchronized with Psychopy. 