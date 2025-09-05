import pygame
import sys
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
CELL_SIZE = 30
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

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Maze layout (1 = wall, 0 = empty, 2 = dot, 3 = pacman start)
MAZE = [
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
	[1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
	[1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
	[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
	[1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
	[1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
	[1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
	[0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
	[1,1,1,1,2,1,0,1,1,0,0,1,1,0,1,2,1,1,1,1],
	[0,0,0,0,2,0,0,1,0,0,0,0,1,0,0,2,0,0,0,0],
	[1,1,1,1,2,1,0,1,0,0,0,0,1,0,1,2,1,1,1,1],
	[0,0,0,1,2,1,0,1,1,1,1,1,1,0,1,2,1,0,0,0],
	[1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
	[1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
	[1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
	[1,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,1],
	[1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
	[1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
	[1,2,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
	[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
	[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

class PacMan:
	def __init__(self):
		self.x = 1
		self.y = 1
		self.direction = RIGHT
		self.mouth_open = True
		self.mouth_timer = 0

	def move(self, dx, dy, maze):
		new_x = self.x + dx
		new_y = self.y + dy

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
	def __init__(self, x, y, color, personality="aggressive"):
		self.x = x
		self.y = y
		self.start_x = x
		self.start_y = y
		self.color = color
		self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
		self.move_timer = 0
		self.personality = personality
		self.stuck_counter = 0
		self.last_position = (x, y)
		self.target_x = x
		self.target_y = y

	def find_path_to_target(self, maze, target_x, target_y):
		"""Simple BFS pathfinding to target"""
		queue = deque([(self.x, self.y, [])])
		visited = set()
		visited.add((self.x, self.y))

		while queue:
			x, y, path = queue.popleft()

			if x == target_x and y == target_y:
				return path

			if len(path) > 15:  # Limit search depth
				continue

			for dx, dy in [UP, DOWN, LEFT, RIGHT]:
				new_x, new_y = x + dx, y + dy

				if ((new_x, new_y) not in visited and
					0 <= new_x < len(maze[0]) and
					0 <= new_y < len(maze) and
					maze[new_y][new_x] != 1):

					visited.add((new_x, new_y))
					new_path = path + [(dx, dy)]
					queue.append((new_x, new_y, new_path))

		return []

	def get_valid_moves(self, maze):
		valid_moves = []
		for dx, dy in [UP, DOWN, LEFT, RIGHT]:
			new_x = self.x + dx
			new_y = self.y + dy
			if (0 <= new_x < len(maze[0]) and
				0 <= new_y < len(maze) and
				maze[new_y][new_x] != 1):  # Not a wall
				valid_moves.append((dx, dy))
		return valid_moves

	def choose_smart_move(self, maze, pacman_x, pacman_y):
		"""Smart movement based on personality"""
		valid_moves = self.get_valid_moves(maze)
		if not valid_moves:
			return (0, 0)

		# Check if stuck in the same position
		if (self.x, self.y) == self.last_position:
			self.stuck_counter += 1
		else:
			self.stuck_counter = 0
			self.last_position = (self.x, self.y)

		# If stuck, try random movement
		if self.stuck_counter > 3:
			self.stuck_counter = 0
			return random.choice(valid_moves)

		if self.personality == "aggressive":
			# Red ghost - direct pursuit using pathfinding
			path = self.find_path_to_target(maze, pacman_x, pacman_y)
			if path and len(path) > 0:
				return path[0]

		elif self.personality == "ambush":
			# Pink ghost - tries to ambush 4 spaces ahead of Pac-Man
			# This is simplified - just tries to get closer to pacman's projected position
			projected_x = pacman_x + 4 * (1 if random.random() > 0.5 else -1)
			projected_y = pacman_y + 4 * (1 if random.random() > 0.5 else -1)
			path = self.find_path_to_target(maze, projected_x, projected_y)
			if path and len(path) > 0:
				return path[0]

		elif self.personality == "patrol":
			# Cyan ghost - patrols corners but still chases
			distance_to_pacman = abs(self.x - pacman_x) + abs(self.y - pacman_y)
			if distance_to_pacman > 8:
				# Far away, move towards pacman
				path = self.find_path_to_target(maze, pacman_x, pacman_y)
				if path and len(path) > 0:
					return path[0]
			else:
				# Close to pacman, retreat to corner
				corner_x, corner_y = 1, 1  # Top-left corner
				path = self.find_path_to_target(maze, corner_x, corner_y)
				if path and len(path) > 0:
					return path[0]

		elif self.personality == "unpredictable":
			# Orange ghost - unpredictable behavior
			distance_to_pacman = abs(self.x - pacman_x) + abs(self.y - pacman_y)
			if distance_to_pacman > 8:
				# Far away, chase pacman
				path = self.find_path_to_target(maze, pacman_x, pacman_y)
				if path and len(path) > 0:
					return path[0]
			else:
				# Close to pacman, move randomly or away
				if random.random() < 0.6:
					# Move away from pacman
					best_move = None
					max_distance = 0
					for dx, dy in valid_moves:
						new_x, new_y = self.x + dx, self.y + dy
						distance = abs(new_x - pacman_x) + abs(new_y - pacman_y)
						if distance > max_distance:
							max_distance = distance
							best_move = (dx, dy)
					if best_move:
						return best_move

		# Fallback: smart chase
		path = self.find_path_to_target(maze, pacman_x, pacman_y)
		if path and len(path) > 0:
			return path[0]

		# Final fallback: avoid going backwards if possible
		opposite_dir = (-self.direction[0], -self.direction[1])
		forward_moves = [move for move in valid_moves if move != opposite_dir]
		if forward_moves:
			return random.choice(forward_moves)

		return random.choice(valid_moves)

	def move(self, maze, pacman_x, pacman_y):
		self.move_timer += 1
		if self.move_timer < 6:  # Move a bit faster than before
			return

		self.move_timer = 0

		# Choose move based on smart AI
		dx, dy = self.choose_smart_move(maze, pacman_x, pacman_y)

		# Apply movement
		new_x = self.x + dx
		new_y = self.y + dy
		if (0 <= new_x < len(maze[0]) and
			0 <= new_y < len(maze) and
			maze[new_y][new_x] != 1):
			self.x = new_x
			self.y = new_y
			self.direction = (dx, dy)

	def draw(self, screen):
		center_x = self.x * CELL_SIZE + CELL_SIZE // 2
		center_y = self.y * CELL_SIZE + CELL_SIZE // 2
		radius = CELL_SIZE // 3

		# Draw ghost body (circle + rectangle)
		pygame.draw.circle(screen, self.color, (center_x, center_y - 2), radius)
		pygame.draw.rect(screen, self.color,
						(center_x - radius, center_y - 2, radius * 2, radius + 2))

		# Draw wavy bottom
		wave_points = []
		for i in range(5):
			x = center_x - radius + (i * radius * 2 // 4)
			y = center_y + radius if i % 2 == 0 else center_y + radius - 4
			wave_points.append((x, y))
		wave_points.append((center_x + radius, center_y + radius))
		wave_points.append((center_x - radius, center_y + radius))
		pygame.draw.polygon(screen, self.color, wave_points)

		# Draw eyes
		eye_size = 3
		pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 8), eye_size)
		pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 8), eye_size)
		pygame.draw.circle(screen, BLACK, (center_x - 6, center_y - 8), 2)
		pygame.draw.circle(screen, BLACK, (center_x + 6, center_y - 8), 2)

class WinDialog:
	def __init__(self, screen, score):
		self.screen = screen
		self.score = score
		self.font_large = pygame.font.Font(None, 48)
		self.font_medium = pygame.font.Font(None, 36)
		self.font_small = pygame.font.Font(None, 24)

		# Dialog dimensions
		self.width = 400
		self.height = 250
		self.x = (WINDOW_WIDTH - self.width) // 2
		self.y = (WINDOW_HEIGHT - self.height) // 2

		# Button dimensions
		self.button_width = 120
		self.button_height = 40
		self.yes_button_rect = pygame.Rect(
			self.x + 50, self.y + self.height - 80,
			self.button_width, self.button_height
		)
		self.no_button_rect = pygame.Rect(
			self.x + self.width - 170, self.y + self.height - 80,
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
		title_text = self.font_large.render("🎉 CONGRATULATIONS! 🎉", True, GREEN)
		title_rect = title_text.get_rect(center=(self.x + self.width//2, self.y + 40))
		self.screen.blit(title_text, title_rect)

		# Draw score
		score_text = self.font_medium.render(f"Final Score: {self.score}", True, BLACK)
		score_rect = score_text.get_rect(center=(self.x + self.width//2, self.y + 80))
		self.screen.blit(score_text, score_rect)

		# Draw message
		msg_text = self.font_medium.render("You collected all the dots!", True, BLACK)
		msg_rect = msg_text.get_rect(center=(self.x + self.width//2, self.y + 110))
		self.screen.blit(msg_text, msg_rect)

		# Draw question
		question_text = self.font_medium.render("Play again?", True, BLACK)
		question_rect = question_text.get_rect(center=(self.x + self.width//2, self.y + 150))
		self.screen.blit(question_text, question_rect)

		# Draw buttons
		pygame.draw.rect(self.screen, GREEN, self.yes_button_rect)
		pygame.draw.rect(self.screen, BLACK, self.yes_button_rect, 2)
		yes_text = self.font_small.render("YES", True, BLACK)
		yes_text_rect = yes_text.get_rect(center=self.yes_button_rect.center)
		self.screen.blit(yes_text, yes_text_rect)

		pygame.draw.rect(self.screen, RED, self.no_button_rect)
		pygame.draw.rect(self.screen, BLACK, self.no_button_rect, 2)
		no_text = self.font_small.render("NO", True, WHITE)
		no_text_rect = no_text.get_rect(center=self.no_button_rect.center)
		self.screen.blit(no_text, no_text_rect)

	def handle_click(self, pos):
		if self.yes_button_rect.collidepoint(pos):
			return "yes"
		elif self.no_button_rect.collidepoint(pos):
			return "no"
		return None

class Game:
	def __init__(self):
		self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption("Pac-Man Game - Smart Ghosts Edition")
		self.clock = pygame.time.Clock()
		self.pacman = PacMan()
		self.maze = [row[:] for row in MAZE]  # Copy the maze
		self.score = 0
		self.dots_remaining = self.count_dots()
		self.game_over = False
		self.won = False
		self.show_win_dialog = False

		# Create smarter ghosts with different personalities
		self.ghosts = [
			Ghost(9, 9, RED, "aggressive"),      # Red ghost - aggressive chaser
			Ghost(10, 9, PINK, "ambush"),        # Pink ghost - ambush tactics
			Ghost(9, 10, CYAN, "patrol"),        # Cyan ghost - patrol behavior
			Ghost(10, 10, ORANGE, "unpredictable")  # Orange ghost - unpredictable
		]

		# Font for text
		self.font = pygame.font.Font(None, 36)
		self.win_dialog = None

	def count_dots(self):
		count = 0
		for row in self.maze:
			for cell in row:
				if cell == 2:  # 2 = dot
					count += 1
		return count

	def draw_maze(self):
		for y, row in enumerate(self.maze):
			for x, cell in enumerate(row):
				rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

				if cell == 1:  # Wall
					pygame.draw.rect(self.screen, BLUE, rect)
				elif cell == 2:  # Dot
					pygame.draw.rect(self.screen, BLACK, rect)
					center_x = x * CELL_SIZE + CELL_SIZE // 2
					center_y = y * CELL_SIZE + CELL_SIZE // 2
					pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 3)
				else:  # Empty space
					pygame.draw.rect(self.screen, BLACK, rect)

	def collect_dot(self):
		if self.maze[self.pacman.y][self.pacman.x] == 2:
			self.maze[self.pacman.y][self.pacman.x] = 0  # Remove dot
			self.score += 10
			self.dots_remaining -= 1

			if self.dots_remaining == 0:
				self.won = True
				self.show_win_dialog = True
				self.win_dialog = WinDialog(self.screen, self.score)

	def check_ghost_collision(self):
		for ghost in self.ghosts:
			if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
				self.game_over = True
				return True
		return False

	def draw_ui(self):
		# Score
		score_text = self.font.render(f"Score: {self.score}", True, WHITE)
		self.screen.blit(score_text, (10, len(self.maze) * CELL_SIZE + 10))

		# Dots remaining
		dots_text = self.font.render(f"Dots: {self.dots_remaining}", True, WHITE)
		self.screen.blit(dots_text, (200, len(self.maze) * CELL_SIZE + 10))

		if self.game_over:
			# Game over message
			game_over_text = self.font.render("GAME OVER! Press R to restart or ESC to quit", True, RED)
			self.screen.blit(game_over_text, (10, len(self.maze) * CELL_SIZE + 50))
		elif not self.show_win_dialog:
			# Instructions
			instruction_text = self.font.render("Use arrow keys or WASD to move! Avoid the smart ghosts!", True, WHITE)
			self.screen.blit(instruction_text, (10, len(self.maze) * CELL_SIZE + 50))

	def restart_game(self):
		self.pacman = PacMan()
		self.maze = [row[:] for row in MAZE]
		self.score = 0
		self.dots_remaining = self.count_dots()
		self.game_over = False
		self.won = False
		self.show_win_dialog = False
		self.win_dialog = None

		# Reset ghosts
		self.ghosts = [
			Ghost(9, 9, RED, "aggressive"),
			Ghost(10, 9, PINK, "ambush"),
			Ghost(9, 10, CYAN, "patrol"),
			Ghost(10, 10, ORANGE, "unpredictable")
		]

	def handle_input(self):
		if self.game_over or self.show_win_dialog:
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
			self.collect_dot()

	def run(self):
		running = True

		while running:
			# Handle events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
					elif event.key == pygame.K_r and self.game_over:
						self.restart_game()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if self.show_win_dialog and self.win_dialog:
						result = self.win_dialog.handle_click(event.pos)
						if result == "yes":
							self.restart_game()
						elif result == "no":
							running = False

			if not self.game_over and not self.show_win_dialog:
				# Handle input
				self.handle_input()

				# Update Pac-Man animation
				self.pacman.update()

				# Move ghosts with smart AI
				for ghost in self.ghosts:
					ghost.move(self.maze, self.pacman.x, self.pacman.y)

				# Check for collisions
				self.check_ghost_collision()

			# Clear screen
			self.screen.fill(BLACK)

			# Draw everything
			self.draw_maze()

			if not self.game_over:
				self.pacman.draw(self.screen)
				for ghost in self.ghosts:
					ghost.draw(self.screen)

			self.draw_ui()

			# Draw win dialog if needed
			if self.show_win_dialog and self.win_dialog:
				self.win_dialog.draw()

			# Update display
			pygame.display.flip()
			self.clock.tick(15)  # 15 FPS for good responsiveness

		pygame.quit()
		sys.exit()

if __name__ == "__main__":
	game = Game()
	game.run()