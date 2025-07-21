# config.py
"""
All constants, parameters, texts, paths, and options for the experiment.
"""

# Timings (seconds)
DUR_PREP_DM = 1.0
DUR_DM = 4.0
DUR_POST_DECISION = 1.0
DUR_ITI = 1.0

# Keys (PsychoPy version)
DECISION_KEYS = ['left', 'right']
QUIT_KEY = 'q'

# Decision information 
decision_result = {
    #anticipation
    "anticipation": False,           # Anticipation or not 
    "antic_time": None,              # If anticipation, time reaction with key_pressed_time
    "antic_key_pressed": None,       # If anticipation, key_pressed_time
    "antic_decision_result": None    # If anticipation, choice

    #decision
    "decisio,": False,             # Decision or not 
    "dec_time": None,              # If decision, time reaction with key_pressed_time
    "dec_key_pressed": None,       # If decision, key_pressed_time
    "dec_result": None             # If decision, choice
}

# Messages
# To do later

"""
# General
N_TRIALS = 30
SCREEN_SIZE = [800, 600]
FONT_SIZE = 30
"""
