import random
import logging


class Level:
    """Handles level properties, collision detection, and rendering coordination."""
    
    def __init__(self, height, width, game_window=None):
        """
        Initialize level.
        
        Args:
            height: Level height
            width: Level width
            game_window: GameWindow instance for rendering
        """
        self.height = height
        self.width = width
        self.food = None
        self.game_window = game_window
        self.logger = logging.getLogger(__name__)
    
    def spawn_food(self, snake_body):
        """
        Spawn food at a random position not occupied by snake.
        
        Args:
            snake_body: List of snake body positions
        """
        self.food = None
        while self.food is None:
            nf = [
                random.randint(1, self.height - 2),
                random.randint(1, self.width - 2)
            ]
            self.food = nf if nf not in snake_body else None
    
    def get_food(self):
        """Get current food position."""
        return self.food
    
    def check_collision(self, snake):
        """
        Check all collisions (walls and self).
        
        Args:
            snake: Snake instance
            
        Returns:
            Tuple (wall_collision, self_collision)
        """
        wall_collision = snake.check_wall_collision(self.height, self.width)
        self_collision = snake.check_self_collision()
        return wall_collision, self_collision
    
    def check_food_collision(self, snake):
        """
        Check if snake collided with food.
        
        Args:
            snake: Snake instance
            
        Returns:
            True if collision detected, False otherwise
        """
        return snake.check_food_collision(self.food)
    
    def render(self, snake, score):
        """
        Render the level (snake, food, score).
        
        Args:
            snake: Snake instance
            score: Current score
        """
        if not self.game_window:
            return
        
        # Render food
        if self.food:
            self.game_window.render_food(self.food)
        
        # Render snake
        self.game_window.render_snake(snake.get_body())
        
        # Render score
        self.game_window.render_score(score)
        
        # Refresh window
        self.game_window.refresh()
    
    def clear_tail(self, tail_pos):
        """
        Clear the tail position from the window.
        
        Args:
            tail_pos: Tail position [y, x]
        """
        if self.game_window:
            self.game_window.clear_cell(tail_pos)
    
    def get_dimensions(self):
        """Get level dimensions."""
        return self.height, self.width
    
    def to_dict(self):
        """Convert level to dictionary for saving."""
        return {
            'height': self.height,
            'width': self.width,
            'food': self.food
        }
    
    def from_dict(self, data):
        """Load level from dictionary."""
        self.height = data['height']
        self.width = data['width']
        self.food = data.get('food', None)

