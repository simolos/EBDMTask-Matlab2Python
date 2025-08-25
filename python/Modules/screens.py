# comments in English
from psychopy import visual, core
from config import TRANSLATIONS

class Screens:
    """
    Gestion des écrans/tampons pour paradigmes type Matlab/Psychtoolbox.
    Les textes sont tirés de TRANSLATIONS selon la langue (lang='fr' ou 'en').
    """
    def __init__(self, win, gain_screen=1.0, lang='fr'):
        self.win = win
        self.gain_screen = gain_screen
        self.lang = lang  # <- language code ('fr' or 'en')

        # --- helper for translations
        # Returns translated string and formats placeholders if provided
        def _tr(key, **kwargs):
            s = TRANSLATIONS.get(self.lang, {}).get(key, key)
            try:
                return s.format(**kwargs) if kwargs else s
            except Exception:
                return s
        self.tr = _tr

        # Resolution
        self.screen_w, self.screen_h = self.win.size

        #------
        self.base_w, self.base_h = 1920*2, 1080*2
        self.scale_x = self.screen_w / self.base_w
        self.scale_y = self.screen_h / self.base_h
        self.choice_sq = 20 * gain_screen  

        # -----
        self.Y_GOAL = 200 * gain_screen * self.scale_y
        self.Y_HOME = -200 * gain_screen * self.scale_y

        self.x = 300 * gain_screen * self.scale_x
        self.y = -30 * gain_screen * self.scale_y
        self.sz = 24 * gain_screen * self.scale_y
        self.cross_thickness = 8 * gain_screen * self.scale_x
        self.cross_arm = 50 * gain_screen * self.scale_y

        self.rect_w = 130 * gain_screen * self.scale_x
        self.rect_h = 600 * gain_screen * self.scale_y
    
        # Colors
        self.darkgrey = [0.2, 0.2, 0.2]
        self.bargrey = [0.25, 0.25, 0.25]
        self.LIGHT_GREY = [0.9, 0.9, 0.9]
        self.DARK_GREY = [0.6510, 0.6510, 0.6510]
        self.BLACK = [0, 0, 0]

        # 
        self.vas_bar_width = 600 * gain_screen * self.scale_x
        self.vas_bar_height = 10 * gain_screen * self.scale_y

        # ----- Construction des buffers -----
        self.bBLACK = self._create_black_buffer()
        self.bWHITE = self._create_white_buffer()
        self.bRectCross = self._create_rect_cross_buffer()
        self.bEffortPerceptionEval = self._create_effort_perception_buffer()
        self.bTaskWait = self._create_taskwait_buffer()
        self.bTaskWaitCross = self._create_taskwaitcross_buffer()
        self.bPosition_fingers = self._create_position_fingers_buffer()
        self.bGetReadyForEP = self._create_get_ready_for_ep_buffer()
        self.bSuccess = self._create_success_buffer()
        self.bFailure = self._create_failure_buffer()
        self.bRest = self._create_rest_buffer()
        self.bAnticip = self._create_anticip_buffer()
        self.bEndOfTheTask = self._create_end_of_task_buffer()
        self.bPrepForER = self._create_prepforer_buffer()
        self.bRedoEP = self._create_redoep_buffer()
        self.bGoEP = self._create_goep_buffer()
        self.bCalib = self._create_calibration_buffer()

    # --------- BUILDERS ---------

    def _create_black_buffer(self):
        return [visual.Rect(self.win, width=self.screen_w, height=self.screen_h, pos=(0,0), fillColor=self.BLACK, lineColor=None)]

    def _create_white_buffer(self):
        big_white = visual.Rect(self.win, width=self.screen_w, height=self.screen_h, pos=(0,0), fillColor=[1,1,1], lineColor=None)
        small_black = visual.Rect(self.win, width=200*self.scale_x, height=200*self.scale_y, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        return [big_white, small_black]

    def _create_rect_cross_buffer(self):
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        return [rect, vert, horiz]

    def _create_calibration_buffer(self):
        texte = visual.TextStim(self.win, text='Tap as fast as you can', pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        return [rect, texte, vert, horiz]

    def _create_effort_perception_buffer(self):
        # VAS bar + center mark
        bar = visual.Rect(self.win, width=self.vas_bar_width, height=self.vas_bar_height, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        midpoint = visual.Rect(self.win, width=self.vas_bar_height, height=self.vas_bar_height, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        # Labels
        title = visual.TextStim(self.win, text=self.tr('effort_perceived'), pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        # left labels
        label_zero = visual.TextStim(self.win, text="0", pos=(-self.vas_bar_width/2, self.screen_h*0.25*0.88), height=self.sz, color=self.darkgrey)
        label_no = visual.TextStim(self.win, text=self.tr('no_effort'), pos=(-self.vas_bar_width/2, self.screen_h*0.25*0.82), height=self.sz, color=self.darkgrey)
        # right labels
        label_ten = visual.TextStim(self.win, text="10", pos=(self.vas_bar_width/2, self.screen_h*0.25*0.88), height=self.sz, color=self.darkgrey)
        label_max = visual.TextStim(self.win, text=self.tr('max_effort'), pos=(self.vas_bar_width/2, self.screen_h*0.25*0.82), height=self.sz, color=self.darkgrey)
        return [bar, midpoint, title, label_zero, label_no, label_max, label_ten]

    def _create_taskwait_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        return [rect]

    def _create_taskwaitcross_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        return [rect, vert, horiz]

    def _create_position_fingers_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        text1 = visual.TextStim(self.win, text=self.tr('press'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        text2 = visual.TextStim(self.win, text=self.tr('fingers'), pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)  # "A-W-E"
        return [rect, vert, horiz, text1, text2]

    def _create_get_ready_for_ep_buffer(self):
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text=self.tr('ready'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [vert, horiz, txt]

    def _create_success_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text=self.tr('success'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_failure_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text=self.tr('failure'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_rest_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text=self.tr('rest'), pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_anticip_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text=self.tr('anticip'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_end_of_task_buffer(self):
        txt = visual.TextStim(self.win, text=self.tr('end_task'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_prepforer_buffer(self):
        txt = visual.TextStim(self.win, text=self.tr('get_effort_note'), pos=(0, self.y-10*self.gain_screen*self.scale_y), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_redoep_buffer(self):
        txt = visual.TextStim(self.win, text=self.tr('failed_try'), pos=(0, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_goep_buffer(self):
        txt = visual.TextStim(self.win, text=self.tr('go'), pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [txt]

    # --------- DYNAMIC BUILDERS (use formatted translations) ---------
    
    def _create_dm_buffer(self, flag_InvYesNo=False):
        left_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(-self.x, 40*self.gain_screen*self.scale_y),  fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        right_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(self.x, 40*self.gain_screen*self.scale_y),  fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        question = visual.TextStim(self.win, text=self.tr('reward_question'), pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        if flag_InvYesNo:
            yes_txt = visual.TextStim(self.win, text=self.tr('yes'), pos=(self.x, self.y), height=self.sz, color=self.darkgrey)
            no_txt = visual.TextStim(self.win, text=self.tr('no'), pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
        else: 
            yes_txt = visual.TextStim(self.win, text=self.tr('yes'), pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
            no_txt = visual.TextStim(self.win, text=self.tr('no'), pos=(self.x, self.y), height=self.sz, color=self.darkgrey)
        return [left_sq, right_sq, question, rect, yes_txt, no_txt]

    def _create_dmcross_buffer(self, flag_InvYesNo=False):
        elems = self._create_dm_buffer(flag_InvYesNo=flag_InvYesNo).copy()
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        elems.extend([vert, horiz])
        return elems

    def _create_decision_dynamic_buffer(self, effort_level, rew_t, choice=None, flag_InvYesNo=False):
        # Choice boxes
        left_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(-self.x, 40*self.gain_screen*self.scale_y), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        right_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(self.x, 40*self.gain_screen*self.scale_y), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        # Static texts
        question = visual.TextStim(self.win, text=self.tr('reward_question'), pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        
        if flag_InvYesNo:
            yes_txt = visual.TextStim(self.win, text=self.tr('yes'), pos=(self.x, self.y), height=self.sz, color=self.darkgrey)
            no_txt = visual.TextStim(self.win, text=self.tr('no'), pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
        else:
            yes_txt = visual.TextStim(self.win, text=self.tr('yes'), pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
            no_txt = visual.TextStim(self.win, text=self.tr('no'), pos=(self.x, self.y), height=self.sz, color=self.darkgrey)

        # Target bar and reward label
        bar_y = (effort_level-0.5)*self.rect_h
        effort_bar = visual.Rect(self.win, width=self.rect_w*1.1, height=self.cross_thickness, pos=(0, bar_y), fillColor=self.bargrey, lineColor=self.bargrey, lineWidth=self.cross_thickness)
        reward_label = visual.TextStim(self.win, text=self.tr('reward_for', val=rew_t), pos=(self.rect_w*1.5, bar_y), height=self.sz, color=self.BLACK)

        # Tick selected
        if flag_InvYesNo:
            if choice == "yes":
                right_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)
            elif choice == "no":
                left_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(-self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        else:
            if choice == "yes":
                left_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(-self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)
            elif choice == "no":
                right_sq = visual.Rect(self.win, width=self._sq_w(), height=self._sq_h(), pos=(self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)

        return [rect, left_sq, right_sq, question, yes_txt, no_txt, effort_bar, reward_label]

    def _create_reward_buffer(self, rew_t, effort_level):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), fillColor=None, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        bar_y = (effort_level-0.5)*self.rect_h
        reward_label = visual.TextStim(self.win, text=self.tr('reward_for', val=rew_t), pos=(self.rect_w*1.5, bar_y), height=self.sz, color=self.BLACK)
        return [rect, reward_label]
    
    def _create_bar_buffer(self, effort_level):
        bar_y = (effort_level-0.5)*self.rect_h
        effort_bar = visual.Rect(self.win, width=self.rect_w*1.1, height=self.cross_thickness, pos=(0, bar_y), fillColor=self.bargrey, lineColor=self.bargrey, lineWidth=self.cross_thickness)
        return [effort_bar]

    def _create_cursor_dynamic_buffer(self, cursor):
        bar_y = (cursor-0.5)*self.rect_h
        effort_bar = visual.Rect(self.win, width=self.rect_w*1.1, height=self.cross_thickness/2, pos=(0, bar_y), fillColor=self.DARK_GREY, lineColor=self.DARK_GREY, lineWidth=self.cross_thickness/3)
        return [effort_bar]

    def _create_ffeedback_buffer(self, final_reward):
        # "Total = {val} CHF"
        reward_label = visual.TextStim(self.win, text=self.tr('total', val=final_reward), pos=(0, 0), height=self.sz, color=self.BLACK)
        return [reward_label]

    # --- small helpers
    def _sq_w(self): return self.choice_sq * self.scale_x
    def _sq_h(self): return self.choice_sq * self.scale_y
