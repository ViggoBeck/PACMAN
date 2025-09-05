import pygame
import random
import math

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850

class DonkeyKongGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.font_large = pygame.font.Font(None, 48)
		self.running = True

		# Mario properties
		self.mario_x = 50
		self.mario_y = WINDOW_HEIGHT - 220  # Start higher up
		self.mario_dy = 0
		self.mario_on_ground = False
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

		# Platform levels (y positions) - Fixed spacing
		self.platforms = [
			{'y': WINDOW_HEIGHT - 200, 'x_start': 0, 'x_end': WINDOW_WIDTH, 'slope': 0},           # Bottom
			{'y': WINDOW_HEIGHT - 320, 'x_start': 100, 'x_end': WINDOW_WIDTH, 'slope': 2},        # Second (sloped)
			{'y': WINDOW_HEIGHT - 440, 'x_start': 0, 'x_end': WINDOW_WIDTH - 100, 'slope': -2},   # Third (reverse slope)
			{'y': WINDOW_HEIGHT - 560, 'x_start': 100, 'x_end': WINDOW_WIDTH, 'slope': 2},        # Fourth (sloped)
			{'y': WINDOW_HEIGHT - 680, 'x_start': 0, 'x_end': WINDOW_WIDTH - 100, 'slope': 0},    # Fifth
			{'y': WINDOW_HEIGHT - 800, 'x_start': 200, 'x_end': WINDOW_WIDTH - 200, 'slope': 0},  # Top platform
		]

		# Ladders (x position, bottom_y, top_y) - fixed positioning
		self.ladders = [
			{'x': 150, 'bottom': WINDOW_HEIGHT - 200, 'top': WINDOW_HEIGHT - 320, 'width': 25},
			{'x': WINDOW_WIDTH - 150, 'bottom': WINDOW_HEIGHT - 320, 'top': WINDOW_HEIGHT - 440, 'width': 25},
			{'x': 150, 'bottom': WINDOW_HEIGHT - 440, 'top': WINDOW_HEIGHT - 560, 'width': 25},
			{'x': WINDOW_WIDTH - 150, 'bottom': WINDOW_HEIGHT - 560, 'top': WINDOW_HEIGHT - 680, 'width': 25},
			{'x': 400, 'bottom': WINDOW_HEIGHT - 680, 'top': WINDOW_HEIGHT - 800, 'width': 25},
		]

		# Donkey Kong - positioned at top
		self.dk_x = WINDOW_WIDTH - 150
		self.dk_y = WINDOW_HEIGHT - 850
		self.dk_throw_timer = 0
		self.dk_animation_frame = 0

		# Barrels
		self.barrels = []
		self.barrel_spawn_timer = 0

		# Princess (Pauline) - positioned at top left
		self.princess_x = 250
		self.princess_y = WINDOW_HEIGHT - 850

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

			# More generous collision detection
			if (mario_bottom >= platform_y - 10 and mario_bottom <= platform_y + 15 and
				mario_center_x > platform['x_start'] and
				mario_center_x < platform['x_end']):

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
				if mario_bottom >= ladder['top'] - 15 and mario_top <= ladder['bottom'] + 15:
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
					self.mario_y = WINDOW_HEIGHT - 220
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
					elif event.key == pygame.K_SPACE and (self.mario_on_ground or self.mario_on_ladder):
						self.mario_dy = -10  # Jump
					elif event.key == pygame.K_r and (self.game_over or self.game_won):
						# Restart game
						self.mario_x = 50
						self.mario_y = WINDOW_HEIGHT - 220
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
					self.mario_x -= 2
					self.mario_facing_right = False
					if self.mario_x < 0:
						self.mario_x = 0

				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					self.mario_x += 2
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

				# Apply vertical movement
				if not self.mario_climbing:
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