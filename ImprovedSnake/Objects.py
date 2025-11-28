import logging
import json


class Snake:
    """Handles snake properties and movement logic."""
    
    # Key bindings
    KEY_UP = (ord("w"), 259)
    KEY_LEFT = (ord("a"), 260)
    KEY_DOWN = (ord("s"), 258)
    KEY_RIGHT = (ord("d"), 261)
    
    def __init__(self, start_x, start_y, initial_length=4):
        """
        Initialize snake with starting position.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            initial_length: Initial length of snake
        """
        self.body = []
        for i in range(initial_length):
            self.body.append([start_y, start_x - i])
        
        # Initialize direction and last_key to first value in tuple
        self.direction = self.KEY_RIGHT[0]
        self.last_key = self.KEY_RIGHT[0]
        self.last_movement = []
        self.logger = logging.getLogger(__name__)
    
    def get_head(self):
        """Get the head position of the snake."""
        return self.body[0]
    
    def get_body(self):
        """Get the entire body of the snake."""
        return self.body
    
    def set_direction(self, key):
        """
        Set the direction of the snake.
        
        Args:
            key: Key code for direction (integer)
        """
        # Prevent reversing into itself
        if key in self.KEY_UP and self.last_key not in self.KEY_DOWN:
            self.direction = key
            self.last_key = key
        elif key in self.KEY_LEFT and self.last_key not in self.KEY_RIGHT:
            self.direction = key
            self.last_key = key
        elif key in self.KEY_DOWN and self.last_key not in self.KEY_UP:
            self.direction = key
            self.last_key = key
        elif key in self.KEY_RIGHT and self.last_key not in self.KEY_LEFT:
            self.direction = key
            self.last_key = key
    
    def _move_up(self, new_head):
        """Move snake up."""
        new_head[0] -= 1
        self.last_movement.append([new_head[0], "-", 0])
        if len(self.last_movement) == 2:
            del self.last_movement[0]
    
    def _move_left(self, new_head):
        """Move snake left."""
        new_head[1] -= 1
        self.last_movement.append([new_head[1], "-", 1])
        if len(self.last_movement) == 2:
            del self.last_movement[0]
    
    def _move_down(self, new_head):
        """Move snake down."""
        new_head[0] += 1
        self.last_movement.append([new_head[0], "+", 0])
        if len(self.last_movement) == 2:
            del self.last_movement[0]
    
    def _move_right(self, new_head):
        """Move snake right."""
        new_head[1] += 1
        self.last_movement.append([new_head[1], "+", 1])
        if len(self.last_movement) == 2:
            del self.last_movement[0]
    
    def _continue_last_movement(self, new_head):
        """Continue with the last movement direction."""
        if self.last_movement:
            coordinates = self.last_movement[0]
            position = coordinates[0]
            operator = coordinates[1]
            index = coordinates[2]
            
            if operator == "+":
                position += 1
            elif operator == "-":
                position -= 1
            
            new_head[int(index)] = position
            self.last_movement.append([new_head[index], operator, index])
            if len(self.last_movement) == 2:
                del self.last_movement[0]
        else:
            # Default to right if no last movement
            self._move_right(new_head)
    
    def move(self):
        """
        Move the snake based on current direction.
        
        Returns:
            New head position
        """
        new_head = [self.body[0][0], self.body[0][1]]
        
        if self.direction in self.KEY_UP:
            self._move_up(new_head)
        elif self.direction in self.KEY_LEFT:
            self._move_left(new_head)
        elif self.direction in self.KEY_DOWN:
            self._move_down(new_head)
        elif self.direction in self.KEY_RIGHT:
            self._move_right(new_head)
        else:
            self._continue_last_movement(new_head)
        
        self.logger.debug(f"last_movement: {self.last_movement}")
        return new_head
    
    def grow(self):
        """Grow the snake by not removing the tail."""
        pass  # Growth is handled by not popping tail in game loop
    
    def shrink(self):
        """Remove the tail of the snake."""
        return self.body.pop()
    
    def check_self_collision(self):
        """
        Check if snake collided with itself.
        
        Returns:
            True if collision detected, False otherwise
        """
        return self.body[0] in self.body[1:]
    
    def check_wall_collision(self, height, width):
        """
        Check if snake collided with walls.
        
        Args:
            height: Level height
            width: Level width
            
        Returns:
            True if collision detected, False otherwise
        """
        head = self.get_head()
        return head[0] in [0, height - 1] or head[1] in [0, width - 1]
    
    def check_food_collision(self, food_pos):
        """
        Check if snake collided with food.
        
        Args:
            food_pos: Food position [y, x]
            
        Returns:
            True if collision detected, False otherwise
        """
        return self.body[0] == food_pos
    
    def to_dict(self):
        """Convert snake to dictionary for saving."""
        return {
            'body': self.body,
            'direction': self.direction,
            'last_key': self.last_key,
            'last_movement': self.last_movement
        }
    
    def from_dict(self, data):
        """Load snake from dictionary."""
        self.body = data['body']
        # Handle direction and last_key - convert tuple to int if needed
        direction = data.get('direction', self.KEY_RIGHT[0])
        if isinstance(direction, tuple):
            direction = direction[0]
        self.direction = direction
        
        last_key = data.get('last_key', self.KEY_RIGHT[0])
        if isinstance(last_key, tuple):
            last_key = last_key[0]
        self.last_key = last_key
        
        self.last_movement = data.get('last_movement', [])
    
    @staticmethod
    def check_last_move(data):
        """
        Convert saved movement data back to key code.
        
        Args:
            data: Movement data [position, operator, index]
            
        Returns:
            Key code for direction (integer, first value from tuple)
        """
        if not data:
            return Snake.KEY_RIGHT[0]
        
        coordinates = data[0] if isinstance(data, list) else data
        operator = coordinates[1]
        index = coordinates[2]
        
        mushed = str(operator) + str(index)
        if mushed == "+0":
            return Snake.KEY_DOWN[0]
        elif mushed == "-0":
            return Snake.KEY_UP[0]
        elif mushed == "+1":
            return Snake.KEY_RIGHT[0]
        elif mushed == "-1":
            return Snake.KEY_LEFT[0]
        
        return Snake.KEY_RIGHT[0]

