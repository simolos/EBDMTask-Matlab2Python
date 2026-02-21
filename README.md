# EBDMTask-Matlab2Python
This repository was created for the conversion of the matlab version of the EBDM task into a python one.

## Python

See the [python](python/README.md) directory and readme for information on setting up the python environment.

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


### Keyboard Detection Requirements:

- Non-blocking: Must not freeze or interrupt other processes.
- Accurate timing: Must log precise timestamps for each key event.
- Experimental precision: Must be reliable for behavioral experiments.

Keyboard Detection Methods
1. Callback Function with extern library (https://discourse.psychopy.org/t/gui-controls-with-callback-functions/2439)
Pynput
How it works:
Code reacts automatically to key events (e.g., key press), without manual polling—useful for GUIs or asynchronous tasks.

Limits:
– Less precise timing, can suffer from OS/busy queue delays
– Harder to synchronize with experiment events
– Not compatible with precise frame timing in PsychoPy

2. Polling in Main Experiment Loop with IOHub
How it works:
The main loop checks for key events each frame, while all other processes (display, timers, data) continue to run.

Limits:
– Can miss extremely brief or simultaneous key presses (rare at human speeds)
– Slightly higher CPU usage
– Window must remain focused

3. Global Event Key (PsychoPy) (https://www.psychopy.org/coder/globalKeys.html)
How it works:
Assign a function to a specific key (or key combination).
The function is called automatically when that key is pressed, integrated with PsychoPy’s experiment loop (synchronized with win.flip() and core.wait()).

Limits:
– Only detects key presses (KEYDOWN) for the keyboard—does not detect key releases (KEYUP) (I'm searching there is another solution to detect keyup)
– Cannot measure key hold duration for the keyboard
– For the mouse, press and release events (and durations) are available via getPressed()

Comparison:
More reliable than standard GUI callbacks (Tkinter, PyQt, etc.) because it is designed to be fully compatible and synchronized with PsychoPy’s experimental timing.

Tests results 

1. IOHub Polling (in PsychoPy)

   1.1 Test 1 (Simulation): Randomized key-press schedule via a unittest; showed that a polling interval of ≤ 5 ms yields a timestamp delta of < 5 ms for human tapping rates.
   1.2 Test 2 (Hardware): Real-world tapping with IOHub in PsychoPy; confirmed excellent tracking accuracy.

2. pynput Callbacks

   2.1 Test 1 (Logic): Simulated key-press/un-press sequences; callback-driven detection worked perfectly.
   2.2Test 2 (Comparison vs. Global Key Event): High-frequency tapping in PsychoPy vs. OS-level global events; no lost events, and delays were only marginally above the “true” global event times.


------------------------------------------------------------