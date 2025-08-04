from psychopy import visual, core

class Screens:
    """
    Gestion des écrans/tampons pour paradigmes type Matlab/Psychtoolbox.
    Toutes tailles et positions sont calculées pour garder la même logique que Matlab, quel que soit l'écran.
    """
    def __init__(self, win, gain_screen=1.0):
        self.win = win
        self.gain_screen = gain_screen

        # Résolution écran courante
        self.screen_w, self.screen_h = self.win.size

        # Paramètres de référence Matlab
        self.base_w, self.base_h = 1920*2, 1080*2
        self.scale_x = self.screen_w / self.base_w
        self.scale_y = self.screen_h / self.base_h

        # ----- Variables tirées du Matlab -----
        # Positions et tailles clefs (toujours scaler X/Y séparés)
        self.Y_GOAL = 200 * gain_screen * self.scale_y      # Point haut de la barre (vertical)
        self.Y_HOME = -200 * gain_screen * self.scale_y     # Point bas de la barre (vertical)

        self.x = 300 * gain_screen * self.scale_x           # Décalage choix Oui/Non (horizontal)
        self.y = -30 * gain_screen * self.scale_y           # Décalage vertical base (pour réponses, textes)
        self.sz = 24 * gain_screen * self.scale_y           # Taille police (vertical)
        self.cross_thickness = 4 * gain_screen * self.scale_x
        self.cross_arm = 42 * gain_screen * self.scale_y    # Longueur des bras de croix
        self.choice_sq = 20 * gain_screen                   # Carré de choix Oui/Non (en fait, symétrique)

        self.rect_w = 100 * gain_screen * self.scale_x      # Largeur rectangle vertical central
        self.rect_h = 600 * gain_screen * self.scale_y      # Hauteur rectangle vertical central
    

        # Couleurs
        self.darkgrey = [0.2, 0.2, 0.2]
        self.bargrey = [0.25, 0.25, 0.25]
        self.LIGHT_GREY = [0.9, 0.9, 0.9]
        self.DARK_GREY = [0.6510, 0.6510, 0.6510]
        self.BLACK = [0, 0, 0]

        # Spécifiques VAS
        self.vas_bar_width = 600 * gain_screen * self.scale_x
        self.vas_bar_height = 10 * gain_screen * self.scale_y
        self.vas_label_offset = 40 * self.scale_y

        # ----- Construction des buffers (sous forme de listes d’objets PsychoPy) -----
        self.bBLACK = self._create_black_buffer()
        self.bWHITE = self._create_white_buffer()
        self.bRectCross = self._create_rect_cross_buffer()
        self.bDM = self._create_dm_buffer()
        self.bDMcross = self._create_dmcross_buffer()
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

    # --------- FONCTIONS DE CONSTRUCTION POUR CHAQUE ÉCRAN ---------

    def _create_black_buffer(self):
        return [visual.Rect(self.win, width=self.screen_w, height=self.screen_h, pos=(0,0), fillColor=self.BLACK, lineColor=None)]

    def _create_white_buffer(self):
        big_white = visual.Rect(self.win, width=self.screen_w, height=self.screen_h, pos=(0,0), fillColor=[1,1,1], lineColor=None)
        small_black = visual.Rect(self.win, width=200*self.scale_x, height=200*self.scale_y, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        return [big_white, small_black]

    def _create_rect_cross_buffer(self):
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        return [rect, vert, horiz]

    def _create_dm_buffer(self):
        left_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(-self.x, 40*self.gain_screen*self.scale_y), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        right_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(self.x, 40*self.gain_screen*self.scale_y), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        question = visual.TextStim(self.win, text="La récompense en vaut-elle l'effort ?", pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        yes_txt = visual.TextStim(self.win, text="Oui", pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
        no_txt = visual.TextStim(self.win, text="Non", pos=(self.x, self.y), height=self.sz, color=self.darkgrey)
        return [left_sq, right_sq, question, rect, yes_txt, no_txt]

    def _create_dmcross_buffer(self):
        elems = self._create_dm_buffer().copy()
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        elems.extend([vert, horiz])
        return elems

    def _create_effort_perception_buffer(self):
        bar = visual.Rect(self.win, width=self.vas_bar_width, height=self.vas_bar_height, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        midpoint = visual.Rect(self.win, width=self.vas_bar_height, height=self.vas_bar_height, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        # Titres et labels comme Matlab (positions fidèles)
        title = visual.TextStim(self.win, text="Effort perçu", pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        label_zero = visual.TextStim(self.win, text="0", pos=(-self.vas_bar_width/2, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        label_pas = visual.TextStim(self.win, text="Pas d'effort", pos=(-self.vas_bar_width/2, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        label_max = visual.TextStim(self.win, text="Effort maximum", pos=(self.vas_bar_width/2, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        label_dix = visual.TextStim(self.win, text="10", pos=(self.vas_bar_width/2, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        return [bar, midpoint, title, label_zero, label_pas, label_max, label_dix]

    def _create_taskwait_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        return [rect]

    def _create_taskwaitcross_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        return [rect, vert, horiz]

    def _create_position_fingers_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        text1 = visual.TextStim(self.win, text='Pressez', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        text2 = visual.TextStim(self.win, text='A-Z-E', pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, text1, text2]

    def _create_get_ready_for_ep_buffer(self):
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text='Préparez-vous', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [vert, horiz, txt]

    def _create_success_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text='Succès !', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_failure_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text='Raté !', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_rest_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text='Repos', pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_anticip_buffer(self):
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        vert = visual.Rect(self.win, width=self.cross_thickness, height=self.cross_arm*2, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        horiz = visual.Rect(self.win, width=self.cross_arm*2, height=self.cross_thickness, pos=(0,0), fillColor=self.BLACK, lineColor=None)
        txt = visual.TextStim(self.win, text='Anticipe !', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [rect, vert, horiz, txt]

    def _create_end_of_task_buffer(self):
        # Placement du texte final comme Matlab : [0, 230*gain_screen]
        txt = visual.TextStim(self.win, text='Fin de la tâche', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_prepforer_buffer(self):
        txt = visual.TextStim(self.win, text='Veuillez noter la perception de votre effort...', pos=(0, self.y-10*self.gain_screen*self.scale_y), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_redoep_buffer(self):
        # Comme Matlab : (y + 282*3)
        txt = visual.TextStim(self.win, text='Raté ! Veuillez essayer à nouveau', pos=(0, self.screen_h*0.25*0.85), height=self.sz, color=self.darkgrey)
        return [txt]

    def _create_goep_buffer(self):
        txt = visual.TextStim(self.win, text='Go!!!', pos=(0, self.screen_h*0.25*0.75), height=self.sz, color=self.darkgrey)
        return [txt]
    
    def _create_decision_dynamic_buffer(self, effort_level, rew_t, choice=None):
        left_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(-self.x, 40*self.gain_screen*self.scale_y), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        right_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(self.x, 40*self.gain_screen*self.scale_y), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        question = visual.TextStim(self.win, text="La récompense en vaut-elle l'effort ?", pos=(0, self.screen_h*0.25*0.65), height=self.sz, color=self.darkgrey)
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        yes_txt = visual.TextStim(self.win, text="Oui", pos=(-self.x, self.y), height=self.sz, color=self.darkgrey)
        no_txt = visual.TextStim(self.win, text="Non", pos=(self.x, self.y), height=self.sz, color=self.darkgrey)
        
        rew_text = f"{rew_t} cents"
        bar_y = (effort_level-0.5)*self.rect_h
        effort_bar = visual.Rect(self.win, width=self.rect_w*1.2, height=self.rect_h*0.02, pos=(0, bar_y), fillColor=self.DARK_GREY, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        reward_label = visual.TextStim(self.win, text=rew_text, pos=(self.rect_w*1.5, bar_y), height=self.sz, color=self.BLACK)
       
        # Coche, seulement si un choix est fait
        tick = None
        if choice == "yes":
            left_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(-self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        elif choice == "no":
            right_sq = visual.Rect(self.win, width=self.choice_sq*self.scale_x, height=self.choice_sq*self.scale_y, pos=(self.x, 40*self.gain_screen*self.scale_y), fillColor=self.BLACK, lineColor=self.BLACK, lineWidth=self.cross_thickness)

        # Assemble tous les éléments à draw()
        elems = [rect, left_sq, right_sq, question, yes_txt, no_txt, effort_bar, reward_label]
        if tick is not None:
            elems.append(tick)
        
        return elems

    def _create_reward_buffer(self, rew_t, effort_level):
        bar_y = (effort_level-0.5)*self.rect_h
        rew_text = f"{rew_t} cents"
        reward_label = visual.TextStim(self.win, text=rew_text, pos=(self.rect_w*1.5, bar_y), height=self.sz, color=self.BLACK)
        return [reward_label]
    
    def _create_bar_dynamic_buffer(self, effort_level):
        bar_y = (effort_level-0.5)*self.rect_h
        rect = visual.Rect(self.win, width=self.rect_w, height=self.rect_h, pos=(0,0), lineColor=self.BLACK, lineWidth=self.cross_thickness)
        effort_bar = visual.Rect(self.win, width=self.rect_w*1.2, height=self.rect_h*0.02, pos=(0, bar_y), fillColor=self.DARK_GREY, lineColor=self.BLACK, lineWidth=self.cross_thickness)
        return [rect, effort_bar]



"""

def main():
    # Configure monitor and get true screen resolution
    #mon = monitors.Monitor('testMonitor')
    screen_res = [1280, 720]  # Fallback to 1440x900 if monitor file not set

    # Create PsychoPy window (debug: fullscr=False)
    win = visual.Window(
        size=screen_res,
        units='pix',
        fullscr=True,
        color=(0.8, 0.8, 0.8)
    )

    gain_screen = 1.0
    darkgrey = (-0.2, -0.2, -0.2)
    screens = Screens(win, gain_screen)

    # Simule un effort au centre (y=0), 50 cents, coche sur Oui
    effort_level = 140
    reward_text = "Pour 50 cents"
    choice = "yes"  # Teste aussi "no" ou None

    # Génère les éléments à afficher pour l'écran décision dynamique
    elems = screens._create_decision_dynamic_buffer(effort_level, reward_text, choice)

    # Affiche ce buffer 2 secondes
    for elem in elems:
        elem.draw()
    win.flip()
    core.wait(5.0)
    win.close()
    core.quit()

if __name__ == '__main__':
    main()
"""
