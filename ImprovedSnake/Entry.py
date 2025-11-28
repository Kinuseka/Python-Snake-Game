import curses
import time
import sys
import os
import logging
import json
import re

try:
    from .Objects import Snake
    from .Interface import WindowManager, Menu, ContinueMenu, GameWindow, ContinueScreen
    from .Level import Level
except ImportError:
    from Objects import Snake
    from Interface import WindowManager, Menu, ContinueMenu, GameWindow, ContinueScreen
    from Level import Level


class Game:
    """Main game class that coordinates all modules."""
    
    KEY_PAUSE = ord("p")
    
    def __init__(self):
        """Initialize game."""
        self.wm = WindowManager()
        self.score = 0
        self.snake = None
        self.level = None
        self.game_window = None
        self.logger = None
        self.prev_data = None
    
    def introduction(self):
        """Display introduction message."""
        print("Welcome snake v1.0")
        print("This fun so enjoy i guess")
        time.sleep(1)
    
    def setup_logging(self):
        """Setup logging for game."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        self.log_handler = logging.FileHandler("Snake.log")
        self.log_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
    
    def close_logging(self):
        """Close logging file handler."""
        if self.logger and self.log_handler:
            self.log_handler.close()
            self.logger.removeHandler(self.log_handler)
    
    def load_previous_game(self):
        """
        Load previous game data from log file.
        
        Returns:
            Dictionary with previous game data or None
        """
        try:
            with open("Snake.log") as f:
                data = {}
                for line in f:
                    stripped = line.strip()
                    if "Window_size" in stripped:
                        window_data = stripped.replace("Window_size: ", "")
                        sh = int(re.search(r"(\d+),", window_data)[1])
                        sw = int(re.search(r",(\d+)", window_data)[1])
                        data['height'] = sh
                        data['width'] = sw
                    if "snake_bod" in stripped:
                        snake_data = stripped.replace("snake_bod: ", "")
                        data['snake_body'] = json.loads(snake_data)
                    if "Food" in stripped:
                        food_data = stripped.replace("Food: ", "")
                        data['food'] = json.loads(food_data)
                    if "last_movement" in stripped:
                        movement_data = stripped.replace("last_movement:", "")
                        new = ""
                        for char in movement_data:
                            new += char.replace("'", '"')
                        data['last_movement'] = json.loads(new)
                
                # Validate loaded data
                if self._validate_saved_data(data):
                    return data
                else:
                    # Close logging handler before deleting file
                    if hasattr(self, 'log_handler') and self.log_handler:
                        self.close_logging()
                    if os.path.isfile(os.path.join(os.getcwd(), "Snake.log")):
                        try:
                            os.remove("Snake.log")
                        except PermissionError:
                            # File might still be locked, try again after a brief delay
                            time.sleep(0.1)
                            try:
                                os.remove("Snake.log")
                            except PermissionError:
                                pass  # Ignore if still locked
                    # Recreate logging handler
                    if hasattr(self, 'logger'):
                        self.setup_logging()
                    return None
        except (FileNotFoundError, KeyError, json.JSONDecodeError, UnboundLocalError):
            return None
    
    def _validate_saved_data(self, data):
        """
        Validate saved game data.
        
        Args:
            data: Dictionary with game data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            snake_body = data['snake_body']
            height = data['height']
            width = data['width']
            
            # Check wall collision
            if snake_body[0][0] in [0, height - 1] or snake_body[0][1] in [0, width - 1]:
                print("Death1")
                return False
            
            # Check self collision
            if snake_body[0] in snake_body[1:]:
                print("Death2")
                return False
            
            return True
        except (KeyError, IndexError):
            return False
    
    def initialize_new_game(self):
        """Initialize a new game."""
        sh, sw = self.wm.get_size()
        snake_x = sw // 4
        snake_y = sh // 2
        
        self.snake = Snake(snake_x, snake_y)
        self.level = Level(sh, sw)
        self.game_window = GameWindow(self.wm, sh, sw)
        self.level.game_window = self.game_window
        self.game_window.create()
        
        # Spawn initial food
        self.level.spawn_food(self.snake.get_body())
        
        self.logger.debug(f"Window_size: {sh},{sw}")
    
    def initialize_continue_game(self, prev_data):
        """
        Initialize game from previous data.
        
        Args:
            prev_data: Dictionary with previous game data
        """
        self.prev_data = prev_data
        
        # Create snake and load data
        self.snake = Snake(0, 0)
        self.snake.from_dict({
            'body': prev_data['snake_body'],
            'direction': Snake.check_last_move(prev_data.get('last_movement', [])),
            'last_key': Snake.check_last_move(prev_data.get('last_movement', [])),
            'last_movement': prev_data.get('last_movement', [])
        })
        
        # Create level and load data
        self.level = Level(prev_data['height'], prev_data['width'])
        self.level.food = prev_data.get('food', None)
        
        # Create game window (will be initialized in render_continue_screen)
        self.game_window = GameWindow(self.wm, prev_data['height'], prev_data['width'])
        self.level.game_window = self.game_window
        
        # Calculate score
        self.score = len(self.snake.get_body()) - 4
        
        self.logger.debug(f"Window_size: {prev_data['height']},{prev_data['width']}")
    
    def render_continue_screen(self):
        """Render continue screen before resuming game."""
        if not self.prev_data:
            return
        
        # Create game window first (it will be used for continue screen)
        self.game_window.create()
        
        # Render continue screen on the game window
        continue_screen = ContinueScreen(self.wm)
        continue_screen.render(self.game_window, self.prev_data['snake_body'])
        
        # Render initial game state after continue screen
        self.level.render(self.snake, self.score)
    
    def game_loop(self):
        """Main game loop."""
        error = False
        
        while True:
            try:
                while True:
                    # Get input
                    get_key = self.game_window.get_key()
                    if get_key != -1:
                        self.snake.set_direction(get_key)
                    
                    # Check collisions
                    wall_collision, self_collision = self.level.check_collision(self.snake)
                    
                    if wall_collision or self_collision or error:
                        self.game_over()
                        return
                    
                    # Handle pause (check before move, but pause after move)
                    should_pause = (get_key == self.KEY_PAUSE)
                    if should_pause:
                        # Continue with last direction
                        get_key = -1
                    
                    # Move snake
                    new_head = self.snake.move()
                    self.snake.body.insert(0, new_head)
                    
                    # Check food collision
                    if self.level.check_food_collision(self.snake):
                        self.score += 1
                        self.level.spawn_food(self.snake.get_body())
                        self.game_window.render_food(self.level.get_food())
                    else:
                        tail = self.snake.shrink()
                        self.level.clear_tail(tail)
                    
                    # Handle pause after move
                    if should_pause:
                        self.handle_pause()
                    
                    # Log game state
                    self.logger.debug(f"User_input: {get_key}")
                    self.logger.debug(f"snake_bod: {self.snake.get_body()}")
                    self.logger.debug(f"Food: {self.level.get_food()}")
                    
                    # Render game
                    try:
                        self.level.render(self.snake, self.score)
                    except curses.error:
                        error = True
                    
                    # Game speed
                    time.sleep(0.05)
                    
            except KeyboardInterrupt:
                # Ctrl+C pressed - save and exit
                self.save_game()
                self.wm.cleanup()
                print("\nGame saved!")
                sys.exit(0)
    
    def save_game(self):
        """Save current game state to log file."""
        # Only save if game is initialized
        if not self.logger or not self.snake or not self.level:
            return
        
        # Close handler before writing to ensure data is flushed
        self.close_logging()
        
        try:
            # Write game state to log file
            with open("Snake.log", "w") as f:
                height, width = self.level.get_dimensions()
                f.write(f"Window_size: {height},{width}\n")
                f.write(f"snake_bod: {json.dumps(self.snake.get_body())}\n")
                f.write(f"Food: {json.dumps(self.level.get_food())}\n")
                f.write(f"last_movement: {json.dumps(self.snake.last_movement)}\n")
        except Exception as e:
            print(f"Error saving game: {e}")
        finally:
            # Recreate logging handler for potential future use
            if hasattr(self, 'logger'):
                self.setup_logging()
    
    def handle_pause(self):
        """Handle game pause."""
        message = 'Game Paused press "p" to continue'
        while True:
            key = self.game_window.get_key()
            self.game_window.render_snake(self.snake.get_body())
            self.game_window.render_score(self.score)
            self.game_window.render_pause_message(message)
            
            if key == self.KEY_PAUSE:
                # Clear pause message
                for num in range(len(message)):
                    self.game_window.window.addstr(
                        self.level.height - 1, 9 + num, "-", 
                        curses.color_pair(7)
                    )
                break
    
    def game_over(self):
        """Handle game over."""
        self.wm.cleanup()
        
        if self.snake.check_wall_collision(self.level.height, self.level.width):
            print("SNAKE WENT OUT LMAO NOOB")
        elif self.snake.check_self_collision():
            print("U ATE UR SELF WTF WEIRDO")
        
        print("Score:", self.score)
        sys.exit()
    
    def run(self):
        """Run the game."""
        try:
            # Introduction
            self.introduction()
            
            # Initialize curses
            self.wm.initialize()
            self.wm.init_color_pairs()
            
            # Setup logging
            self.setup_logging()
            
            # Load previous game
            prev_data = self.load_previous_game()
            status = prev_data is not None
            
            # Main menu
            menu = Menu(self.wm)
            selected = menu.render()
            
            if selected is None:  # Exit selected
                sys.exit()
            
            # Continue menu if previous data exists
            if status:
                continue_menu = ContinueMenu(self.wm)
                continue_selected = continue_menu.render()
                
                if continue_selected:
                    self.initialize_continue_game(prev_data)
                    self.render_continue_screen()
                else:
                    # Close logging handler before deleting file
                    self.close_logging()
                    if os.path.isfile(os.path.join(os.getcwd(), "Snake.log")):
                        try:
                            os.remove("Snake.log")
                        except PermissionError:
                            # File might still be locked, try again after a brief delay
                            time.sleep(0.1)
                            try:
                                os.remove("Snake.log")
                            except PermissionError:
                                pass  # Ignore if still locked
                    # Recreate logging handler for new game
                    self.setup_logging()
                    self.initialize_new_game()
            else:
                self.initialize_new_game()
            
            # Start game loop
            self.game_loop()
            
        except KeyboardInterrupt:
            # Handle Ctrl+C outside game loop (e.g., in menus)
            self.save_game()
            self.wm.cleanup()
            print("\nGame saved!")
            sys.exit(0)
        finally:
            # Close logging handler before cleanup
            if self.logger:
                self.close_logging()
            self.wm.cleanup()


def main():
    """Main entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

