import curses
import time


def render_border(window, left='|', right='|', top='-', bottom='-', 
                  top_left='+', top_right='+', bottom_left='+', bottom_right='+'):
    """
    Render a border on a curses window.
    
    Args:
        window: curses window object
        left: Left border character (default: '|')
        right: Right border character (default: '|')
        top: Top border character (default: '-')
        bottom: Bottom border character (default: '-')
        top_left: Top-left corner character (default: '+')
        top_right: Top-right corner character (default: '+')
        bottom_left: Bottom-left corner character (default: '+')
        bottom_right: Bottom-right corner character (default: '+')
    """
    if window:
        try:
            window.border(left, right, top, bottom, top_left, top_right, 
                         bottom_left, bottom_right)
        except curses.error:
            pass


class WindowManager:
    """Manages curses window initialization and configuration."""
    
    def __init__(self):
        self.screen = None
        self.colors_initialized = False
    
    def initialize(self):
        """Initialize curses screen."""
        self.screen = curses.initscr()
        curses.noecho()
        curses.start_color()
        curses.curs_set(0)
        
        if curses.has_colors():
            curses.use_default_colors()
            self.colors_initialized = True
    
    def cleanup(self):
        """Clean up curses screen."""
        if self.screen:
            curses.endwin()
    
    def get_size(self):
        """Get screen dimensions."""
        if self.screen:
            return self.screen.getmaxyx()
        return (0, 0)
    
    def init_color_pairs(self):
        """Initialize color pairs for the game."""
        if not self.colors_initialized:
            return
        
        # Menu colors
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
        
        # Game colors
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)  # Food
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)  # Snake
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)  # Score background
        curses.init_pair(7, curses.COLOR_WHITE, -1)  # Default text
        curses.init_pair(90, curses.COLOR_WHITE, curses.COLOR_WHITE)  # Continue screen


class Menu:
    """Handles main menu UI."""
    
    KEY_UP = (ord("w"),259)
    KEY_DOWN = (ord("s"),258)
    KEY_ENTER = (10,)
    
    def __init__(self, window_manager):
        """
        Initialize menu.
        
        Args:
            window_manager: WindowManager instance
        """
        self.wm = window_manager
        self.window = None
        self.selected = "Start"
        self.sh = 0
        self.sw = 0
    
    def render(self):
        """Render the main menu."""
        self.sh, self.sw = self.wm.get_size()
        self.window = curses.newwin(self.sh, self.sw, 0, 0)
        self.window.keypad(1)
        self.window.timeout(100)
        self.window.bkgd(" ", curses.color_pair(3))
        render_border(self.window)
        
        start_button = [self.sh // 4, self.sw // 5]
        exit_button = [self.sh - self.sh // 2, self.sw // 5]
        initial_select = [start_button[0], start_button[1] - 2]
        
        key = 0
        while True:
            key = self.window.getch()
            
            # Render menu items
            self.window.addstr(self.sh // 8, self.sw // 4, "SNEK GAME BY KINU", 
                             curses.color_pair(1) | curses.A_BOLD)
            self.window.addch(initial_select[0], initial_select[1], ">", 
                            curses.color_pair(2) | curses.A_BLINK)
            self.window.addstr(start_button[0], start_button[1], "Start", 
                             curses.color_pair(1) | curses.A_BOLD)
            self.window.addstr(exit_button[0], exit_button[1], "Exit", 
                             curses.color_pair(1) | curses.A_BOLD)
            
            # Handle navigation
            # print(key, self.KEY_UP, self.KEY_DOWN, self.KEY_ENTER)
            if key in self.KEY_UP:
                initial_select = [start_button[0], start_button[1] - 2]
                self.selected = "Start"
                self.window.addch(exit_button[0], exit_button[1] - 2, " ", 
                                curses.color_pair(3))
            elif key in self.KEY_DOWN:
                initial_select = [exit_button[0], exit_button[1] - 2]
                self.selected = "Exit"
                self.window.addch(start_button[0], start_button[1] - 2, " ", 
                                curses.color_pair(3))
            
            # Handle selection
            if key in self.KEY_ENTER:
                if self.selected == "Start":
                    return self._handle_start()
                elif self.selected == "Exit":
                    return None
    
    def _handle_start(self):
        """Handle start button press."""
        return True  # Return True to indicate start was selected


class ContinueMenu:
    """Handles continue game confirmation menu."""
    
    KEY_UP = (ord("w"),259)
    KEY_DOWN = (ord("s"),258)
    KEY_ENTER = (10,)
    
    def __init__(self, window_manager):
        """
        Initialize continue menu.
        
        Args:
            window_manager: WindowManager instance
        """
        self.wm = window_manager
        self.window = None
        self.selected = "Yes"
        self.sh = 0
        self.sw = 0
    
    def render(self):
        """Render the continue menu."""
        self.sh, self.sw = self.wm.get_size()
        self.window = curses.newwin(self.sh, self.sw, 0, 0)
        self.window.keypad(1)
        self.window.timeout(100)
        self.window.bkgd(" ", curses.color_pair(3))
        render_border(self.window)
        
        yes_button = [self.sh // 4, self.sw // 5]
        no_button = [self.sh - self.sh // 2, self.sw // 5]
        initial_select = [yes_button[0], yes_button[1] - 2]
        
        key = 0
        while True:
            key = self.window.getch()
            
            # Render menu items
            self.window.addstr(self.sh // 8, self.sw // 4, 
                             "Game Data existing, do you want to continue?", 
                             curses.color_pair(1) | curses.A_BOLD)
            self.window.addch(initial_select[0], initial_select[1], ">", 
                            curses.color_pair(2) | curses.A_BLINK)
            self.window.addstr(yes_button[0], yes_button[1], "Yes", 
                             curses.color_pair(1) | curses.A_BOLD)
            self.window.addstr(no_button[0], no_button[1], "No", 
                             curses.color_pair(1) | curses.A_BOLD)
            
            # Handle navigation
            if key in self.KEY_UP:
                initial_select = [yes_button[0], yes_button[1] - 2]
                self.selected = "Yes"
                self.window.addch(no_button[0], no_button[1] - 2, " ", 
                                curses.color_pair(3))
            elif key in self.KEY_DOWN:
                initial_select = [no_button[0], no_button[1] - 2]
                self.selected = "No"
                self.window.addch(yes_button[0], yes_button[1] - 2, " ", 
                                curses.color_pair(3))
            
            # Handle selection
            if key in self.KEY_ENTER:
                if self.selected == "Yes":
                    return True
                elif self.selected == "No":
                    return False


class GameWindow:
    """Handles game window rendering."""
    
    def __init__(self, window_manager, height, width):
        """
        Initialize game window.
        
        Args:
            window_manager: WindowManager instance
            height: Window height
            width: Window width
        """
        self.wm = window_manager
        self.height = height
        self.width = width
        self.window = None
    
    def create(self):
        """Create the game window."""
        self.window = curses.newwin(self.height, self.width, 0, 0)
        self.window.keypad(1)
        self.window.timeout(100)
        render_border(self.window)
        return self.window
    
    def render_snake(self, snake_body):
        """
        Render snake on the window.
        
        Args:
            snake_body: List of snake body positions
        """
        try:
            self.window.addch(snake_body[0][0], snake_body[0][1], "@", 
                            curses.color_pair(5))
        except curses.error:
            pass
    
    def render_food(self, food_pos):
        """
        Render food on the window.
        
        Args:
            food_pos: Food position [y, x]
        """
        try:
            self.window.addch(food_pos[0], food_pos[1], "@", 
                            curses.color_pair(4))
        except curses.error:
            pass
    
    def render_score(self, score):
        """
        Render score on the window.
        
        Args:
            score: Current score
        """
        try:
            self.window.addstr(self.height - 1, 0, f'Score:{score}', 
                             curses.color_pair(6))
        except curses.error:
            pass
    
    def render_pause_message(self, message):
        """
        Render pause message.
        
        Args:
            message: Pause message text
        """
        try:
            self.window.addstr(self.height - 1, 9, message, 
                             curses.color_pair(6))
        except curses.error:
            pass
    
    def clear_cell(self, pos):
        """
        Clear a cell on the window.
        
        Args:
            pos: Position [y, x]
        """
        try:
            self.window.addch(pos[0], pos[1], ' ')
        except curses.error:
            pass
    
    def refresh(self):
        """Refresh the window."""
        if self.window:
            self.window.refresh()
    
    def get_key(self):
        """Get key input from window."""
        if self.window:
            return self.window.getch()
        return -1


class ContinueScreen:
    """Handles continue game screen rendering."""
    
    def __init__(self, window_manager):
        """
        Initialize continue screen.
        
        Args:
            window_manager: WindowManager instance
        """
        self.wm = window_manager
        self.window = None
    
    def render(self, game_window, snake_body):
        """
        Render continue screen with snake preview on the game window.
        
        Args:
            game_window: GameWindow instance to render on
            snake_body: Previous snake body positions
        """
        csh, csw = self.wm.get_size()
        height = game_window.height
        width = game_window.width
        w2 = curses.newwin(csh, csw)
        
        # Check window size
        while not (csh >= height and csw >= width):
            csh, csw = self.wm.get_size()
            w2.addstr(0, 0, "THE SIZE OF YOUR WINDOW IS SMALLER")
            w2.addstr(1, 0, "THAN THE GIVEN WINDOW! PLEASE RESIZE!")
            w2.addstr(2, 0, "Windows/Linux: Drag the outer box")
            w2.addstr(3, 0, "Android(Termux): Pinch your terminal outwards")
            w2.refresh()
        else:
            w2.touchwin()
            w2.refresh()
            del w2
        
        # Use the game window for countdown
        timed = 5 / len(snake_body) if snake_body else 0.1
        
        for i, snake in enumerate(snake_body):
            game_window.window.addstr(0, 0, f"Get ready in:  5 seconds")
            game_window.window.addch(snake[0], snake[1], "@", curses.color_pair(90))
            time.sleep(timed)
            game_window.window.refresh()
        
        # Clear the countdown message area
        try:
            game_window.window.addstr(0, 0, " " * width)
            render_border(game_window.window)
        except curses.error:
            pass
        
        game_window.window.refresh()
