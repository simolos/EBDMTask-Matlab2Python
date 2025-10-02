
# Installation

Open VSC and cd to /EBDMTask-Matlab2Python

Python environment:
	- Use Python 3.10 or 3.11 for compatibility with PsychoPy 2023.2 --> brew install python@3.11

		Check installed version by running in the terminal: python3 --version 

  	- Create a virtual environment before installing dependencies:

    		Linux / macOS:
      			python3.11 -m venv venv
      			source venv/bin/activate

		(if you already have a venv folder in your path, you only need to activate)

    		Windows:
      			python -m venv venv
      			venv\Scripts\activate


	- Upgrade pip, setuptools, and wheel:

		pip install --upgrade pip setuptools wheel


Dependencies:
  	- All required packages are listed in requirements.txt
  	- Install them by running in the terminal:

		pip install -r python/requirements.txt

	- Check with 
		pip show psychopy



PsychoPy and IOHub:
  - This project depends on PsychoPy with IOHub enabled for precise keyboard handling.
  - IOHub provides low-level access to keyboard events with millisecond precision.
  - On some systems, IOHub requires extra configuration:

    macOS:
      - Grant Accessibility permissions to PsychoPy in System Preferences (System Settings > Privacy & Security > Accessibility > + > ".../venv/bin/psychopy)

    Linux:
      - You may need elevated privileges if the OS restricts access to low-level input devices.

    Windows:
      - Usually works without changes, but administrative rights may be required in locked environments.

Fallback mode:
  - If IOHub cannot be initialized, the code will automatically fall back to the standard PsychoPy "event" module.
  - This fallback mode works but offers lower temporal precision.

Recommendation:
  - Always test the installation before running a full experiment.
  - Run a short trial and verify that key presses are detected correctly.

--------------------------------
## Usage (running the code)

Entry point:
  - Run the experiment from the project root using Python.
  - Main script: main.py

Basic command:
  - Syntax:
      python main.py -s <SUBJECT_ID> -b <BLOCK_ID> -mtf <MTF>[options...]

Mandatory arguments:
  - -s, --subject-id (str):
      Description: Participant identifier.
      Example: S01
  - -b, --block-id (str):
      Description: Block identifier for the session.
      Example: B1

  - -mtf, --MTF (int):
      Description: Maximum Tapping Frequency of the participant (from calibration)

Output info (websocket, triggerDBS, triggerTI, ...)
  - -ws, --ws_streaming (str):
      Choices: {"true"; "false"}
      Default: "false"
      Description: enable streaming through websocket 

Core options (CLI):
  - -n, --nTrials (int):
      Default: 32
      Description: Total number of trials in the block (should be a multiple of 16).
  - -e, --nEffortTrials (int):
      Default: 8
      Description: Number of trials that include the effort phase.
  - -p, --population (int):
      Choices: {1, 2, 3}
      Default: 1
      Description:
        1: healthy timings
        2: older adults timings
        3: DBS-implanted timings
  - -l, --language (str):
      Choices: {"en", "fr"}
      Default: "en"
      Description: UI language for on-screen texts.
  - -fullscr, --fullscreen (str):
      Choices: {"Y", "N"}
      Default: "N"
      Description:
        Y: Fullscreen window on current monitor.
        N: Windowed mode (default size is set in main.py).
  - -o, --output_dir (str):
      Default: "results"
      Description: Directory where data files are written.
  - -t, --stimulation (str):
      Default: "none"
      Description: Free text flag for stimulation condition (metadata only).
  - --eyetracker (flag):
      Default: disabled
      Description: If present, enables eyetracker timing-specific durations.
  - --debug (flag):
      Default: disabled
      Description: If present, enables debug mode in parts of the code (shorter waits, extra logs).
  - --test-dev (flag):
      Default: disabled
      Description: Developer/testing flag (reserved for local tweaks).
  - -m, --mode (int):
      Choices: {0, 1, 2}
      Default: 0
      Description:
        0: single-key mode (Ctrl)
        1: multi-finger posture (hold A+W+E) + tap F
        2: hold Ctrl + tap Ctrl (backward-compat)
  - -chmap, --ChangeMappingYes (str):
      Choices: {"N", "Y"}
      Default: "N"
      Description:
        If "Y", the "Yes" choice is mapped to the RIGHT box; if "N", "Yes" is on the LEFT.

What the options control at runtime:
  - Trial generation:
      Module: general_trial.GetTrialCondition
      Uses: --nTrials, --nEffortTrials, --population
  - Per-trial durations:
      Module: config.get_task_duration
      Uses: --population, --eyetracker
  - Window configuration:
      Fullscreen vs windowed based on --fullscreen.
      Base monitor is created in main.py via psychopy.monitors.Monitor('MyMonitor').
  - Language:
      On-screen labels and messages come from config.TRANSLATIONS keyed by --language.
  - Keyboard handling:
      IOHub is initialized in keyboard.init_keyboard(); if unavailable, falls back to psychopy.event.
      The --mode flag selects the tapping/posture logic used in effort_new.py.
  - Decision mapping:
      --ChangeMappingYes determines left/right mapping for the "Yes" label and accepted key.

Minimal examples:
  - Windowed, English, quick demo block:
      python main.py -s S01 -b B1 -n 16 -e 4 -p 1 -l en -fullscr N
  - Fullscreen, French, standard block:
      python main.py -s S02 -b B2 -n 32 -e 8 -p 1 -l fr -fullscr Y
  - Older population timings with right-side "Yes":
      python main.py -s S03 -b B3 -n 32 -e 8 -p 2 -l en -chmap Y
  - Multi-finger posture mode:
      python main.py -s S04 -b B4 -n 32 -e 8 -p 1 -m 1

Runtime controls:
  - Quit:
      Press ESC at any time.
      Behavior: a QuitSignal/SystemExit is handled; the program attempts to save data and then closes the window.
  - Keyboard polling:
      IOHub events are polled every loop; if IOHub fails, the fallback uses psychopy.event.getKeys().

Default timing and rates:
  - Refresh pacing for effort frames is set by Hz in main.py (default 60).
  - GV (gain/normalization for cursor) is fixed to 7 in main.py by default.
  - Optional calibration exists (calibration function in main.py) but is not enabled by default; enabling it requires editing main.py to call calibration() and set GV accordingly.

Output behavior (where files go and when they are written):
  - Location: --output_dir (default "results"); the directory is created if it does not exist.
  - Timing: Data is written once at the end of the run or upon clean quit handling.
  - Format: By default main.py calls DataRecorder.save_all(..., fmt="xlsx"). To change to "csv" or "mat", edit the save_and_quit(...) call in main.py (parameter all_fmt).

WebSocket streaming (optional):
  - Client: ws_stream.TrialStreamer
  - Default URI: ws://127.0.0.1:8765/trials (hardcoded in main.py)
  - Requirement: If no server is listening at that URI, connection may fail during startup.
  - To disable or change:
      Option 1: Edit main.py to comment out streamer.start() and all streamer.send_* calls.
      Option 2: Replace the default URI with the address of your server before running.
  - Use-case: Sending compact JSON events (trial metadata, markers) and optionally binary arrays.

Troubleshooting quick notes:
  - "IOHub not available": The code falls back to psychopy.event; verify IOHub permissions (see Step 2).
  - WebSocket connection errors at startup:
      Run/point to a valid server at ws://127.0.0.1:8765/trials or disable streaming in main.py.
  - PsychoPy window errors in fullscreen:
      Try -fullscr N to confirm windowed mode works, then adjust monitor settings in PsychoPy.

-------------------------
### Project structure

Overview:
  - This section describes the modules, their responsibilities, and how they interact at runtime.
  - Use it to locate where to change parameters, UI, timing, and data handling.

Modules:
  config.py:
    Purpose: Command-line parsing, global constants, translations, durations, and trial table factory.
    Key objects and functions:
      - parse_args(): builds argparse.Namespace with all CLI flags.
      - TRANSLATIONS: language dictionary used by Screens.
      - get_task_duration(flag_eyetracker, flag_population) -> dict: per-phase durations (ms).
      - init_trials(n_trials, cond_e_r, dur_prep_dm, dur_prep_ep) -> DataFrame: creates the trial table.
      - keys_choice, combo: keyboard mapping constants.
    Edit here:
      - Add/modify CLI arguments.
      - Update language strings (TRANSLATIONS).
      - Adjust default durations logic per population.

  general_trial.py (or Modules/generation_trial.py):
    Purpose: Generate balanced Effort × Reward conditions and EP flags.
    Key function:
      - GetTrialCondition(n_trials, n_effort_trials, flag_population) -> (cond_er, indx_effort_trials)
    Edit here:
      - Effort/reward grids, balancing strategy, and EP scheduling rules.

  screens.py:
    Purpose: Build all static/dynamic visual buffers (PsychoPy stimuli).
    Key class:
      - Screens(win, gain_screen, lang):
          - Pre-built buffers: bRectCross, bTaskWait, bTaskWaitCross, bSuccess, bFailure, bRest, bAnticip, bEndOfTheTask, bGetReadyForEP, bGoEP, bCalib, etc.
          - Dynamic builders: _create_dm_buffer(), _create_dmcross_buffer(), _create_decision_dynamic_buffer(), _create_reward_buffer(), _create_bar_buffer(), _create_cursor_dynamic_buffer(), _create_ffeedback_buffer()
    Edit here:
      - Layout, sizes, positions, text styling, colors, and any custom visual elements.

  decision.py:
    Purpose: Decision phase loop with strict “post-response” display window.
    Key function:
      - decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, TaskTimings, flag_MapYesAtRight)
        - Reads per-trial durations, shows DM UI, polls keys, records Acceptance/DecisionTime.
        - Displays a “tick” (selected box) for AFTER_S seconds after a valid response, then exits.
    Edit here:
      - Key mapping logic, choice-to-label side mapping, timing constraints, event streaming markers.

  effort_new.py:
    Purpose: Effort pipeline (positioning, get-ready, effort frames, blank, feedback, pupil baseline).
    Main entry:
      - effort_phase(streamer, i, win, screens, kb, io, expClock, dur, GV, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed, KEYBOARD_MODE)
    Subroutines:
      - init_cursor_matrix(task_ms, Hz, n_trials) -> (CURSOR, n_frames)
      - hand_positioning_phase(...): waits until the correct combo is held for a minimum time.
      - get_ready_phase(...): jitter + anticipation detection.
      - effort_production_phase(...): per-frame key onset detection, cursor computation, drawing, and pacing at Hz.
      - blank_phase(...), feedback_phase(...), pupil_baseline_phase(...)
    Edit here:
      - Mode-specific tapping/posture detection, cursor normalization, success thresholds, binary event logic.

  keyboard.py:
    Purpose: Input layer abstraction (IOHub primary, event module fallback).
    Key items:
      - QuitSignal(Exception): raised on ESC (or 'q' if implemented).
      - init_keyboard(use_iohub=True) -> (kb, io): starts IOHub and returns keyboard device.
      - poll_keys(kb, io) -> List[Event]: non-blocking keyboard poll; raises QuitSignal on ESC.
      - clear_events(kb, io): clears buffered events.
      - wait_for_keys(...): utility (not used by default main loop).
    Edit here:
      - ESC handling policy, extra keys, filtering, or alternative input devices.

  data.py:
    Purpose: Accumulate trial records and save across formats.
    Key class:
      - DataRecorder(output_dir, prefix):
          - add_trial(dict): append trial row.
          - save_all(fmt, trials_df, cursor, keypr, tasktimings, Hz, GV, csv_mode="long") -> str
            - xlsx: multi-sheet (trials, cursor, keypr, timings, meta)
            - csv: long format frames merged with per-trial columns
            - mat: requires scipy.io.savemat
    Edit here:
      - Output schema changes, additional metadata, or saving strategy.

  ws_stream.py:
    Purpose: Background WebSocket client for JSON events and binary arrays.
    Key class:
      - TrialStreamer(uri, proto="v1"):
          - start(), close()
          - send_event(event, payload_dict)
          - send_array(name, np_array, trial, meta=None)
    Edit here:
      - Server URI, protocol fields, payload schema, reconnect policy.

  utils_ws.py (or ws_utils.py):
    Purpose: Trial-row serialization helpers for streaming.
    Key functions:
      - trial_row_payload(trials, i, include=None, exclude=None, drop_none=False) -> dict
      - _to_json_scalar(x) -> json-safe scalar
    Edit here:
      - Include/exclude logic, column renaming, or type coercion rules.

  main.py:
    Purpose: Orchestrates the full run (init, window, keyboard, trials loop, decision, effort, save).
    Pipeline outline:
      - Parse args → durations → conditions → trials
      - Init recorder + streamer
      - Open PsychoPy window + build Screens
      - Init keyboard (IOHub preferred)
      - Pre-trial fixation (StartBlock)
      - For each trial:
          - Stream minimal trial payload
          - Blank1 → decision_phase(...)
          - If scheduled and accepted: effort_phase(...)
          - Accumulate TotalGain (if no anticipation)
          - Add enriched trial row (Hz, GV) to recorder
      - Final feedback display
      - Close streamer, save_all(...), close window, quit
    Edit here:
      - Run-time choices (fullscreen, Hz, GV), which formats to save, how/when to stream, error handling.

Runtime data shapes and types:
  - trials (pandas.DataFrame):
      Columns: trial, effort, reward, efftested, rewtested, durPrep_DM, durPrep_EP, DecisionTime, ReactionTimeEP, Acceptance, success, Anticipation_DM, Anticipation_EP, KeyPositionTime, ...
      Indexing: zero-based for code, but "trial" column is 1..N for human-readable IDs.
  - CURSOR (numpy.ndarray):
      Shape: (n_frames, n_trials)
      Type: float, NaN where frames/trials are not applicable.
  - keypr (numpy.ndarray):
      Shape: (n_frames, n_trials)
      Type: float, entries in {0.0, 1.0} for onset detection.

Call graph (high level):
  main.py
    -> config.parse_args()
    -> config.get_task_duration()
    -> general_trial.GetTrialCondition()
    -> config.init_trials()
    -> DataRecorder(...)
    -> TrialStreamer.start()
    -> Screens(...)
    -> keyboard.init_keyboard()
    -> decision_phase(...)
    -> effort_phase(...)
    -> DataRecorder.save_all(...)
    -> TrialStreamer.close()
    -> core.quit()

Where to change common settings:
  - CLI defaults and new flags: config.parse_args()
  - Visual layout and text labels: screens.py (plus TRANSLATIONS in config.py)
  - Timing presets by population: config.get_task_duration()
  - Effort/Reward grids and balancing: general_trial.GetTrialCondition()
  - Input handling and ESC behavior: keyboard.py
  - Output format and location: data.py and save_and_quit(...) in main.py
  - WebSocket endpoints and payloads: ws_stream.py and utils_ws.py

-------------------
#### Data output:

Overview:
  - All trial-level records are accumulated during runtime and saved at the end (or on clean quit).
  - The save routine is centralized in data.DataRecorder.save_all(...).
  - Default format in main.py is XLSX; you can switch to CSV or MAT by editing save_and_quit(..., all_fmt=...).

Where files are written:
  - Directory: --output_dir (default "results"); created if it does not exist.
  - Filenames: <prefix>_<timestamp>.<ext>
      prefix: "<subject_id>_<block_id>" (set in main.py)
      timestamp: YYYYMMDD_HHMMSS
  - Examples:
      results/S01_B1_20250101_101500.xlsx
      results/S01_B1_20250101_101500.csv
      results/S01_B1_20250101_101500.mat

XLSX format (multi-sheet):
  - Function: DataRecorder.save_all(fmt="xlsx", ...)
  - Sheets:
      trials:
        - One row per trial with decision/effort outcomes and timings.
        - Typical columns (subset):
            trial (1..N)
            effort, reward, efftested, rewtested
            durPrep_DM, durPrep_EP
            DecisionTime
            Acceptance (1 yes, 0 no, -1 timeout)
            ReactionTimeEP
            Anticipation_DM (0/1), Anticipation_EP (0/1)
            KeyPositionTime
            success (1 success, 0 fail, -1 big fail)
            Hz, GV (added when recording enriched rows)
      cursor:
        - Framewise cursor matrix as wide format
        - Shape: n_frames rows × n_trials columns; float in [0,1] with NaN padding
      keypr:
        - Framewise key onset matrix as wide format
        - Shape: n_frames rows × n_trials columns; values {0.0, 1.0} or NaN
      timings:
        - TaskTimings as two columns: ["timestamp", "event"]
        - Event names are appended throughout the run (e.g., "T0 Start DM", "T0 Start EP")
      meta:
        - Single row with run metadata:
            prefix, Hz, GV, nFrames, nTrials

CSV format (long, framewise):
  - Function: DataRecorder.save_all(fmt="csv", Hz=<required>, ...)
  - Structure:
      - Long table merging framewise signals with per-trial fields.
      - Columns include:
          trial (1..N)
          frame (0..n_frames-1)
          time_s (= frame / Hz)
          cursor (float)
          keypr (0.0 or 1.0)
          ...plus all per-trial columns merged on "trial"
  - Notes:
      - Hz must be provided to compute time_s.
      - This file can be large for long tasks (n_trials × n_frames rows).

MAT format (for MATLAB/Octave):
  - Function: DataRecorder.save_all(fmt="mat", ...)
  - Requirements: scipy installed (scipy.io.savemat)
  - Variables saved:
      CURSOR: float array (n_frames × n_trials)
      KEYPR: float array (n_frames × n_trials)
      Hz: scalar
      GV: scalar
      prefix: string
      trials: struct-like dict of arrays (one array per column of the pandas DataFrame)
      TaskTimings: Nx2 cell-like array (timestamps and labels) if present

When data are added:
  - rec.add_trial(trial_dict):
      - Called during the loop to capture trial-level states.
      - After each trial, an enriched row (with Hz, GV) is appended.
  - Final save:
      - In the finally block of main.py:
          streamer.close()
          save_and_quit(..., all_fmt="xlsx")

How to change the output format:
  - Edit main.py in the finally block, call:
      save_and_quit(..., all_fmt="csv")
      or
      save_and_quit(..., all_fmt="mat")
  - For CSV "long" format: no extra change needed (implemented by default).
  - For MAT: ensure scipy is installed (see requirements).

Column reference (common per-trial columns):
  - Identifiers:
      trial
  - Stimulus parameters:
      effort, reward, efftested, rewtested
      durPrep_DM, durPrep_EP
  - Decision phase outputs:
      DecisionTime
      Acceptance (1, 0, or -1 if no response)
      Anticipation_DM (0/1)
  - Effort phase outputs:
      ReactionTimeEP
      Anticipation_EP (0/1)
      success (1 / 0 / -1)
      KeyPositionTime
  - Run-level augmentation:
      Hz, GV (added to the recorded trial rows late in the loop)

Size considerations:
  - XLSX:
      - Convenient for inspection; multiple sheets separate concerns.
      - Suitable for moderate datasets; very large runs may be slower to open.
  - CSV (long):
      - Best for large-scale analysis and direct import into pandas/R.
      - Potentially very large files due to framewise rows.
  - MAT:
      - Best for MATLAB analysis pipelines; preserves native arrays and struct fields.

Quick verification checklist after a run:
  - Confirm a new file exists in --output_dir with the expected timestamp and extension.
  - Open XLSX:
      - Check that "trials" has N rows.
      - Check that "cursor"/"keypr" dimensions match expected n_frames × n_trials.
      - Check "timings" contains chronological events.
  - For CSV:
      - Verify time_s increases within each trial and resets across trials as expected.
  - For MAT:
      - Load in MATLAB and confirm fields exist: CURSOR, KEYPR, trials, Hz, GV, TaskTimings (if used).

---------------------
##### Customization

Goal:
  - This step explains where and how to modify the code to adapt timing, stimuli, input logic, output formats, and streaming.
  - All paths below refer to modules in this repository.

Experimental design (effort × reward):
  File: Modules/generation_trial.py (or general_trial.py)
  Function: GetTrialCondition(n_trials, n_effort_trials, flag_population)
  What to change:
    - Effort grid: eff_proposed = np.array([...])
    - Reward grid: rew_proposed = np.array([...])
    - Balancing rules: selection and shuffling strategy for EP vs DM trials
  Notes:
    - The function returns cond_er (N×3) and indx_effort_trials (indices of EP trials).
    - Integrity asserts ensure counts match CLI flags; update them if you change constraints.

Per-phase durations (ms) by population:
  File: config.py
  Function: get_task_duration(flag_eyetracker, flag_population) -> dict
  Keys typically used:
    - "Blank1", "DM_Preparation", "DM", "TimeAfterDMade",
      "TimeAfterPositionRight", "GetReadyForEP", "EP_Preparation",
      "Task", "Blank2", "Reward", "TimeForPupilBaselineBack",
      "FinalFeedback", "StartBlock"
  What to change:
    - Update per-population values.
    - Add/remove keys only if you also update all call-sites that reference them.

Language and on-screen texts:
  File: config.py
  Object: TRANSLATIONS
  What to change:
    - Edit strings for keys such as 'yes', 'no', 'reward_for', etc.
    - Add new keys if you reference them from screens.py; keep the same keys across languages.

Visual layout, sizes, colors:
  File: screens.py
  Class: Screens
  Primary controls:
    - Scaling and geometry: scale_x, scale_y, rect_w, rect_h, cross_thickness, cross_arm, choice_sq, vas_bar_width/height
    - Colors: darkgrey, bargrey, UI_LIGHT_GREY, MOVING_BAR_GREY, BLACK
    - Text sizes and positions: sz, x, y, computed positions inside each _create_* method
  What to change:
    - Modify constants at __init__ for global layout changes.
    - Modify individual _create_* builders to alter specific buffers (e.g., decision boxes, reward label positions).
  Caution:
    - Keep consistency between target bar, cursor bar, and reward label positions (they rely on rect_w/rect_h and scale_*).

Keyboard mapping and modes:
  File: config.py
  Constants: keys_choice, combo
    - keys_choice: ["left", "right"] → decision keys; do not change names unless you also adapt decision_phase logic.
    - combo: {"q", "z", "e"} → multikey posture set (mode 1).
  File: main.py (CLI)
  Flag: -m / --mode
    - 0: single-key (Ctrl)
    - 1: combo + tap (A/W/E + tap F as implemented)
    - 2: hold Ctrl + tap Ctrl (compat mode)
  Where used:
    - effort_new.py: hand_positioning_phase(), get_ready_phase(), effort_production_phase()
  What to change:
    - Adjust tap_key and posture logic in effort_new.py to match your device/keyboard layout.

Decision mapping (left/right "Yes"):
  File: main.py (CLI) and decision.py
  Flag: -chmap / --ChangeMappingYes {"N","Y"}
  Where used:
    - decision_phase(...) and Screens dynamic builders
  What to change:
    - If you add more layouts, propagate new flags through Screens and decision_phase.

Anticipation detection:
  File: effort_new.py
  Functions:
    - get_ready_phase(...): sets trials['Anticipation_EP']=1 based on KEY_PRESS/KEY_RELEASE depending on mode.
  What to change:
    - Switch detection to stricter or laxer rules (e.g., enforce no activity window, use different keys, or both press and release).

Cursor normalization and success thresholds:
  File: effort_new.py
  Functions:
    - effort_production_phase(...):
        cursor_pos = (((mean_onsets * Hz) / GV) - 0.3) / 0.7 → clamp to [0,1]
    - feedback_phase(...):
        success = 1 if tap_rate_norm >= eff_t else (-1 if tap_rate_norm < 0.7 * eff_t else 0)
  What to change:
    - Adjust the linear mapping (offset/slope) if you recalibrate GV or redefine effort scale.
    - Change success boundaries (e.g., replace 0.7 with another threshold, or add graded feedback levels).

Frame rate (Hz) and gain (GV):
  File: main.py
  Variables:
    - Hz = 60 (default)
    - GV = 7 (default)
  Calibration (optional):
    - Function: calibration(...) exists but is not called by default.
    - To enable: call GV = calibration(win, screens, kb, io, expClock) before trials; store GV for the run.
  What to change:
    - If your display runs at another refresh rate, set Hz accordingly to keep pacing and time_s correct.
    - If sensor/keypress dynamics change, adjust GV or enable calibration.

Saving format and location:
  File: main.py (save_and_quit call)
  Parameter:
    - all_fmt: "xlsx" (default), "csv", or "mat"
  File: data.py
  Class: DataRecorder
  What to change:
    - Switch output format by changing all_fmt.
    - Extend meta fields or add extra sheets/columns in DataRecorder.save_all.

Streaming configuration (WebSocket):
  File: main.py and ws_stream.py
  Default client:
    - TrialStreamer("ws://127.0.0.1:8765/trials")
  What to change:
    - Replace the URI with your server address.
    - To disable, comment out streamer.start() and send_event/send_array calls in main.py.
  Payload selection:
    - File: utils_ws.py (or ws_utils.py)
    - Function: trial_row_payload(..., include=None, exclude=None, drop_none=False)
    - To restrict columns sent:
        Example in main.py:
          include = ["trial", "efftested", "rewtested"]
          payload = trial_row_payload(trials, i, include, drop_none=True)

Window mode and monitor:
  File: main.py
  Flags:
    - -fullscr Y|N
  Objects:
    - monitors.Monitor('MyMonitor')
  What to change:
    - Provide your calibrated monitor profile via PsychoPy Monitor Center and use its name here.
    - Adjust the window size in the windowed branch if needed.

Debug and logging:
  Files: main.py, keyboard.py, decision.py, effort_new.py
  Flags:
    - --debug, --test-dev
  What to change:
    - Add logging.debug/info calls where you need more visibility.
    - Keep ESC handling consistent (QuitSignal) and ensure try/except/finally always attempts saving.

CLI defaults:
  File: config.py
  Function: parse_args()
  What to change:
    - Add new flags or adjust defaults.
    - Remember to propagate new flags to modules that require them (e.g., pass through main.py to decision/effort).

Sanity checks and assertions:
  Where:
    - GetTrialCondition integrity asserts
    - main.py argument checks
  What to change:
    - Update or add asserts to match your modified design (e.g., new constraints on counts or grids).

-----------------------
###### Technical notes

Purpose:
  - Summarize critical implementation details, performance guidelines, and reproducibility tips.
  - Focus on how the code behaves on different systems and how to maintain timing fidelity.

PsychoPy version and Python:
  - Recommended Python: 3.10 or 3.11
  - Recommended PsychoPy: >= 2023.2
  - Rationale: matches APIs used in visual/core/monitors/event/iohub and recent bugfixes.

Display timing and frame pacing:
  - Refresh pacing during the effort phase is controlled by:
      Hz (target frame rate, default 60) in main.py
      oneframe = 1.0 / Hz
      Per-frame loop enforces pacing using core.wait(remain)
  - To adapt to a 75/120/144 Hz monitor:
      Set Hz in main.py to your display refresh.
      Validate that the measured per-frame interval ~ 1/Hz using simple logging.
  - VSync:
      Ensure VSync is enabled in your graphics driver; PsychoPy window defaults usually sync to refresh.
      If you see tearing or unstable timing, force VSync on in the OS/driver.

win.flip() cost:
  - Typical cost is 8–16 ms on 60 Hz displays (one refresh).
  - Never do heavy CPU work between draw() calls and win.flip().
  - Pre-build fixed stimuli (as done in screens.py) and reuse objects each frame to minimize GC/allocations.

CPU/GPU power settings:
  - Windows:
      Set Power Plan to “High Performance”.
      Disable adaptive power saving on the GPU.
  - macOS:
      Disable automatic graphics switching on dual-GPU laptops (if available).
  - Linux:
      Prefer proprietary drivers for NVIDIA; keep compositor settings stable across runs.

Monitor calibration:
  - Use PsychoPy Monitor Center to define a calibrated monitor (size, distance, luminance/gamma if available).
  - Replace 'MyMonitor' in main.py with your calibrated profile name.
  - If you modify pixel geometry (rect_w, rect_h, scale_x/y) in screens.py, test that positions scale correctly in fullscreen and windowed modes.

Fullscreen vs windowed:
  - Fullscreen:
      Use -fullscr Y for experiments; ensures consistent timing and avoids OS window manager interference.
  - Windowed:
      Use -fullscr N only for debugging; size is set in main.py, and timing may be less precise.

Reproducibility:
  - Fix random seeds if you require repeatable condition orders:
      Add np.random.seed(<int>) early in main.py (before calls to GetTrialCondition).
  - Record config:
      The code already embeds subject_id, block_id, and timestamps in filenames.
      Consider saving CLI args to a JSON sidecar for complete provenance.

Error handling and data safety:
  - Quit behavior:
      Pressing ESC raises QuitSignal/SystemExit; the finally block attempts to save all data before quitting.
  - Try/except:
      main.py wraps the entire run; unhandled exceptions log a traceback and still trigger save_and_quit().
  - Recommendation:
      Keep output_dir on a local SSD to avoid I/O stalls; backup raw files after each session.

WebSocket streaming:
  - If no server listens at ws://127.0.0.1:8765/trials the connection attempt can fail at start.
  - This does not prevent the experiment from running; you can disable TrialStreamer in main.py for offline runs.
  - Network jitter has no effect on timing because rendering and input are local; streaming is fire-and-forget.

Large outputs:
  - XLSX is convenient but slower for very large runs; prefer CSV if runs are long (large n_frames × n_trials).
  - CSV “long” can exceed millions of rows; ensure sufficient disk space and consider chunked analysis.

Antivirus and overlays:
  - Disable overlays (screen recorders, FPS counters, GPU overlays) during sessions.
  - Exclude the project directory from real-time antivirus scanning to reduce random I/O stalls.

Time base consistency:
  - PsychoPy core.Clock() is used for intra-phase timing; expClock.getTime() is logged for event markers.
  - Do not mix OS time functions with core.Clock() for timing-critical code.
  - If you add new timers, instantiate them immediately before the measured phase to avoid drift.

Testing checklist before data collection:
  - Verify IOHub initialization and ESC quit behavior (handled in keyboard.init_keyboard and poll_keys).
  - Run a 2–3 trial smoke test in fullscreen to confirm:
      Key detection works in chosen mode (-m 0/1/2).
      Decision tick holds for the configured AFTER_S window.
      Effort cursor moves and pacing matches Hz.
      Output file is created with all expected sheets/columns.

--------------------------------------------
####### Streaming server (FastAPI WebSocket)

Purpose:
  - Provide a lightweight server to receive real-time trial events (JSON) and binary arrays from the client (main.py via TrialStreamer).
  - Persist control events to JSON Lines and arrays to .npy files for later inspection and syncing with external tools.

File:
  - main_server.py

Endpoint:
  - WebSocket route: /trials
  - Default host/port when run via uvicorn example below: 0.0.0.0:8765
  - Health endpoints (HTTP):
      GET /         -> basic status JSON
      GET /health   -> {"ok": true}

Persistence layout:
  - Root save directory: ./session_data (auto-created)
  - Control JSONL: session_data/control_events.jsonl
  - Array headers JSONL: session_data/array_headers.jsonl
  - Binary arrays (.npy): session_data/<name>/<name>_trial<id>_<timestamp>.npy
    Notes:
      - One subfolder per array "name" (e.g., "cursor_trace").
      - Filenames include trial number and a timestamp to avoid overwrites.

Message protocol (client -> server):
  - Control messages (text JSON):
      Any event (e.g., "trial_record", "Start DM", "Decision") is appended to control_events.jsonl.
      The server responds with an "ack" JSON: {"event":"ack","ack_of":"<event>",...}.
  - Binary arrays:
      Two frames per transfer:
        1) Text JSON header: {"event":"array_header","name":<str>,"trial":<int>,"dtype":<str>,"shape":[...], "order":"C"|"F", "meta":{...}}
        2) One binary frame: raw bytes of the array
      The server reconstructs the array using dtype/shape/order and saves it under session_data/<name>/.
      The server sends an "ack" with name/trial/shape/dtype after saving.

How to run the server:
  - Option A (uvicorn CLI):
      uvicorn main_server:app --host 0.0.0.0 --port 8765 --log-level info
  - Option B (python -m, if you add an entrypoint block):
      python -m uvicorn main_server:app --host 0.0.0.0 --port 8765 --log-level info
  - Option C (direct script if __main__ is present):
      python main_server.py
    Notes:
      - Use --reload during development, not in production.
      - Ensure that the port (default 8765) is open and not blocked by a firewall.

How to connect from the client (this repository):
  - The client class ws_stream.TrialStreamer connects to a URI like ws://127.0.0.1:8765/trials.
  - In main.py the default is:
      streamer = TrialStreamer("ws://127.0.0.1:8765/trials")
      streamer.start()
  - To change the server address or port:
      Edit the URI passed to TrialStreamer(...) in main.py before running.

Quick test workflow:
  1) Start the server:
       uvicorn main_server:app --host 0.0.0.0 --port 8765 --log-level info
  2) In another terminal, run the experiment client:
       python main.py -s Test -b demo -n 4 -e 2 -l en -fullscr N
  3) Observe the server logs:
       - Incoming control events (e.g., "trial_record") are acknowledged and appended to control_events.jsonl.
       - Any received arrays are saved to session_data/<name>/.
  4) Inspect outputs:
       - tail -n +1 session_data/*.jsonl
       - ls session_data/<name>/ and np.load(...) in a Python shell to inspect arrays.

Troubleshooting:
  - Client fails to connect at start:
      Ensure the server is running and the URI matches (host, port, and /trials path).
  - "binary_without_header" error on server:
      The client must send an "array_header" JSON immediately before the binary frame.
  - Reshape failures:
      Ensure header "shape" and "dtype" match the actual bytes length sent by the client.
  - File permissions:
      Confirm the process can write to ./session_data or change SAVE_DIR in main_server.py.

Operational notes:
  - The server is stateless and accepts a single stream; it acknowledges messages but does not enforce ordering beyond the header+binary pairing.
  - Network issues do not affect client-side timing in PsychoPy; rendering and input polling are local. The client uses fire-and-forget semantics for events and arrays.

--------------------------------------------
Notes on Improvements
This codebase is functional and tested, but it can be improved.  
The current design favors clarity over optimization, and some routines (e.g., frame loops, IOHub handling, WebSocket streaming) could be refactored for efficiency and robustness.  
Contributions are welcome to extend functionality, improve modularity, or adapt the code to specific experimental setups.  
