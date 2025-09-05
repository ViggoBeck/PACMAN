import pygame
import sys
import random
import math
import time
from collections import deque
from pacman import Game as PacManGame

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_BLUE = (0, 0, 139)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)

class ArcadeMenu:
	def __init__(self, screen):
		self.screen = screen
		self.font_title = pygame.font.Font(None, 72)
		self.font_large = pygame.font.Font(None, 48)
		self.font_medium = pygame.font.Font(None, 36)
		self.selected_game = 0
		self.games = [
			{"name": "PAC-MAN", "color": YELLOW, "description": "Eat dots, avoid ghosts!"},
			{"name": "DONKEY KONG", "color": RED, "description": "Climb up, avoid barrels!"},
			{"name": "SNAKE", "color": GREEN, "description": "Grow longer, don't crash!"},
			{"name": "TETRIS", "color": BLUE, "description": "Stack blocks perfectly!"},
			{"name": "FROGGER", "color": GREEN, "description": "Cross the busy road!"},
			{"name": "BREAKOUT", "color": RED, "description": "Bounce ball, break bricks!"}
		]
		self.animation_timer = 0

	def handle_input(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP or event.key == pygame.K_w:
				self.selected_game = (self.selected_game - 1) % len(self.games)
			elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
				self.selected_game = (self.selected_game + 1) % len(self.games)
			elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
				return self.selected_game
		return None

	def update(self):
		self.animation_timer += 1

	def draw(self):
		# Background gradient effect
		for y in range(WINDOW_HEIGHT):
			color_intensity = int(20 + 15 * math.sin(y * 0.01 + self.animation_timer * 0.05))
			pygame.draw.line(self.screen, (color_intensity, 0, color_intensity), (0, y), (WINDOW_WIDTH, y))

		# Title
		title_text = self.font_title.render("RETRO ARCADE", True, WHITE)
		title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
		self.screen.blit(title_text, title_rect)

		# Subtitle
		subtitle_text = self.font_medium.render("Choose Your Game", True, CYAN)
		subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
		self.screen.blit(subtitle_text, subtitle_rect)

		# Game list
		start_y = 220
		for i, game in enumerate(self.games):
			y_pos = start_y + i * 80

			# Selection highlight
			if i == self.selected_game:
				# Animated selection box
				pulse = int(10 + 5 * math.sin(self.animation_timer * 0.2))
				highlight_rect = pygame.Rect(50, y_pos - 25, WINDOW_WIDTH - 100, 60)
				pygame.draw.rect(self.screen, (pulse, pulse, pulse), highlight_rect, 3)
				pygame.draw.rect(self.screen, (pulse//3, pulse//3, pulse//3), highlight_rect)

			# Game name
			game_color = game["color"] if i == self.selected_game else WHITE
			game_text = self.font_large.render(game["name"], True, game_color)
			self.screen.blit(game_text, (100, y_pos - 15))

			# Game description
			if i == self.selected_game:
				desc_text = self.font_medium.render(game["description"], True, CYAN)
				self.screen.blit(desc_text, (100, y_pos + 20))

		# Instructions
		instructions = [
			"↑↓ or W/S: Select Game",
			"ENTER or SPACE: Start Game",
			"ESC: Quit Arcade"
		]

		for i, instruction in enumerate(instructions):
			inst_text = self.font_medium.render(instruction, True, WHITE)
			self.screen.blit(inst_text, (50, WINDOW_HEIGHT - 120 + i * 30))



class SnakeGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.running = True
		self.snake = [(10, 10), (9, 10), (8, 10)]
		self.food = (15, 15)
		self.direction = (1, 0)
		self.score = 0
		self.cell_size = 20
		self.last_move_time = 0

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			current_time = pygame.time.get_ticks()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"
					elif event.key == pygame.K_UP and self.direction != (0, 1):
						self.direction = (0, -1)
					elif event.key == pygame.K_DOWN and self.direction != (0, -1):
						self.direction = (0, 1)
					elif event.key == pygame.K_LEFT and self.direction != (1, 0):
						self.direction = (-1, 0)
					elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
						self.direction = (1, 0)

			# Move snake every 150ms
			if current_time - self.last_move_time > 150:
				self.last_move_time = current_time
				head = self.snake[0]
				new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

				# Check boundaries
				if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH // self.cell_size or
					new_head[1] < 0 or new_head[1] >= (WINDOW_HEIGHT - 100) // self.cell_size):
					# Game over - restart
					self.snake = [(10, 10), (9, 10), (8, 10)]
					self.direction = (1, 0)
					self.score = 0
					self.food = (15, 15)
					continue

				# Check self collision
				if new_head in self.snake:
					# Game over - restart
					self.snake = [(10, 10), (9, 10), (8, 10)]
					self.direction = (1, 0)
					self.score = 0
					self.food = (15, 15)
					continue

				self.snake.insert(0, new_head)

				# Check food collision
				if new_head == self.food:
					self.score += 10
					# Generate new food
					while True:
						new_food = (random.randint(0, WINDOW_WIDTH // self.cell_size - 1),
								   random.randint(0, (WINDOW_HEIGHT - 100) // self.cell_size - 1))
						if new_food not in self.snake:
							self.food = new_food
							break
				else:
					self.snake.pop()

			# Draw everything
			self.screen.fill(BLACK)

			# Draw snake
			for segment in self.snake:
				rect = pygame.Rect(segment[0] * self.cell_size, segment[1] * self.cell_size,
								 self.cell_size - 1, self.cell_size - 1)
				pygame.draw.rect(self.screen, GREEN, rect)

			# Draw food
			food_rect = pygame.Rect(self.food[0] * self.cell_size, self.food[1] * self.cell_size,
								   self.cell_size - 1, self.cell_size - 1)
			pygame.draw.rect(self.screen, RED, food_rect)

			# Draw UI
			score_text = self.font.render(f"SNAKE - Score: {self.score}", True, WHITE)
			self.screen.blit(score_text, (10, WINDOW_HEIGHT - 80))

			back_text = self.font.render("Press ESC to return to menu", True, WHITE)
			self.screen.blit(back_text, (10, WINDOW_HEIGHT - 40))

			pygame.display.flip()
			clock.tick(60)

		return "menu"

class TetrisGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 48)
		self.running = True
		self.game_time = 0

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"

			self.game_time += 1
			self.screen.fill(BLACK)

			# Title
			title_text = self.font.render("TETRIS", True, BLUE)
			title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
			self.screen.blit(title_text, title_rect)

			# Game board outline
			board_x = WINDOW_WIDTH // 2 - 150
			board_y = 150
			pygame.draw.rect(self.screen, WHITE, (board_x, board_y, 300, 500), 2)

			# Animated falling blocks
			for i in range(5):
				block_y = (board_y + 50 + (self.game_time + i * 20) % 400)
				colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
				pygame.draw.rect(self.screen, colors[i],
							   (board_x + 50 + i * 40, block_y, 30, 30))

			# Instructions
			inst_text = self.font.render("Coming Soon!", True, WHITE)
			inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 700))
			self.screen.blit(inst_text, inst_rect)

			back_text = self.font.render("Press ESC to return to menu", True, WHITE)
			back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, 750))
			self.screen.blit(back_text, back_rect)

			pygame.display.flip()
			clock.tick(60)

		return "menu"

class DonkeyKongGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.font_large = pygame.font.Font(None, 48)
		self.running = True

		# Mario properties
		self.mario_x = 50
		self.mario_y = WINDOW_HEIGHT - 212  # Position Mario on bottom platform
		self.mario_dy = 0
		self.mario_on_ground = True  # Start on ground
		self.mario_on_ladder = False
		self.mario_climbing = False
		self.mario_facing_right = True
		self.mario_width = 24
		self.mario_height = 32
		self.mario_animation_frame = 0

		# Game properties
		self.score = 0
		self.lives = 3
		self.level = 1

		# Platform levels (y positions) - more authentic spacing
		self.platforms = [
			{'y': WINDOW_HEIGHT - 180, 'x_start': 0, 'x_end': WINDOW_WIDTH, 'slope': 0},           # Bottom
			{'y': WINDOW_HEIGHT - 300, 'x_start': 100, 'x_end': WINDOW_WIDTH, 'slope': 2},        # Second (sloped)
			{'y': WINDOW_HEIGHT - 420, 'x_start': 0, 'x_end': WINDOW_WIDTH - 100, 'slope': -2},   # Third (reverse slope)
			{'y': WINDOW_HEIGHT - 540, 'x_start': 100, 'x_end': WINDOW_WIDTH, 'slope': 2},        # Fourth (sloped)
			{'y': WINDOW_HEIGHT - 660, 'x_start': 0, 'x_end': WINDOW_WIDTH - 100, 'slope': 0},    # Fifth
			{'y': WINDOW_HEIGHT - 780, 'x_start': 200, 'x_end': WINDOW_WIDTH - 200, 'slope': 0},  # Top platform
		]

		# Ladders (x position, bottom_y, top_y) - fixed positioning
		self.ladders = [
			{'x': 150, 'bottom': WINDOW_HEIGHT - 180, 'top': WINDOW_HEIGHT - 300, 'width': 20},
			{'x': WINDOW_WIDTH - 150, 'bottom': WINDOW_HEIGHT - 300, 'top': WINDOW_HEIGHT - 420, 'width': 20},
			{'x': 150, 'bottom': WINDOW_HEIGHT - 420, 'top': WINDOW_HEIGHT - 540, 'width': 20},
			{'x': WINDOW_WIDTH - 150, 'bottom': WINDOW_HEIGHT - 540, 'top': WINDOW_HEIGHT - 660, 'width': 20},
			{'x': 400, 'bottom': WINDOW_HEIGHT - 660, 'top': WINDOW_HEIGHT - 780, 'width': 20},
		]

		# Donkey Kong - positioned at top
		self.dk_x = WINDOW_WIDTH - 150
		self.dk_y = WINDOW_HEIGHT - 830
		self.dk_throw_timer = 0
		self.dk_animation_frame = 0

		# Barrels
		self.barrels = []
		self.barrel_spawn_timer = 0

		# Princess (Pauline) - positioned at top left
		self.princess_x = 250
		self.princess_y = WINDOW_HEIGHT - 830

		# Game state
		self.game_won = False
		self.game_over = False

		# Animation timers
		self.animation_timer = 0

	def spawn_barrel(self):
		barrel = {
			'x': self.dk_x,
			'y': self.dk_y + 50,
			'dx': -2 - random.uniform(0, 1),
			'dy': 0,
			'platform_level': len(self.platforms) - 1,  # Start at top platform
			'bouncing': False
		}
		self.barrels.append(barrel)

	def update_barrels(self):
		for barrel in self.barrels[:]:  # Copy list to avoid modification during iteration
			# Update position
			barrel['x'] += barrel['dx']
			barrel['y'] += barrel['dy']

			# Gravity
			if barrel['bouncing']:
				barrel['dy'] += 0.3

			# Check platform collisions
			on_platform = False
			for i, platform in enumerate(self.platforms):
				if (barrel['y'] >= platform['y'] - 15 and barrel['y'] <= platform['y'] + 5 and
					barrel['x'] >= platform['x_start'] - 20 and barrel['x'] <= platform['x_end'] + 20):

					barrel['y'] = platform['y'] - 15
					barrel['dy'] = 0
					barrel['bouncing'] = False
					barrel['platform_level'] = i
					on_platform = True
					break

			if not on_platform and not barrel['bouncing']:
				barrel['bouncing'] = True
				barrel['dy'] = 1

			# Check for ladder transitions (barrels occasionally fall down ladders)
			if random.random() < 0.02:  # 2% chance per frame
				for ladder in self.ladders:
					if abs(barrel['x'] - ladder['x']) < 30:
						if barrel['platform_level'] > 0:  # Not on bottom platform
							barrel['bouncing'] = True
							barrel['dy'] = 2

			# Remove barrels that go off screen
			if barrel['x'] < -50 or barrel['x'] > WINDOW_WIDTH + 50 or barrel['y'] > WINDOW_HEIGHT:
				self.barrels.remove(barrel)

	def check_mario_platform_collision(self):
		mario_bottom = self.mario_y + self.mario_height
		mario_center_x = self.mario_x + self.mario_width // 2

		# Check if Mario is on a platform
		self.mario_on_ground = False
		for i, platform in enumerate(self.platforms):
			platform_y = platform['y']

			# Handle sloped platforms
			if platform['slope'] != 0:
				slope_offset = (mario_center_x - platform['x_start']) * platform['slope'] / 100
				platform_y += slope_offset

			if (mario_bottom >= platform_y - 8 and mario_bottom <= platform_y + 12 and
				self.mario_x + self.mario_width > platform['x_start'] and
				self.mario_x < platform['x_end']):

				if self.mario_dy >= 0:  # Only if falling or standing
					self.mario_y = platform_y - self.mario_height
					self.mario_dy = 0
					self.mario_on_ground = True
				break

	def check_mario_ladder_collision(self):
		mario_center_x = self.mario_x + self.mario_width // 2
		mario_bottom = self.mario_y + self.mario_height
		mario_top = self.mario_y

		self.mario_on_ladder = False
		for ladder in self.ladders:
			# Check if Mario is horizontally aligned with ladder
			if abs(mario_center_x - ladder['x']) < ladder['width']:
				# Check if Mario is vertically within ladder bounds
				if mario_bottom >= ladder['top'] - 10 and mario_top <= ladder['bottom'] + 10:
					self.mario_on_ladder = True
					break

	def check_barrel_collision(self):
		mario_rect = pygame.Rect(self.mario_x, self.mario_y, self.mario_width, self.mario_height)

		for barrel in self.barrels:
			barrel_rect = pygame.Rect(barrel['x'] - 10, barrel['y'] - 10, 20, 20)
			if mario_rect.colliderect(barrel_rect):
				# Mario hit by barrel
				self.lives -= 1
				if self.lives <= 0:
					self.game_over = True
				else:
					# Reset Mario position
					self.mario_x = 50
					self.mario_y = WINDOW_HEIGHT - 180
					self.mario_dy = 0
					self.barrels.clear()  # Clear barrels on hit
				return

	def check_win_condition(self):
		# Check if Mario reached the princess
		if (abs(self.mario_x - self.princess_x) < 40 and
			abs(self.mario_y - self.princess_y) < 40):
			self.game_won = True
			self.score += 1000

	def draw_background(self):
		"""Draw construction site background"""
		# Dark blue night sky
		self.screen.fill((25, 25, 112))  # Midnight blue

		# Draw some construction elements
		# Vertical support beams
		for x in [100, 300, 500, 700]:
			pygame.draw.rect(self.screen, (70, 70, 70), (x, 0, 8, WINDOW_HEIGHT))
			# Rivets on beams
			for y in range(50, WINDOW_HEIGHT - 100, 40):
				pygame.draw.circle(self.screen, (90, 90, 90), (x + 4, y), 3)

	def draw_platforms(self):
		"""Draw authentic girder platforms"""
		for i, platform in enumerate(self.platforms):
			y = platform['y']
			start_x = platform['x_start']
			end_x = platform['x_end']

			# Main girder body
			girder_height = 12
			pygame.draw.rect(self.screen, (255, 140, 0),
						   (start_x, y - girder_height//2, end_x - start_x, girder_height))

			# Top edge highlight
			pygame.draw.line(self.screen, (255, 180, 40),
						   (start_x, y - girder_height//2),
						   (end_x, y - girder_height//2), 2)

			# Bottom shadow
			pygame.draw.line(self.screen, (200, 100, 0),
						   (start_x, y + girder_height//2),
						   (end_x, y + girder_height//2), 2)

			# Rivets along the girder
			for x in range(start_x + 20, end_x - 20, 40):
				pygame.draw.circle(self.screen, (180, 90, 0), (x, y), 4)
				pygame.draw.circle(self.screen, (255, 160, 20), (x, y), 2)

	def draw_ladders(self):
		"""Draw industrial ladders"""
		for ladder in self.ladders:
			x = ladder['x']
			top = ladder['top']
			bottom = ladder['bottom']
			width = ladder['width']

			# Side rails
			pygame.draw.rect(self.screen, (255, 255, 0), (x - width//2, top, 4, bottom - top))
			pygame.draw.rect(self.screen, (255, 255, 0), (x + width//2 - 4, top, 4, bottom - top))

			# Rungs
			rung_spacing = 16
			for y in range(int(top) + 8, int(bottom), rung_spacing):
				pygame.draw.rect(self.screen, (255, 255, 0),
							   (x - width//2, y, width, 4))
				# Rung highlight
				pygame.draw.line(self.screen, (255, 255, 150),
							   (x - width//2, y), (x + width//2, y), 1)

	def draw_donkey_kong(self):
		"""Draw authentic Donkey Kong sprite"""
		self.animation_timer += 1
		dk_x, dk_y = self.dk_x, self.dk_y

		# Body (brown gorilla body)
		body_width, body_height = 80, 60
		pygame.draw.ellipse(self.screen, (139, 69, 19),
						  (dk_x - body_width//2, dk_y, body_width, body_height))

		# Chest (lighter brown)
		pygame.draw.ellipse(self.screen, (160, 82, 45),
						  (dk_x - 25, dk_y + 15, 50, 35))

		# Head
		head_radius = 35
		pygame.draw.circle(self.screen, (139, 69, 19), (dk_x, dk_y - 10), head_radius)

		# Face (lighter)
		pygame.draw.ellipse(self.screen, (160, 82, 45),
						  (dk_x - 25, dk_y - 25, 50, 40))

		# Eyes
		eye_y = dk_y - 15
		pygame.draw.circle(self.screen, WHITE, (dk_x - 12, eye_y), 8)
		pygame.draw.circle(self.screen, WHITE, (dk_x + 12, eye_y), 8)
		pygame.draw.circle(self.screen, BLACK, (dk_x - 12, eye_y), 5)
		pygame.draw.circle(self.screen, BLACK, (dk_x + 12, eye_y), 5)

		# Angry eyebrows
		pygame.draw.polygon(self.screen, BLACK, [
			(dk_x - 20, dk_y - 25), (dk_x - 5, dk_y - 30), (dk_x - 5, dk_y - 25)
		])
		pygame.draw.polygon(self.screen, BLACK, [
			(dk_x + 5, dk_y - 30), (dk_x + 20, dk_y - 25), (dk_x + 5, dk_y - 25)
		])

		# Nose
		pygame.draw.ellipse(self.screen, BLACK, (dk_x - 3, dk_y - 5, 6, 8))

		# Mouth (angry expression)
		pygame.draw.arc(self.screen, BLACK, (dk_x - 15, dk_y - 5, 30, 20),
					   0, math.pi, 3)

		# Arms
		arm_animation = int(self.animation_timer / 10) % 2
		arm_offset = 5 if arm_animation else 0

		# Left arm
		pygame.draw.ellipse(self.screen, (139, 69, 19),
						  (dk_x - 60, dk_y + 10 - arm_offset, 30, 50))
		# Right arm
		pygame.draw.ellipse(self.screen, (139, 69, 19),
						  (dk_x + 30, dk_y + 10 + arm_offset, 30, 50))

		# Fists
		pygame.draw.circle(self.screen, (139, 69, 19), (dk_x - 50, dk_y + 40 - arm_offset), 12)
		pygame.draw.circle(self.screen, (139, 69, 19), (dk_x + 50, dk_y + 40 + arm_offset), 12)

	def draw_princess(self):
		"""Draw Princess Pauline"""
		px, py = self.princess_x, self.princess_y

		# Dress (pink)
		dress_width = 20
		dress_height = 35
		pygame.draw.rect(self.screen, (255, 182, 193),
						(px, py + 10, dress_width, dress_height))

		# Dress details
		pygame.draw.rect(self.screen, (255, 105, 180),
						(px + 2, py + 15, dress_width - 4, 5))

		# Head
		pygame.draw.circle(self.screen, (255, 220, 177), (px + 10, py), 12)

		# Hair (blonde)
		pygame.draw.circle(self.screen, (255, 215, 0), (px + 10, py - 3), 15)
		pygame.draw.circle(self.screen, (255, 220, 177), (px + 10, py), 10)

		# Eyes
		pygame.draw.circle(self.screen, BLACK, (px + 7, py - 2), 2)
		pygame.draw.circle(self.screen, BLACK, (px + 13, py - 2), 2)

		# Mouth
		pygame.draw.circle(self.screen, RED, (px + 10, py + 3), 2)

		# Arms
		pygame.draw.rect(self.screen, (255, 220, 177), (px - 3, py + 12, 6, 15))
		pygame.draw.rect(self.screen, (255, 220, 177), (px + 17, py + 12, 6, 15))

		# Help gesture (arms up)
		if self.animation_timer % 60 < 30:
			pygame.draw.line(self.screen, (255, 220, 177), (px + 3, py + 8), (px - 5, py - 5), 4)
			pygame.draw.line(self.screen, (255, 220, 177), (px + 17, py + 8), (px + 25, py - 5), 4)

	def draw_mario(self):
		"""Draw authentic Mario sprite"""
		mx, my = self.mario_x, self.mario_y

		# Animation frame for walking
		if abs(self.mario_dy) < 0.1 and (pygame.key.get_pressed()[pygame.K_LEFT] or
										pygame.key.get_pressed()[pygame.K_RIGHT] or
										pygame.key.get_pressed()[pygame.K_a] or
										pygame.key.get_pressed()[pygame.K_d]):
			self.mario_animation_frame += 1

		walk_frame = (self.mario_animation_frame // 8) % 2

		# Body (red overalls)
		body_color = (255, 0, 0)  # Red overalls
		pygame.draw.rect(self.screen, body_color, (mx + 2, my + 12, 20, 15))

		# Legs (blue pants)
		leg_color = (0, 0, 255)
		leg_width = 8
		leg_spacing = walk_frame * 2 if not self.mario_on_ground else 0

		# Left leg
		pygame.draw.rect(self.screen, leg_color,
						(mx + 4 - leg_spacing, my + 22, leg_width, 10))
		# Right leg
		pygame.draw.rect(self.screen, leg_color,
						(mx + 12 + leg_spacing, my + 22, leg_width, 10))

		# Shoes (brown)
		shoe_color = (139, 69, 19)
		pygame.draw.rect(self.screen, shoe_color, (mx + 2, my + 28, 10, 4))
		pygame.draw.rect(self.screen, shoe_color, (mx + 14, my + 28, 10, 4))

		# Head (skin color)
		skin_color = (255, 220, 177)
		pygame.draw.circle(self.screen, skin_color, (mx + 12, my + 8), 10)

		# Hat (red)
		hat_points = [(mx + 2, my + 2), (mx + 22, my + 2), (mx + 20, my + 8), (mx + 4, my + 8)]
		pygame.draw.polygon(self.screen, (255, 0, 0), hat_points)

		# Hat emblem (M)
		pygame.draw.rect(self.screen, WHITE, (mx + 10, my + 3, 4, 3))

		# Mustache
		mustache_color = (139, 69, 19)
		pygame.draw.ellipse(self.screen, mustache_color, (mx + 8, my + 10, 8, 3))

		# Eyes
		if self.mario_facing_right:
			pygame.draw.circle(self.screen, BLACK, (mx + 9, my + 7), 1)
			pygame.draw.circle(self.screen, BLACK, (mx + 13, my + 7), 1)
		else:
			pygame.draw.circle(self.screen, BLACK, (mx + 11, my + 7), 1)
			pygame.draw.circle(self.screen, BLACK, (mx + 15, my + 7), 1)

		# Nose
		pygame.draw.circle(self.screen, (255, 200, 177), (mx + 12, my + 9), 2)

		# Arms
		arm_color = skin_color
		if self.mario_climbing:
			# Climbing pose
			pygame.draw.rect(self.screen, arm_color, (mx - 2, my + 10, 6, 12))
			pygame.draw.rect(self.screen, arm_color, (mx + 20, my + 10, 6, 12))
		else:
			# Normal pose
			if self.mario_facing_right:
				pygame.draw.rect(self.screen, arm_color, (mx + 22, my + 12, 4, 10))
				pygame.draw.rect(self.screen, arm_color, (mx - 2, my + 14, 4, 8))
			else:
				pygame.draw.rect(self.screen, arm_color, (mx - 2, my + 12, 4, 10))
				pygame.draw.rect(self.screen, arm_color, (mx + 22, my + 14, 4, 8))

	def draw_barrels(self):
		"""Draw authentic rolling barrels"""
		for barrel in self.barrels:
			bx, by = int(barrel['x']), int(barrel['y'])

			# Barrel body (brown)
			barrel_color = (139, 69, 19)
			pygame.draw.ellipse(self.screen, barrel_color, (bx - 12, by - 10, 24, 20))

			# Barrel hoops (metal bands)
			hoop_color = (105, 105, 105)
			pygame.draw.ellipse(self.screen, hoop_color, (bx - 12, by - 8, 24, 3))
			pygame.draw.ellipse(self.screen, hoop_color, (bx - 12, by + 2, 24, 3))

			# Barrel highlight
			pygame.draw.ellipse(self.screen, (160, 82, 45), (bx - 8, by - 6, 16, 12))

			# Rotation effect
			rotation_frame = int(barrel['x'] / 5) % 4
			for i in range(rotation_frame):
				angle = i * math.pi / 2
				line_x = bx + 8 * math.cos(angle)
				line_y = by + 4 * math.sin(angle)
				pygame.draw.line(self.screen, (100, 50, 0),
							   (bx, by), (line_x, line_y), 2)

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"
					elif event.key == pygame.K_SPACE and self.mario_on_ground:
						self.mario_dy = -12  # Jump
					elif event.key == pygame.K_r and (self.game_over or self.game_won):
						# Restart game
						self.mario_x = 50
						self.mario_y = WINDOW_HEIGHT - 180
						self.mario_dy = 0
						self.mario_on_ground = False
						self.score = 0
						self.lives = 3
						self.level = 1
						self.barrels.clear()
						self.game_won = False
						self.game_over = False

			if not self.game_over and not self.game_won:
				keys = pygame.key.get_pressed()

				# Mario movement
				if keys[pygame.K_LEFT] or keys[pygame.K_a]:
					self.mario_x -= 3
					self.mario_facing_right = False
					if self.mario_x < 0:
						self.mario_x = 0

				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					self.mario_x += 3
					self.mario_facing_right = True
					if self.mario_x > WINDOW_WIDTH - self.mario_width:
						self.mario_x = WINDOW_WIDTH - self.mario_width

				# Ladder climbing - FIXED
				self.mario_climbing = False
				if self.mario_on_ladder:
					if keys[pygame.K_UP] or keys[pygame.K_w]:
						self.mario_y -= 2
						self.mario_dy = 0
						self.mario_climbing = True
					elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
						self.mario_y += 2
						self.mario_dy = 0
						self.mario_climbing = True

				# Gravity (only when not on ladder or ground)
				if not self.mario_on_ground and not self.mario_climbing:
					self.mario_dy += 0.4

				self.mario_y += self.mario_dy

				# Update game objects
				self.check_mario_platform_collision()
				self.check_mario_ladder_collision()

				# Spawn barrels
				self.barrel_spawn_timer += 1
				if self.barrel_spawn_timer > 80:  # Spawn every ~1.3 seconds at 60fps
					self.spawn_barrel()
					self.barrel_spawn_timer = 0

				self.update_barrels()
				self.check_barrel_collision()
				self.check_win_condition()

				# Update Donkey Kong
				self.dk_throw_timer += 1

				# Update score
				self.score += 1

			# Draw everything
			self.screen.fill(BLACK)

			# Draw construction site background
			self.draw_background()

			# Draw platforms (girders)
			self.draw_platforms()

			# Draw ladders
			self.draw_ladders()

			# Draw Donkey Kong
			self.draw_donkey_kong()

			# Draw Princess (Pauline)
			self.draw_princess()

			# Draw Mario
			if not self.game_over:
				self.draw_mario()

			# Draw barrels
			self.draw_barrels()

			# Draw UI
			score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
			self.screen.blit(score_text, (10, 10))

			lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
			self.screen.blit(lives_text, (200, 10))

			level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
			self.screen.blit(level_text, (350, 10))

			# Game title
			title_text = self.font_large.render("DONKEY KONG", True, RED)
			title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
			self.screen.blit(title_text, title_rect)

			if self.game_over:
				game_over_text = self.font_large.render("GAME OVER!", True, RED)
				game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
				self.screen.blit(game_over_text, game_over_rect)

				restart_text = self.font.render("Press R to restart, ESC for menu", True, WHITE)
				restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
				self.screen.blit(restart_text, restart_rect)

			elif self.game_won:
				win_text = self.font_large.render("YOU SAVED THE PRINCESS!", True, GREEN)
				win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
				self.screen.blit(win_text, win_rect)

				restart_text = self.font.render("Press R to play again, ESC for menu", True, WHITE)
				restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
				self.screen.blit(restart_text, restart_rect)

			else:
				# Instructions
				inst_text = self.font.render("Arrow keys: Move | SPACE: Jump | Climb ladders to save the princess!", True, WHITE)
				self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 60))

				back_text = self.font.render("Press ESC to return to menu", True, WHITE)
				self.screen.blit(back_text, (10, WINDOW_HEIGHT - 30))

			pygame.display.flip()
			clock.tick(60)

		return "menu"

class FroggerGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 48)
		self.running = True
		self.frog_x = WINDOW_WIDTH // 2
		self.frog_y = WINDOW_HEIGHT - 100
		self.cars = []
		for i in range(4):
			self.cars.append({
				'x': random.randint(0, WINDOW_WIDTH),
				'y': 200 + i * 80,
				'speed': random.choice([-3, -2, 2, 3]),
				'width': 60,
				'height': 30
			})

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"
					elif event.key == pygame.K_UP:
						self.frog_y = max(100, self.frog_y - 40)
					elif event.key == pygame.K_DOWN:
						self.frog_y = min(WINDOW_HEIGHT - 100, self.frog_y + 40)
					elif event.key == pygame.K_LEFT:
						self.frog_x = max(20, self.frog_x - 40)
					elif event.key == pygame.K_RIGHT:
						self.frog_x = min(WINDOW_WIDTH - 20, self.frog_x + 40)

			# Update cars
			for car in self.cars:
				car['x'] += car['speed']
				if car['x'] > WINDOW_WIDTH:
					car['x'] = -car['width']
				elif car['x'] < -car['width']:
					car['x'] = WINDOW_WIDTH

			# Check collision
			frog_rect = pygame.Rect(self.frog_x - 15, self.frog_y - 15, 30, 30)
			for car in self.cars:
				car_rect = pygame.Rect(car['x'], car['y'], car['width'], car['height'])
				if frog_rect.colliderect(car_rect):
					# Reset frog position
					self.frog_x = WINDOW_WIDTH // 2
					self.frog_y = WINDOW_HEIGHT - 100

			self.screen.fill(BLACK)

			# Draw road
			for i in range(4):
				road_color = GRAY if i % 2 == 0 else (64, 64, 64)
				pygame.draw.rect(self.screen, road_color, (0, 200 + i * 80, WINDOW_WIDTH, 80))

			# Draw cars
			for car in self.cars:
				pygame.draw.rect(self.screen, RED, (car['x'], car['y'], car['width'], car['height']))
				pygame.draw.rect(self.screen, WHITE, (car['x'], car['y'], car['width'], car['height']), 2)

			# Draw frog
			pygame.draw.circle(self.screen, GREEN, (self.frog_x, self.frog_y), 15)
			pygame.draw.circle(self.screen, WHITE, (self.frog_x - 5, self.frog_y - 5), 3)
			pygame.draw.circle(self.screen, WHITE, (self.frog_x + 5, self.frog_y - 5), 3)

			# Title and instructions
			title_text = self.font.render("FROGGER", True, GREEN)
			title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
			self.screen.blit(title_text, title_rect)

			inst_text = self.font.render("Cross the road safely!", True, WHITE)
			self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 80))

			back_text = self.font.render("Press ESC to return to menu", True, WHITE)
			self.screen.blit(back_text, (10, WINDOW_HEIGHT - 40))

			pygame.display.flip()
			clock.tick(60)

		return "menu"

class BreakoutGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 48)
		self.running = True
		self.paddle_x = WINDOW_WIDTH // 2 - 50
		self.paddle_y = WINDOW_HEIGHT - 100
		self.paddle_width = 100
		self.ball_x = WINDOW_WIDTH // 2
		self.ball_y = WINDOW_HEIGHT // 2
		self.ball_dx = 3
		self.ball_dy = -3
		self.bricks = []

		# Create bricks
		for row in range(6):
			for col in range(10):
				brick = {
					'x': col * 80 + 5,
					'y': row * 30 + 100,
					'width': 75,
					'height': 25,
					'active': True,
					'color': [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE][row]
				}
				self.bricks.append(brick)

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"

			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT]:
				self.paddle_x = max(0, self.paddle_x - 5)
			if keys[pygame.K_RIGHT]:
				self.paddle_x = min(WINDOW_WIDTH - self.paddle_width, self.paddle_x + 5)

			# Update ball
			self.ball_x += self.ball_dx
			self.ball_y += self.ball_dy

			# Ball collision with walls
			if self.ball_x <= 10 or self.ball_x >= WINDOW_WIDTH - 10:
				self.ball_dx = -self.ball_dx
			if self.ball_y <= 10:
				self.ball_dy = -self.ball_dy

			# Ball collision with paddle
			if (self.ball_y + 10 >= self.paddle_y and
				self.ball_x >= self.paddle_x and
				self.ball_x <= self.paddle_x + self.paddle_width):
				self.ball_dy = -abs(self.ball_dy)

			# Ball collision with bricks
			ball_rect = pygame.Rect(self.ball_x - 10, self.ball_y - 10, 20, 20)
			for brick in self.bricks:
				if brick['active']:
					brick_rect = pygame.Rect(brick['x'], brick['y'], brick['width'], brick['height'])
					if ball_rect.colliderect(brick_rect):
						brick['active'] = False
						self.ball_dy = -self.ball_dy
						break

			# Reset if ball goes off screen
			if self.ball_y > WINDOW_HEIGHT:
				self.ball_x = WINDOW_WIDTH // 2
				self.ball_y = WINDOW_HEIGHT // 2
				self.ball_dx = 3
				self.ball_dy = -3

			self.screen.fill(BLACK)

			# Draw bricks
			for brick in self.bricks:
				if brick['active']:
					pygame.draw.rect(self.screen, brick['color'],
								   (brick['x'], brick['y'], brick['width'], brick['height']))
					pygame.draw.rect(self.screen, WHITE,
								   (brick['x'], brick['y'], brick['width'], brick['height']), 1)

			# Draw paddle
			pygame.draw.rect(self.screen, WHITE,
						   (self.paddle_x, self.paddle_y, self.paddle_width, 10))

			# Draw ball
			pygame.draw.circle(self.screen, WHITE, (int(self.ball_x), int(self.ball_y)), 10)

			# Title and instructions
			title_text = self.font.render("BREAKOUT", True, WHITE)
			title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
			self.screen.blit(title_text, title_rect)

			inst_text = self.font.render("Left/Right arrows to move paddle", True, WHITE)
			self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 80))

			back_text = self.font.render("Press ESC to return to menu", True, WHITE)
			self.screen.blit(back_text, (10, WINDOW_HEIGHT - 40))

			pygame.display.flip()
			clock.tick(60)

		return "menu"

class RetroArcade:
	def __init__(self):
		self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption("RETRO ARCADE MACHINE")
		self.clock = pygame.time.Clock()
		self.menu = ArcadeMenu(self.screen)
		self.current_state = "menu"

		# Game classes
		self.games = {
			0: PacManGame,
			1: DonkeyKongGame,
			2: SnakeGame,
			3: TetrisGame,
			4: FroggerGame,
			5: BreakoutGame
		}

	def run(self):
		running = True

		while running:
			if self.current_state == "menu":
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_ESCAPE:
							running = False
						else:
							selected = self.menu.handle_input(event)
							if selected is not None:
								# Launch selected game
								game_class = self.games[selected]
								game = game_class(self.screen)
								result = game.run()
								if result == "quit":
									running = False
								# If result is "menu", we stay in menu state

				self.menu.update()
				self.menu.draw()

			pygame.display.flip()
			self.clock.tick(60)

		pygame.quit()
		sys.exit()

if __name__ == "__main__":
	arcade = RetroArcade()
	arcade.run()