class UIConfig:
    MENU_PLAY = (300, 200, 200, 60)
    MENU_LEVELS = (300, 280, 200, 60)
    MENU_LEADERS = (300, 360, 200, 60)
    MENU_EXIT = (300, 440, 200, 60)

    GAME_UNDO = (10, 60, 80, 35)
    GAME_REDO = (100, 60, 80, 35)
    GAME_RESET = (10, 105, 80, 35)
    GAME_EXIT = (100, 105, 80, 35)

    WIN_NEXT = (250, 350, 300, 60)
    WIN_MENU = (250, 430, 300, 60)

    BACK_BTN = (20, 20, 100, 40)
    PREVIEW_START = (300, 520, 200, 50)

    LEVEL_BTN_BASE = (300, 180, 200, 50)
    LEVEL_BTN_GAP = 70

    @staticmethod
    def get_level_rect(index):
        x, y, w, h = UIConfig.LEVEL_BTN_BASE
        return (x, y + index * UIConfig.LEVEL_BTN_GAP, w, h)