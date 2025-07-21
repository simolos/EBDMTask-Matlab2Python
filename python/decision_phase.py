from psychopy import core, visual, event
import config

def decision_phase():

    # Screen of the effort and the gain

    # Prep_decision_phase -->
    clock = core.clock();
    result = decision_result;

    key, time_pressed = key_detector_psychopy(DECISION_KEYS, DUR_PREP_DM);
    if key:
        result["anticipation"] = True;
        result["antic_time"] = core.clock() - clock;
        result["antic_key_pressed"] = time_pressed;
        result["antic_decision_result"] = key;
    
    # Dcision_making_phase -->
    clock = core.clock();

    key, time_pressed = key_detector_psychopy(DECISION_KEYS, DUR_DM);
    if key:
        result["decision"] = True;
        result["dec_time"] = core.clock() - clock;
        result["dec_key_pressed"] = time_pressed;
        result["dec_result"] = key;

    core.wait(DUR_POST_DECISION);
    

    
        




    



 
    