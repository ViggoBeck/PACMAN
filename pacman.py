import pygame
import sys
import random
import math
import time
from collections import deque

# Initialize Pygame
pygame.init()

# Constants - Adjusted for full window maze
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850  # Increased to fit larger maze
CELL_SIZE = 35  # Increased from 30 to fill window better
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 139)
DARK_RED = (139, 0, 0)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Life system constants
MAX_LIVES = 4
EXTRA_LIFE_SCORES = [5000, 15000, 35000]  # Get extra lives at these scores

# Maze layout (1 = wall, 0 = empty, 2 = dot, 4 = super dot, 5 = fruit)
MAZE = [
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
	[1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
	[1,4,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,4,1],  # Super dots in corners
	[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
	[1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
	[1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
	[1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
	[0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
	[1,1,1,1,2,1,0,1,1,0,0,1,1,0,1,2,1,1,1,1],
	[0,0,0,0,2,0,0,1,0,0,0,0,1,0,0,2,0,0,0,0],  # This is the tunnel row
	[1,1,1,1,2,1,0,1,0,0,0,0,1,0,1,2,1,1,1,1],
	[0,0,0,1,2,1,0,1,1,1,1,1,1,0,1,2,1,0,0,0],
	[1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
	[1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
	[1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
	[1,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,1],
	[1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
	[1,4,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,4,1],  # More super dots
	[1,2,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
	[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Ghost base coordinates (exclude from fruit spawning)
GHOST_BASE_COORDS = {
	(8, 8), (9, 8), (10, 8), (11, 8),
	(8, 9), (9, 9), (10, 9), (11, 9),
	(8, 10), (9, 10), (10, 10), (11, 10),
	(8, 11), (9, 11), (10, 11), (11, 11)
}

# Tunnel row (where horizontal wraparound is possible)
TUNNEL_ROW = 9

# Fruit types with different point values and colors
FRUITS = [
	("cherry", 100, RED, DARK_RED),
	("strawberry", 300, RED, LIGHT_GREEN),
	("orange", 500, ORANGE, GREEN),
	("apple", 700, RED, GREEN),
	("grapes", 1000, PURPLE, GREEN),
	("bell", 2000, YELLOW, BROWN),
	("key", 5000, YELLOW, BROWN)
]

class PacMan:
	def __init__(self, level=1):
		self.x = 1
		self.y = 1
		self.start_x = 1
		self.start_y = 1
		self.direction = RIGHT
		self.mouth_open = True
		self.mouth_timer = 0
		self.move_timer = 0
		# Speed increases with level - starts at 2 frames delay, decreases by 0.1 per level
		# Minimum delay of 0.5 frames to prevent becoming too fast
		self.move_delay = max(0.5, 2.0 - (level - 1) * 0.1)
		self.level = level

	def set_level_speed(self, level):
		"""Update Pac-Man's speed based on current level"""
		self.level = level
		self.move_delay = max(0.5, 2.0 - (level - 1) * 0.1)

	def reset_position(self):
		"""Reset Pac-Man to starting position"""
		self.x = self.start_x
		self.y = self.start_y
		self.direction = RIGHT

	def move(self, dx, dy, maze):
		# Add movement delay - gets faster each level
		self.move_timer += 1
		if self.move_timer < self.move_delay:
			return False
		self.move_timer = 0

		new_x = self.x + dx
		new_y = self.y + dy

		# Handle tunnel wraparound
		if new_y == TUNNEL_ROW:
			if new_x < 0:  # Going through left edge
				new_x = len(maze[0]) - 1
			elif new_x >= len(maze[0]):  # Going through right edge
				new_x = 0

		# Check boundaries and walls
		if (0 <= new_x < len(maze[0]) and
			0 <= new_y < len(maze) and
			maze[new_y][new_x] != 1):  # 1 = wall
			self.x = new_x
			self.y = new_y
			# Update direction for drawing
			if dx != 0 or dy != 0:
				self.direction = (dx, dy)
			return True
		return False

	def update(self):
		# Animate mouth opening/closing
		self.mouth_timer += 1
		if self.mouth_timer > 5:  # Change every 5 frames
			self.mouth_open = not self.mouth_open
			self.mouth_timer = 0

	def draw(self, screen):
		center_x = self.x * CELL_SIZE + CELL_SIZE // 2
		center_y = self.y * CELL_SIZE + CELL_SIZE // 2
		radius = CELL_SIZE // 3

		if self.mouth_open:
			# Calculate mouth angle based on direction
			if self.direction == RIGHT:
				start_angle = 0.3
				end_angle = -0.3
			elif self.direction == LEFT:
				start_angle = math.pi - 0.3
				end_angle = math.pi + 0.3
			elif self.direction == UP:
				start_angle = -math.pi/2 - 0.3
				end_angle = -math.pi/2 + 0.3
			else:  # DOWN
				start_angle = math.pi/2 - 0.3
				end_angle = math.pi/2 + 0.3

			# Draw Pac-Man with mouth
			pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)

			# Draw mouth (triangle to create the opening)
			mouth_points = [
				(center_x, center_y),
				(center_x + radius * math.cos(start_angle), center_y + radius * math.sin(start_angle)),
				(center_x + radius * math.cos(end_angle), center_y + radius * math.sin(end_angle))
			]
			pygame.draw.polygon(screen, BLACK, mouth_points)
		else:
			# Closed mouth - just a circle
			pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)

class Ghost:
	def __init__(self, x, y, color, personality="aggressive", ghost_id=0):
		self.x = x
		self.y = y
		self.start_x = x
		self.start_y = y
		self.color = color
		self.original_color = color
		self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
		self.move_timer = 0
		self.personality = personality
		self.ghost_id = ghost_id  # For spreading behavior
		self.stuck_counter = 0
		self.last_position = (x, y)
		self.vulnerable = False
		self.vulnerable_timer = 0
		self.eaten = False
		self.returning_home = False
		self.base_speed = 6
		self.path_cache = {}
		self.path_cache_timer = 0
		self.target_corner = None
		self.scatter_timer = 0
		self.mode = "chase"  # chase, scatter, or frightened
		self.spread_offset = ghost_id * 3  # Each ghost gets different spread behavior

	def set_vulnerable(self, duration):
		self.vulnerable = True
		self.vulnerable_timer = duration
		self.color = DARK_BLUE
		self.mode = "frightened"

	def update_vulnerable_state(self):
		if self.vulnerable:
			self.vulnerable_timer -= 1
			# Flash when about to end
			if self.vulnerable_timer < 60 and self.vulnerable_timer % 20 < 10:
				self.color = WHITE
			elif self.vulnerable_timer < 60:
				self.color = DARK_BLUE

			if self.vulnerable_timer <= 0:
				self.vulnerable = False
				self.color = self.original_color
				self.mode = "chase"

	def reset_after_eaten(self):
		# Improved reset logic to prevent disappearing
		self.x = self.start_x
		self.y = self.start_y
		self.eaten = False
		self.returning_home = False
		self.vulnerable = False
		self.vulnerable_timer = 0
		self.color = self.original_color
		self.mode = "chase"
		self.stuck_counter = 0
		self.last_position = (self.x, self.y)

	def reset_position(self):
		"""Reset ghost to starting position"""
		self.x = self.start_x
		self.y = self.start_y
		self.vulnerable = False
		self.vulnerable_timer = 0
		self.eaten = False
		self.returning_home = False
		self.color = self.original_color
		self.mode = "chase"
		self.stuck_counter = 0
		self.last_position = (self.x, self.y)

	def get_corner_target(self):
		"""Get corner target based on personality"""
		if self.personality == "aggressive":
			return (1, 1)  # Top-left
		elif self.personality == "ambush":
			return (18, 1)  # Top-right
		elif self.personality == "patrol":
			return (18, 19)  # Bottom-right
		else:  # unpredictable
			return (1, 19)  # Bottom-left

	def calculate_distance(self, x1, y1, x2, y2):
		"""Calculate Manhattan distance with tunnel consideration"""
		dx = abs(x1 - x2)
		dy = abs(y1 - y2)

		# Consider tunnel shortcut on tunnel row
		if y1 == TUNNEL_ROW and y2 == TUNNEL_ROW:
			tunnel_distance = min(dx, 20 - dx)  # 20 is maze width
			return tunnel_distance + dy

		return dx + dy

	def get_other_ghost_positions(self, all_ghosts):
		"""Get positions of other ghosts for avoidance"""
		positions = []
		for ghost in all_ghosts:
			if ghost.ghost_id != self.ghost_id:
				positions.append((ghost.x, ghost.y))
		return positions

	def find_path_to_target(self, maze, target_x, target_y):
		"""Advanced BFS pathfinding with caching and tunnel support"""
		cache_key = (self.x, self.y, target_x, target_y)

		# Use cached path if recent and valid
		if (cache_key in self.path_cache and
			self.path_cache_timer < 30):  # Cache for 30 frames
			return self.path_cache[cache_key]

		queue = deque([(self.x, self.y, [])])
		visited = set()
		visited.add((self.x, self.y))

		while queue:
			x, y, path = queue.popleft()

			if x == target_x and y == target_y:
				self.path_cache[cache_key] = path
				self.path_cache_timer = 0
				return path

			if len(path) > 20:  # Increased search depth
				continue

			for dx, dy in [UP, DOWN, LEFT, RIGHT]:
				new_x, new_y = x + dx, y + dy

				# Handle tunnel wraparound for ghosts too
				if new_y == TUNNEL_ROW:
					if new_x < 0:
						new_x = len(maze[0]) - 1
					elif new_x >= len(maze[0]):
						new_x = 0

				if ((new_x, new_y) not in visited and
					0 <= new_x < len(maze[0]) and
					0 <= new_y < len(maze) and
					maze[new_y][new_x] != 1):

					visited.add((new_x, new_y))
					new_path = path + [(dx, dy)]
					queue.append((new_x, new_y, new_path))

		# Cache empty result too
		self.path_cache[cache_key] = []
		return []

	def get_valid_moves(self, maze):
		valid_moves = []
		for dx, dy in [UP, DOWN, LEFT, RIGHT]:
			new_x = self.x + dx
			new_y = self.y + dy

			# Handle tunnel wraparound
			if new_y == TUNNEL_ROW:
				if new_x < 0:
					new_x = len(maze[0]) - 1
				elif new_x >= len(maze[0]):
					new_x = 0

			if (0 <= new_x < len(maze[0]) and
				0 <= new_y < len(maze) and
				maze[new_y][new_x] != 1):  # Not a wall
				valid_moves.append((dx, dy))
		return valid_moves

	def get_spread_target(self, pacman_x, pacman_y, other_ghost_positions):
		"""Calculate a spread-out target to avoid clustering"""
		# Base target around Pac-Man with personality-based offset
		if self.personality == "aggressive":
			# Direct approach but slightly offset
			target_x = pacman_x + self.spread_offset - 2
			target_y = pacman_y
		elif self.personality == "ambush":
			# Approach from different angles
			target_x = pacman_x + (4 if self.ghost_id % 2 == 0 else -4)
			target_y = pacman_y + (2 if self.ghost_id < 2 else -2)
		elif self.personality == "patrol":
			# Circle around Pac-Man
			angle = (self.ghost_id * 90 + self.scatter_timer) % 360
			target_x = pacman_x + int(6 * math.cos(math.radians(angle)))
			target_y = pacman_y + int(6 * math.sin(math.radians(angle)))
		else:  # unpredictable
			# Random positions around Pac-Man
			offset_x = random.choice([-5, -3, 3, 5])
			offset_y = random.choice([-5, -3, 3, 5])
			target_x = pacman_x + offset_x
			target_y = pacman_y + offset_y

		# Avoid other ghosts by adjusting target
		for ghost_x, ghost_y in other_ghost_positions:
			distance = abs(target_x - ghost_x) + abs(target_y - ghost_y)
			if distance < 3:  # Too close to another ghost
				# Push away from the other ghost
				if target_x < ghost_x:
					target_x -= 2
				else:
					target_x += 2
				if target_y < ghost_y:
					target_y -= 2
				else:
					target_y += 2

		# Clamp to maze bounds
		target_x = max(1, min(18, target_x))
		target_y = max(1, min(19, target_y))

		return target_x, target_y

	def predict_pacman_position(self, pacman_x, pacman_y, pacman_direction, steps=4):
		"""Predict where Pac-Man will be in 'steps' moves"""
		predicted_x = pacman_x + pacman_direction[0] * steps
		predicted_y = pacman_y + pacman_direction[1] * steps

		# Handle tunnel wraparound in prediction
		if predicted_y == TUNNEL_ROW:
			if predicted_x < 0:
				predicted_x = 19
			elif predicted_x >= 20:
				predicted_x = 0

		# Clamp to maze bounds
		predicted_x = max(0, min(19, predicted_x))
		predicted_y = max(0, min(20, predicted_y))

		return predicted_x, predicted_y

	def update_mode(self):
		"""Update ghost mode between scatter and chase"""
		self.scatter_timer += 1

		if not self.vulnerable:
			# Alternate between chase (600 frames) and scatter (200 frames)
			if self.mode == "chase" and self.scatter_timer > 600:
				self.mode = "scatter"
				self.scatter_timer = 0
			elif self.mode == "scatter" and self.scatter_timer > 200:
				self.mode = "chase"
				self.scatter_timer = 0

	def choose_smart_move(self, maze, pacman_x, pacman_y, pacman_direction, all_ghosts):
		"""Ultra-smart movement with improved spreading and no disappearing"""
		valid_moves = self.get_valid_moves(maze)
		if not valid_moves:
			return (0, 0)

		# Update ghost mode
		self.update_mode()

		# If eaten, return to start position - IMPROVED LOGIC
		if self.eaten or self.returning_home:
			# Check if we're at home position
			if abs(self.x - self.start_x) <= 1 and abs(self.y - self.start_y) <= 1:
				self.reset_after_eaten()  # Properly reset when home
				return (0, 0)

			# Find path home
			path = self.find_path_to_target(maze, self.start_x, self.start_y)
			if path and len(path) > 0:
				return path[0]
			else:
				# Fallback if pathfinding fails
				dx = 1 if self.start_x > self.x else -1 if self.start_x < self.x else 0
				dy = 1 if self.start_y > self.y else -1 if self.start_y < self.y else 0
				if (dx, dy) in valid_moves:
					return (dx, dy)
				return random.choice(valid_moves)

		# Get other ghost positions for spreading
		other_ghost_positions = self.get_other_ghost_positions(all_ghosts)

		# If vulnerable (frightened mode), run away intelligently with spreading
		if self.vulnerable:
			best_move = None
			max_distance = -1

			for dx, dy in valid_moves:
				new_x, new_y = self.x + dx, self.y + dy

				# Handle tunnel wraparound
				if new_y == TUNNEL_ROW:
					if new_x < 0:
						new_x = len(maze[0]) - 1
					elif new_x >= len(maze[0]):
						new_x = 0

				distance_to_pacman = self.calculate_distance(new_x, new_y, pacman_x, pacman_y)

				# Avoid other ghosts bonus
				ghost_avoidance_bonus = 0
				for ghost_x, ghost_y in other_ghost_positions:
					ghost_distance = abs(new_x - ghost_x) + abs(new_y - ghost_y)
					if ghost_distance > 3:
						ghost_avoidance_bonus += 2

				# Prefer corners when vulnerable
				corner_bonus = 0
				if new_x <= 2 or new_x >= 17 or new_y <= 2 or new_y >= 18:
					corner_bonus = 5

				total_score = distance_to_pacman + corner_bonus + ghost_avoidance_bonus

				if total_score > max_distance:
					max_distance = total_score
					best_move = (dx, dy)

			if best_move:
				return best_move

		# Scatter mode - head to corners with spreading
		if self.mode == "scatter":
			corner_x, corner_y = self.get_corner_target()
			# Add some randomness to prevent exact clustering
			corner_x += random.randint(-2, 2)
			corner_y += random.randint(-2, 2)
			corner_x = max(1, min(18, corner_x))
			corner_y = max(1, min(19, corner_y))

			path = self.find_path_to_target(maze, corner_x, corner_y)
			if path and len(path) > 0:
				return path[0]

		# Chase mode - IMPROVED with better spreading
		if self.mode == "chase":
			# Get spread target instead of direct Pac-Man position
			target_x, target_y = self.get_spread_target(pacman_x, pacman_y, other_ghost_positions)

			if self.personality == "aggressive":
				# Red ghost - direct but spread approach
				path = self.find_path_to_target(maze, target_x, target_y)
				if path and len(path) > 0:
					return path[0]

			elif self.personality == "ambush":
				# Pink ghost - predictive ambush with spreading
				predicted_x, predicted_y = self.predict_pacman_position(
					pacman_x, pacman_y, pacman_direction, 4 + self.spread_offset)

				# Adjust prediction to avoid other ghosts
				for ghost_x, ghost_y in other_ghost_positions:
					if abs(predicted_x - ghost_x) + abs(predicted_y - ghost_y) < 3:
						predicted_x += 3 if predicted_x > 10 else -3
						predicted_y += 2 if predicted_y > 10 else -2

				path = self.find_path_to_target(maze, predicted_x, predicted_y)
				if path and len(path) > 0:
					return path[0]

			elif self.personality == "patrol":
				# Cyan ghost - circling behavior with better spreading
				distance_to_pacman = self.calculate_distance(self.x, self.y, pacman_x, pacman_y)

				if distance_to_pacman > 8:
					# Far away - approach but maintain spread
					path = self.find_path_to_target(maze, target_x, target_y)
					if path and len(path) > 0:
						return path[0]
				else:
					# Close - maintain patrol pattern
					patrol_x = target_x
					patrol_y = target_y
					path = self.find_path_to_target(maze, patrol_x, patrol_y)
					if path and len(path) > 0:
						return path[0]

			elif self.personality == "unpredictable":
				# Orange ghost - truly unpredictable with spreading
				distance_to_pacman = self.calculate_distance(self.x, self.y, pacman_x, pacman_y)

				if distance_to_pacman > 8:
					# Far away - approach spread target
					path = self.find_path_to_target(maze, target_x, target_y)
					if path and len(path) > 0:
						return path[0]
				else:
					# Close - be truly unpredictable
					if random.random() < 0.3:
						# Sometimes approach anyway
						path = self.find_path_to_target(maze, target_x, target_y)
						if path and len(path) > 0:
							return path[0]
					else:
						# Random movement with ghost avoidance
						best_moves = []
						for dx, dy in valid_moves:
							new_x, new_y = self.x + dx, self.y + dy
							avoid_ghosts = True
							for ghost_x, ghost_y in other_ghost_positions:
								if abs(new_x - ghost_x) + abs(new_y - ghost_y) < 2:
									avoid_ghosts = False
									break
							if avoid_ghosts:
								best_moves.append((dx, dy))

						if best_moves:
							return random.choice(best_moves)

		# Fallback: smart chase with ghost avoidance
		path = self.find_path_to_target(maze, pacman_x, pacman_y)
		if path and len(path) > 0:
			return path[0]

		# Final fallback: avoid reversing and avoid other ghosts
		opposite_dir = (-self.direction[0], -self.direction[1])
		good_moves = []

		for dx, dy in valid_moves:
			if (dx, dy) != opposite_dir:  # Don't reverse
				new_x, new_y = self.x + dx, self.y + dy
				avoid_ghosts = True
				for ghost_x, ghost_y in other_ghost_positions:
					if abs(new_x - ghost_x) + abs(new_y - ghost_y) < 2:
						avoid_ghosts = False
						break
				if avoid_ghosts:
					good_moves.append((dx, dy))

		if good_moves:
			return random.choice(good_moves)

		return random.choice(valid_moves)

	def move(self, maze, pacman_x, pacman_y, pacman_direction, level_speed_multiplier=1.0, all_ghosts=None):
		# Update vulnerable state and timers
		self.update_vulnerable_state()
		self.path_cache_timer += 1

		self.move_timer += 1
		# Increase speed based on level
		adjusted_speed = max(1, int(self.base_speed / level_speed_multiplier))
		move_speed = adjusted_speed + 2 if self.vulnerable else adjusted_speed

		if self.move_timer < move_speed:
			return

		self.move_timer = 0

		# Choose move based on ultra-smart AI with spreading
		if all_ghosts is None:
			all_ghosts = []
		dx, dy = self.choose_smart_move(maze, pacman_x, pacman_y, pacman_direction, all_ghosts)

		# Apply movement with tunnel support
		new_x = self.x + dx
		new_y = self.y + dy

		# Handle tunnel wraparound
		if new_y == TUNNEL_ROW:
			if new_x < 0:
				new_x = len(maze[0]) - 1
			elif new_x >= len(maze[0]):
				new_x = 0

		if (0 <= new_x < len(maze[0]) and
			0 <= new_y < len(maze) and
			maze[new_y][new_x] != 1):
			self.x = new_x
			self.y = new_y
			self.direction = (dx, dy)

	def draw(self, screen):
		# FIXED: Always draw ghost unless specifically being respawned
		if self.eaten and self.returning_home and abs(self.x - self.start_x) <= 1 and abs(self.y - self.start_y) <= 1:
			return  # Only don't draw when actually respawning at home

		center_x = self.x * CELL_SIZE + CELL_SIZE // 2
		center_y = self.y * CELL_SIZE + CELL_SIZE // 2
		radius = CELL_SIZE // 3

		# Draw ghost body (circle + rectangle)
		ghost_color = self.color if not (self.eaten and self.returning_home) else GRAY
		pygame.draw.circle(screen, ghost_color, (center_x, center_y - 2), radius)
		pygame.draw.rect(screen, ghost_color,
						(center_x - radius, center_y - 2, radius * 2, radius + 2))

		# Draw wavy bottom
		wave_points = []
		for i in range(5):
			x = center_x - radius + (i * radius * 2 // 4)
			y = center_y + radius if i % 2 == 0 else center_y + radius - 4
			wave_points.append((x, y))
		wave_points.append((center_x + radius, center_y + radius))
		wave_points.append((center_x - radius, center_y + radius))
		pygame.draw.polygon(screen, ghost_color, wave_points)

		# Draw eyes - different for eaten ghosts
		eye_size = 3
		if self.eaten and self.returning_home:
			# Draw dot eyes for eaten ghosts
			pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 8), 2)
			pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 8), 2)
		else:
			eye_color = WHITE if not self.vulnerable or self.vulnerable_timer >= 60 else BLACK
			pygame.draw.circle(screen, eye_color, (center_x - 6, center_y - 8), eye_size)
			pygame.draw.circle(screen, eye_color, (center_x + 6, center_y - 8), eye_size)
			if not self.vulnerable or self.vulnerable_timer >= 60:
				pygame.draw.circle(screen, BLACK, (center_x - 6, center_y - 8), 2)
				pygame.draw.circle(screen, BLACK, (center_x + 6, center_y - 8), 2)

class Fruit:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.fruit_type = random.choice(FRUITS)
		self.spawn_time = time.time()
		self.lifetime = 10  # Fruit disappears after 10 seconds
		self.pulse_timer = 0

	def is_expired(self):
		return time.time() - self.spawn_time > self.lifetime

	def get_points(self):
		return self.fruit_type[1]

	def draw_cherry(self, screen, center_x, center_y):
		# Draw cherry stems
		pygame.draw.line(screen, BROWN, (center_x-4, center_y-10), (center_x-4, center_y-4), 3)
		pygame.draw.line(screen, BROWN, (center_x+4, center_y-10), (center_x+4, center_y-4), 3)
		# Draw cherry bodies
		pygame.draw.circle(screen, self.fruit_type[2], (center_x-4, center_y), 6)
		pygame.draw.circle(screen, self.fruit_type[2], (center_x+4, center_y), 6)
		# Highlight
		pygame.draw.circle(screen, WHITE, (center_x-6, center_y-2), 2)
		pygame.draw.circle(screen, WHITE, (center_x+2, center_y-2), 2)

	def draw_strawberry(self, screen, center_x, center_y):
		# Draw strawberry body
		points = [(center_x, center_y+8), (center_x-6, center_y), (center_x-4, center_y-5),
				 (center_x+4, center_y-5), (center_x+6, center_y)]
		pygame.draw.polygon(screen, self.fruit_type[2], points)
		# Draw leaves
		pygame.draw.rect(screen, self.fruit_type[3], (center_x-5, center_y-8, 10, 4))
		# Draw seeds
		for i in range(3):
			for j in range(2):
				pygame.draw.circle(screen, WHITE, (center_x-4+i*4, center_y-1+j*4), 1)

	def draw_orange(self, screen, center_x, center_y):
		# Draw orange body
		pygame.draw.circle(screen, self.fruit_type[2], (center_x, center_y), 8)
		# Draw orange texture lines
		for angle in range(0, 360, 45):
			end_x = center_x + 6 * math.cos(math.radians(angle))
			end_y = center_y + 6 * math.sin(math.radians(angle))
			pygame.draw.line(screen, DARK_RED, (center_x, center_y), (end_x, end_y), 2)
		# Draw stem
		pygame.draw.circle(screen, self.fruit_type[3], (center_x, center_y-8), 3)

	def draw_apple(self, screen, center_x, center_y):
		# Draw apple body
		pygame.draw.circle(screen, self.fruit_type[2], (center_x, center_y+1), 7)
		# Draw apple indent at top
		pygame.draw.circle(screen, BLACK, (center_x, center_y-5), 4)
		pygame.draw.circle(screen, self.fruit_type[2], (center_x, center_y-3), 4)
		# Draw stem
		pygame.draw.line(screen, BROWN, (center_x, center_y-8), (center_x, center_y-4), 3)
		# Draw leaf
		pygame.draw.circle(screen, self.fruit_type[3], (center_x+3, center_y-6), 3)

	def draw_grapes(self, screen, center_x, center_y):
		# Draw grape cluster
		for row in range(3):
			for col in range(2 - row % 2):
				x = center_x - 4 + col * 8 + (row % 2) * 4
				y = center_y - 5 + row * 4
				pygame.draw.circle(screen, self.fruit_type[2], (x, y), 4)
		# Draw stem
		pygame.draw.line(screen, self.fruit_type[3], (center_x, center_y-9), (center_x, center_y-5), 3)

	def draw_bell(self, screen, center_x, center_y):
		# Draw bell body
		points = [(center_x-8, center_y+5), (center_x-8, center_y-2), (center_x-3, center_y-8),
				 (center_x+3, center_y-8), (center_x+8, center_y-2), (center_x+8, center_y+5)]
		pygame.draw.polygon(screen, self.fruit_type[2], points)
		# Draw bell bottom
		pygame.draw.rect(screen, BROWN, (center_x-9, center_y+5, 18, 3))
		# Draw clapper
		pygame.draw.circle(screen, BLACK, (center_x, center_y+3), 3)
		# Draw highlight
		pygame.draw.circle(screen, WHITE, (center_x-4, center_y-4), 3)

	def draw_key(self, screen, center_x, center_y):
		# Draw key shaft
		pygame.draw.rect(screen, self.fruit_type[2], (center_x-8, center_y-1, 10, 3))
		# Draw key head (circle)
		pygame.draw.circle(screen, self.fruit_type[2], (center_x+8, center_y), 5)
		pygame.draw.circle(screen, BLACK, (center_x+8, center_y), 3)
		# Draw key teeth
		pygame.draw.rect(screen, self.fruit_type[2], (center_x-8, center_y+1, 3, 4))
		pygame.draw.rect(screen, self.fruit_type[2], (center_x-5, center_y+1, 3, 3))

	def draw(self, screen):
		center_x = self.x * CELL_SIZE + CELL_SIZE // 2
		center_y = self.y * CELL_SIZE + CELL_SIZE // 2

		# Draw black background
		pygame.draw.rect(screen, BLACK, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

		# Pulse effect for visibility
		self.pulse_timer += 1
		if self.pulse_timer % 60 < 30:  # Pulse every 2 seconds
			# Draw fruit based on type
			fruit_name = self.fruit_type[0]
			if fruit_name == "cherry":
				self.draw_cherry(screen, center_x, center_y)
			elif fruit_name == "strawberry":
				self.draw_strawberry(screen, center_x, center_y)
			elif fruit_name == "orange":
				self.draw_orange(screen, center_x, center_y)
			elif fruit_name == "apple":
				self.draw_apple(screen, center_x, center_y)
			elif fruit_name == "grapes":
				self.draw_grapes(screen, center_x, center_y)
			elif fruit_name == "bell":
				self.draw_bell(screen, center_x, center_y)
			elif fruit_name == "key":
				self.draw_key(screen, center_x, center_y)

class LifeNotification:
	def __init__(self, message, color=GREEN):
		self.message = message
		self.color = color
		self.timer = 120  # Show for 2 seconds at 60 FPS
		self.alpha = 255

	def update(self):
		self.timer -= 1
		if self.timer < 30:  # Fade out in last 0.5 seconds
			self.alpha = int(255 * (self.timer / 30))
		return self.timer > 0

	def draw(self, screen, font):
		if self.timer > 0:
			# Create surface with text
			text_surface = font.render(self.message, True, self.color)

			# Apply alpha transparency
			if self.alpha < 255:
				text_surface.set_alpha(self.alpha)

			# Center text on screen
			text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
			screen.blit(text_surface, text_rect)

class WinDialog:
	def __init__(self, screen, score, level):
		self.screen = screen
		self.score = score
		self.level = level
		self.font_large = pygame.font.Font(None, 48)
		self.font_medium = pygame.font.Font(None, 36)
		self.font_small = pygame.font.Font(None, 24)

		# Dialog dimensions
		self.width = 450
		self.height = 280
		self.x = (WINDOW_WIDTH - self.width) // 2
		self.y = (WINDOW_HEIGHT - self.height) // 2

		# Button dimensions
		self.button_width = 140
		self.button_height = 40
		self.continue_button_rect = pygame.Rect(
			self.x + 50, self.y + self.height - 80,
			self.button_width, self.button_height
		)
		self.quit_button_rect = pygame.Rect(
			self.x + self.width - 190, self.y + self.height - 80,
			self.button_width, self.button_height
		)

	def draw(self):
		# Draw semi-transparent overlay
		overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		overlay.set_alpha(128)
		overlay.fill(BLACK)
		self.screen.blit(overlay, (0, 0))

		# Draw dialog box
		pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height))
		pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height), 3)

		# Draw title
		title_text = self.font_large.render("🎉 LEVEL COMPLETE! 🎉", True, GREEN)
		title_rect = title_text.get_rect(center=(self.x + self.width//2, self.y + 35))
		self.screen.blit(title_text, title_rect)

		# Draw level info
		level_text = self.font_medium.render(f"Level {self.level} Cleared!", True, BLACK)
		level_rect = level_text.get_rect(center=(self.x + self.width//2, self.y + 75))
		self.screen.blit(level_text, level_rect)

		# Draw score
		score_text = self.font_medium.render(f"Score: {self.score}", True, BLACK)
		score_rect = score_text.get_rect(center=(self.x + self.width//2, self.y + 110))
		self.screen.blit(score_text, score_rect)

		# Draw message
		msg_text = self.font_medium.render("All dots collected!", True, BLACK)
		msg_rect = msg_text.get_rect(center=(self.x + self.width//2, self.y + 140))
		self.screen.blit(msg_text, msg_rect)

		# Draw question
		question_text = self.font_medium.render("Continue to next level?", True, BLACK)
		question_rect = question_text.get_rect(center=(self.x + self.width//2, self.y + 175))
		self.screen.blit(question_text, question_rect)

		# Draw buttons
		pygame.draw.rect(self.screen, GREEN, self.continue_button_rect)
		pygame.draw.rect(self.screen, BLACK, self.continue_button_rect, 2)
		continue_text = self.font_small.render("NEXT LEVEL", True, BLACK)
		continue_text_rect = continue_text.get_rect(center=self.continue_button_rect.center)
		self.screen.blit(continue_text, continue_text_rect)

		pygame.draw.rect(self.screen, RED, self.quit_button_rect)
		pygame.draw.rect(self.screen, BLACK, self.quit_button_rect, 2)
		quit_text = self.font_small.render("QUIT", True, WHITE)
		quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
		self.screen.blit(quit_text, quit_text_rect)

	def handle_click(self, pos):
		if self.continue_button_rect.collidepoint(pos):
			return "continue"
		elif self.quit_button_rect.collidepoint(pos):
			return "quit"
		return None

class Game:
	def __init__(self, screen=None):
		if screen is None:
			self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
			pygame.display.set_caption("Pac-Man Game - Spread Out Ghosts & No Disappearing")
			self.own_screen = True
		else:
			self.screen = screen
			self.own_screen = False
		self.clock = pygame.time.Clock()
		self.pacman = PacMan(1)  # Initialize with level 1
		self.maze = [row[:] for row in MAZE]  # Copy the maze
		self.score = 0
		self.level = 1
		self.lives = MAX_LIVES
		self.last_extra_life_score = 0
		self.dots_remaining = self.count_dots()
		self.super_dots_remaining = self.count_super_dots()
		self.game_over = False
		self.won = False
		self.show_win_dialog = False
		self.life_notification = None
		self.life_lost_timer = 0

		# Create ultra-smart ghosts with different personalities and IDs
		self.ghosts = [
			Ghost(9, 9, RED, "aggressive", 0),      # Red ghost - aggressive chaser
			Ghost(10, 9, PINK, "ambush", 1),        # Pink ghost - ambush tactics
			Ghost(9, 10, CYAN, "patrol", 2),        # Cyan ghost - patrol behavior
			Ghost(10, 10, ORANGE, "unpredictable", 3)  # Orange ghost - unpredictable
		]

		# Fruit system
		self.current_fruit = None
		self.fruit_spawn_timer = 0
		self.fruit_spawn_interval = max(150, 300 - (self.level * 20))  # Faster spawning at higher levels

		# Ghost eating system
		self.ghost_eat_multiplier = 1

		# Fonts - adjusted for larger display
		self.font = pygame.font.Font(None, 32)
		self.font_large = pygame.font.Font(None, 40)
		self.font_notification = pygame.font.Font(None, 52)
		self.win_dialog = None

	def get_level_difficulty(self):
		"""Return difficulty multipliers based on level"""
		speed_multiplier = 1.0 + (self.level - 1) * 0.3  # Ghosts get 30% faster each level
		power_duration = max(100, 200 - (self.level - 1) * 15)  # Power pellets last shorter
		return speed_multiplier, power_duration

	def check_extra_life(self):
		"""Check if player earned an extra life"""
		for threshold in EXTRA_LIFE_SCORES:
			if (self.score >= threshold and
				self.last_extra_life_score < threshold and
				self.lives < MAX_LIVES):
				self.lives += 1
				self.last_extra_life_score = threshold
				self.life_notification = LifeNotification("EXTRA LIFE!", GREEN)
				return True
		return False

	def lose_life(self):
		"""Lose a life and reset positions"""
		self.lives -= 1
		self.life_lost_timer = 90  # 1.5 second pause

		if self.lives <= 0:
			self.game_over = True
			self.life_notification = LifeNotification("GAME OVER!", RED)
		else:
			# Reset positions
			self.pacman.reset_position()
			for ghost in self.ghosts:
				ghost.reset_position()
			self.life_notification = LifeNotification(f"LIFE LOST! {self.lives} REMAINING", ORANGE)

	def count_dots(self):
		count = 0
		for row in self.maze:
			for cell in row:
				if cell == 2:  # 2 = regular dot
					count += 1
		return count

	def count_super_dots(self):
		count = 0
		for row in self.maze:
			for cell in row:
				if cell == 4:  # 4 = super dot
					count += 1
		return count

	def spawn_fruit(self):
		# Find empty spaces to spawn fruit, excluding ghost base
		empty_spaces = []
		for y, row in enumerate(self.maze):
			for x, cell in enumerate(row):
				if cell == 0 and (x, y) not in GHOST_BASE_COORDS:  # Empty space, not in ghost base
					empty_spaces.append((x, y))

		if empty_spaces:
			x, y = random.choice(empty_spaces)
			self.current_fruit = Fruit(x, y)

	def draw_maze(self):
		for y, row in enumerate(self.maze):
			for x, cell in enumerate(row):
				rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

				if cell == 1:  # Wall
					pygame.draw.rect(self.screen, BLUE, rect)
				elif cell == 2:  # Regular dot
					pygame.draw.rect(self.screen, BLACK, rect)
					center_x = x * CELL_SIZE + CELL_SIZE // 2
					center_y = y * CELL_SIZE + CELL_SIZE // 2
					pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 4)
				elif cell == 4:  # Super dot (power pellet)
					pygame.draw.rect(self.screen, BLACK, rect)
					center_x = x * CELL_SIZE + CELL_SIZE // 2
					center_y = y * CELL_SIZE + CELL_SIZE // 2
					pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 10)
					pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), 8)
				else:  # Empty space
					pygame.draw.rect(self.screen, BLACK, rect)

		# Draw fruit if it exists and not expired
		if self.current_fruit and not self.current_fruit.is_expired():
			self.current_fruit.draw(self.screen)
		elif self.current_fruit and self.current_fruit.is_expired():
			self.current_fruit = None

	def collect_items(self):
		cell = self.maze[self.pacman.y][self.pacman.x]

		if cell == 2:  # Regular dot
			self.maze[self.pacman.y][self.pacman.x] = 0
			self.score += 10
			self.dots_remaining -= 1

		elif cell == 4:  # Super dot (power pellet)
			self.maze[self.pacman.y][self.pacman.x] = 0
			self.score += 50
			self.super_dots_remaining -= 1
			# Make all ghosts vulnerable with level-adjusted duration
			speed_multiplier, power_duration = self.get_level_difficulty()
			for ghost in self.ghosts:
				ghost.set_vulnerable(power_duration)
			self.ghost_eat_multiplier = 1  # Reset multiplier

		# Check for fruit collection
		if (self.current_fruit and
			self.pacman.x == self.current_fruit.x and
			self.pacman.y == self.current_fruit.y):
			self.score += self.current_fruit.get_points()
			self.current_fruit = None

		# Check for extra life
		self.check_extra_life()

		# Check win condition
		if self.dots_remaining == 0 and self.super_dots_remaining == 0:
			self.won = True
			self.show_win_dialog = True
			self.win_dialog = WinDialog(self.screen, self.score, self.level)

	def check_ghost_collision(self):
		for i, ghost in enumerate(self.ghosts):
			if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
				if ghost.vulnerable and not ghost.eaten:
					# Eat the ghost!
					ghost.eaten = True
					ghost.returning_home = True
					points = 200 * self.ghost_eat_multiplier
					self.score += points
					self.ghost_eat_multiplier *= 2  # Double points for next ghost
					return False  # Don't end game
				elif not ghost.vulnerable:
					self.lose_life()
					return True
		return False

	def update_fruit_spawning(self):
		self.fruit_spawn_timer += 1
		if self.fruit_spawn_timer >= self.fruit_spawn_interval and not self.current_fruit:
			self.spawn_fruit()
			self.fruit_spawn_timer = 0

	def next_level(self):
		# Keep score, increment level, reset maze
		self.level += 1
		self.pacman = PacMan(self.level)  # Create new Pac-Man with level speed
		self.maze = [row[:] for row in MAZE]
		self.dots_remaining = self.count_dots()
		self.super_dots_remaining = self.count_super_dots()
		self.won = False
		self.show_win_dialog = False
		self.win_dialog = None
		self.current_fruit = None
		self.fruit_spawn_timer = 0
		self.ghost_eat_multiplier = 1
		self.life_lost_timer = 0

		# Update fruit spawn interval for higher levels
		self.fruit_spawn_interval = max(150, 300 - (self.level * 20))

		# Reset ghosts with proper IDs
		self.ghosts = [
			Ghost(9, 9, RED, "aggressive", 0),
			Ghost(10, 9, PINK, "ambush", 1),
			Ghost(9, 10, CYAN, "patrol", 2),
			Ghost(10, 10, ORANGE, "unpredictable", 3)
		]

	def draw_lives(self, ui_y):
		"""Draw life indicators in the UI"""
		life_text = self.font_large.render("LIVES:", True, WHITE)
		self.screen.blit(life_text, (520, ui_y + 15))

		# Draw Pac-Man symbols for each life
		for i in range(self.lives):
			life_x = 620 + i * 30
			life_y = ui_y + 25
			# Draw mini Pac-Man (larger for bigger display)
			pygame.draw.circle(self.screen, YELLOW, (life_x, life_y), 10)
			# Draw small mouth
			mouth_points = [
				(life_x, life_y),
				(life_x + 8, life_y - 4),
				(life_x + 8, life_y + 4)
			]
			pygame.draw.polygon(self.screen, BLACK, mouth_points)

	def draw_ui(self):
		# UI area background
		ui_y = len(self.maze) * CELL_SIZE
		pygame.draw.rect(self.screen, GRAY, (0, ui_y, WINDOW_WIDTH, WINDOW_HEIGHT - ui_y))

		# Score
		score_text = self.font_large.render(f"SCORE: {self.score}", True, WHITE)
		self.screen.blit(score_text, (20, ui_y + 15))

		# Level
		level_text = self.font_large.render(f"LEVEL: {self.level}", True, YELLOW)
		self.screen.blit(level_text, (200, ui_y + 15))

		# Speed indicator
		speed_text = self.font.render(f"Speed: {2.0 - self.pacman.move_delay:.1f}x", True, CYAN)
		self.screen.blit(speed_text, (320, ui_y + 20))

		# Lives
		self.draw_lives(ui_y)

		# Dots remaining
		dots_text = self.font.render(f"Dots: {self.dots_remaining} | Super Dots: {self.super_dots_remaining}", True, WHITE)
		self.screen.blit(dots_text, (20, ui_y + 50))

		# Next extra life info
		next_threshold = None
		for threshold in EXTRA_LIFE_SCORES:
			if self.score < threshold:
				next_threshold = threshold
				break

		if next_threshold and self.lives < MAX_LIVES:
			extra_life_text = self.font.render(f"Extra life at: {next_threshold}", True, GREEN)
			self.screen.blit(extra_life_text, (350, ui_y + 50))

		if self.game_over and self.lives <= 0:
			# Game over message
			game_over_text = self.font.render("ALL LIVES LOST! Press R to restart or ESC to quit", True, RED)
			self.screen.blit(game_over_text, (20, ui_y + 80))
		elif not self.show_win_dialog and not self.life_lost_timer:
			# Instructions
			instruction_text = self.font.render("WASD/Arrows: Move | Ghosts spread out and hunt strategically!", True, WHITE)
			self.screen.blit(instruction_text, (20, ui_y + 80))

	def restart_game(self):
		self.pacman = PacMan(1)  # Reset to level 1 speed
		self.maze = [row[:] for row in MAZE]
		self.score = 0
		self.level = 1
		self.lives = MAX_LIVES
		self.last_extra_life_score = 0
		self.dots_remaining = self.count_dots()
		self.super_dots_remaining = self.count_super_dots()
		self.game_over = False
		self.won = False
		self.show_win_dialog = False
		self.win_dialog = None
		self.current_fruit = None
		self.fruit_spawn_timer = 0
		self.fruit_spawn_interval = 300
		self.ghost_eat_multiplier = 1
		self.life_notification = None
		self.life_lost_timer = 0

		# Reset ghosts with proper IDs
		self.ghosts = [
			Ghost(9, 9, RED, "aggressive", 0),
			Ghost(10, 9, PINK, "ambush", 1),
			Ghost(9, 10, CYAN, "patrol", 2),
			Ghost(10, 10, ORANGE, "unpredictable", 3)
		]

	def handle_input(self):
		if self.game_over or self.show_win_dialog or self.life_lost_timer > 0:
			return

		# Handle continuous key presses for smooth movement
		keys = pygame.key.get_pressed()

		moved = False
		# Arrow keys
		if keys[pygame.K_LEFT]:
			moved = self.pacman.move(-1, 0, self.maze)
		elif keys[pygame.K_RIGHT]:
			moved = self.pacman.move(1, 0, self.maze)
		elif keys[pygame.K_UP]:
			moved = self.pacman.move(0, -1, self.maze)
		elif keys[pygame.K_DOWN]:
			moved = self.pacman.move(0, 1, self.maze)

		# WASD keys
		elif keys[pygame.K_a]:
			moved = self.pacman.move(-1, 0, self.maze)
		elif keys[pygame.K_d]:
			moved = self.pacman.move(1, 0, self.maze)
		elif keys[pygame.K_w]:
			moved = self.pacman.move(0, -1, self.maze)
		elif keys[pygame.K_s]:
			moved = self.pacman.move(0, 1, self.maze)

		if moved:
			self.collect_items()

	def run(self):
		running = True

		while running:
			# Handle events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					if self.own_screen:
						pygame.quit()
						sys.exit()
					else:
						return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						if self.own_screen:
							running = False
						else:
							return "menu"
					elif event.key == pygame.K_r and self.game_over:
						self.restart_game()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if self.show_win_dialog and self.win_dialog:
						result = self.win_dialog.handle_click(event.pos)
						if result == "continue":
							self.next_level()
						elif result == "quit":
							if self.own_screen:
								running = False
							else:
								return "menu"

			# Update life lost timer
			if self.life_lost_timer > 0:
				self.life_lost_timer -= 1

			if not self.game_over and not self.show_win_dialog and self.life_lost_timer == 0:
				# Handle input
				self.handle_input()

				# Update Pac-Man animation
				self.pacman.update()

				# Update fruit spawning
				self.update_fruit_spawning()

				# Move ghosts with ultra-smart AI and level-based speed - PASS ALL GHOSTS
				speed_multiplier, _ = self.get_level_difficulty()
				for ghost in self.ghosts:
					ghost.move(self.maze, self.pacman.x, self.pacman.y, self.pacman.direction, speed_multiplier, self.ghosts)

				# Check for collisions
				self.check_ghost_collision()

			# Update life notification
			if self.life_notification:
				if not self.life_notification.update():
					self.life_notification = None

			# Clear screen
			self.screen.fill(BLACK)

			# Draw everything
			self.draw_maze()

			if not self.game_over or self.lives > 0:
				self.pacman.draw(self.screen)
				for ghost in self.ghosts:
					ghost.draw(self.screen)

			self.draw_ui()

			# Draw life notification
			if self.life_notification:
				self.life_notification.draw(self.screen, self.font_notification)

			# Draw win dialog if needed
			if self.show_win_dialog and self.win_dialog:
				self.win_dialog.draw()

			# Update display
			pygame.display.flip()
			self.clock.tick(15)  # 15 FPS for good responsiveness

		if self.own_screen:
			pygame.quit()
			sys.exit()
		else:
			return "menu"

if __name__ == "__main__":
	game = Game()
	game.run()