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
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850

class GalagaGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.font_large = pygame.font.Font(None, 48)
		self.running = True

		# Player
		self.player_x = WINDOW_WIDTH // 2
		self.player_y = WINDOW_HEIGHT - 100
		self.player_width = 32
		self.player_height = 24
		self.player_speed = 4

		# Bullets
		self.bullets = []
		self.bullet_speed = 10

		# Enemies
		self.enemies = []
		self.enemy_bullets = []
		self.formation_enemies = []
		self.diving_enemies = []

		# Game state
		self.score = 0
		self.lives = 3
		self.game_over = False
		self.stage = 1
		self.enemies_spawned = 0
		self.spawn_timer = 0

		# Animation and effects
		self.animation_frame = 0
		self.stars = self.create_starfield()

		# Wave management
		self.wave_complete = False
		self.next_wave_timer = 0

	def create_starfield(self):
		"""Create animated starfield"""
		stars = []
		for _ in range(80):
			star = {
				'x': random.randint(0, WINDOW_WIDTH),
				'y': random.randint(0, WINDOW_HEIGHT - 120),
				'speed': random.uniform(0.5, 2.0),
				'brightness': random.randint(100, 255)
			}
			stars.append(star)
		return stars

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "quit"
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return "menu"
					elif event.key == pygame.K_SPACE and not self.game_over:
						self.shoot()
					elif event.key == pygame.K_r and self.game_over:
						self.restart_game()

			if not self.game_over:
				# Handle continuous input
				keys = pygame.key.get_pressed()
				if keys[pygame.K_LEFT] or keys[pygame.K_a]:
					self.player_x = max(20, self.player_x - self.player_speed)
				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					self.player_x = min(WINDOW_WIDTH - self.player_width - 20, self.player_x + self.player_speed)

				self.update_game()

			self.draw_everything()
			pygame.display.flip()
			clock.tick(60)

		return "menu"

	def shoot(self):
		"""Player shoots a bullet"""
		if len(self.bullets) < 2:  # Limit to 2 bullets like original Galaga
			bullet = {
				'x': self.player_x + self.player_width // 2 - 2,
				'y': self.player_y,
				'width': 4,
				'height': 12,
				'active': True
			}
			self.bullets.append(bullet)

	def spawn_enemy_wave(self):
		"""Spawn enemies in classic Galaga formation"""
		if self.enemies_spawned >= 40:  # Full wave spawned
			return

		self.spawn_timer += 1
		if self.spawn_timer > 30:  # Spawn every 0.5 seconds
			self.spawn_timer = 0

			# Different enemy types
			enemy_types = ['bee', 'butterfly', 'boss']
			enemy_type = 'bee'

			if self.enemies_spawned < 16:
				enemy_type = 'bee'
			elif self.enemies_spawned < 32:
				enemy_type = 'butterfly'
			else:
				enemy_type = 'boss'

			# Entry pattern - enemies fly in from sides
			entry_side = random.choice(['left', 'right'])
			if entry_side == 'left':
				start_x = -50
				curve_direction = 1
			else:
				start_x = WINDOW_WIDTH + 50
				curve_direction = -1

			enemy = {
				'x': start_x,
				'y': 100,
				'type': enemy_type,
				'state': 'entering',  # entering, formation, diving
				'speed': 3,
				'curve_direction': curve_direction,
				'target_x': 100 + (self.enemies_spawned % 8) * 80,
				'target_y': 150 + (self.enemies_spawned // 8) * 60,
				'dive_timer': 0,
				'health': 2 if enemy_type == 'boss' else 1,
				'points': {'bee': 50, 'butterfly': 80, 'boss': 150}[enemy_type]
			}

			self.enemies.append(enemy)
			self.enemies_spawned += 1

	def update_game(self):
		"""Update all game elements"""
		self.animation_frame += 1

		# Update starfield
		for star in self.stars:
			star['y'] += star['speed']
			if star['y'] > WINDOW_HEIGHT - 120:
				star['y'] = 0
				star['x'] = random.randint(0, WINDOW_WIDTH)

		# Spawn enemies
		self.spawn_enemy_wave()

		# Update player bullets
		for bullet in self.bullets[:]:
			if bullet['active']:
				bullet['y'] -= self.bullet_speed
				if bullet['y'] < 0:
					bullet['active'] = False
					self.bullets.remove(bullet)

		# Update enemies
		self.update_enemies()

		# Check bullet-enemy collisions
		self.check_collisions()

		# Enemy shooting
		if random.random() < 0.02:  # 2% chance per frame
			self.enemy_shoot()

		# Update enemy bullets
		for bullet in self.enemy_bullets[:]:
			bullet['y'] += 4
			if bullet['y'] > WINDOW_HEIGHT:
				self.enemy_bullets.remove(bullet)

		# Check enemy bullet hits player
		self.check_player_hit()

		# Check wave complete
		formation_enemies = [e for e in self.enemies if e['state'] == 'formation']
		if len(formation_enemies) == 0 and self.enemies_spawned >= 40:
			if not self.wave_complete:
				self.wave_complete = True
				self.next_wave_timer = 180  # 3 seconds

		# Start next wave
		if self.wave_complete:
			self.next_wave_timer -= 1
			if self.next_wave_timer <= 0:
				self.start_next_wave()

	def update_enemies(self):
		"""Update enemy positions and behaviors"""
		for enemy in self.enemies[:]:
			if enemy['state'] == 'entering':
				# Flying in curved pattern to formation
				progress = min(1.0, (self.animation_frame % 120) / 120.0)

				# Curved entry path
				if enemy['curve_direction'] == 1:  # From left
					enemy['x'] += enemy['speed']
					enemy['y'] += math.sin(progress * math.pi) * 2
				else:  # From right
					enemy['x'] -= enemy['speed']
					enemy['y'] += math.sin(progress * math.pi) * 2

				# Check if reached formation position
				if abs(enemy['x'] - enemy['target_x']) < 20:
					enemy['state'] = 'formation'
					enemy['x'] = enemy['target_x']
					enemy['y'] = enemy['target_y']

			elif enemy['state'] == 'formation':
				# Bob up and down in formation
				enemy['y'] = enemy['target_y'] + math.sin(self.animation_frame * 0.05 + enemy['target_x'] * 0.01) * 5

				# Randomly decide to dive
				if random.random() < 0.001:  # Very low chance
					enemy['state'] = 'diving'
					enemy['dive_timer'] = 0

			elif enemy['state'] == 'diving':
				# Dive attack pattern
				enemy['dive_timer'] += 1

				# Curve towards player
				player_center = self.player_x + self.player_width // 2
				if enemy['x'] < player_center:
					enemy['x'] += 2
				elif enemy['x'] > player_center:
					enemy['x'] -= 2

				enemy['y'] += 4

				# If went off screen, remove or return to formation
				if enemy['y'] > WINDOW_HEIGHT:
					if random.random() < 0.7:  # 70% chance to return
						enemy['state'] = 'entering'
						enemy['x'] = random.choice([-50, WINDOW_WIDTH + 50])
						enemy['y'] = 100
						enemy['curve_direction'] = 1 if enemy['x'] < 0 else -1
					else:
						self.enemies.remove(enemy)

	def check_collisions(self):
		"""Check bullet-enemy collisions"""
		for bullet in self.bullets[:]:
			if not bullet['active']:
				continue

			bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])

			for enemy in self.enemies[:]:
				enemy_rect = pygame.Rect(enemy['x'] - 16, enemy['y'] - 12, 32, 24)

				if bullet_rect.colliderect(enemy_rect):
					bullet['active'] = False
					self.bullets.remove(bullet)

					enemy['health'] -= 1
					if enemy['health'] <= 0:
						self.score += enemy['points']
						self.enemies.remove(enemy)
					break

	def enemy_shoot(self):
		"""Enemy shoots at player"""
		formation_enemies = [e for e in self.enemies if e['state'] == 'formation']
		diving_enemies = [e for e in self.enemies if e['state'] == 'diving']

		shooters = formation_enemies + diving_enemies
		if shooters:
			shooter = random.choice(shooters)
			bullet = {
				'x': shooter['x'],
				'y': shooter['y'] + 12,
				'width': 4,
				'height': 8
			}
			self.enemy_bullets.append(bullet)

	def check_player_hit(self):
		"""Check if player is hit by enemy bullets or enemies"""
		player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)

		# Check enemy bullets
		for bullet in self.enemy_bullets[:]:
			bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])
			if bullet_rect.colliderect(player_rect):
				self.enemy_bullets.remove(bullet)
				self.player_hit()

		# Check direct enemy collision
		for enemy in self.enemies:
			if enemy['state'] == 'diving':
				enemy_rect = pygame.Rect(enemy['x'] - 16, enemy['y'] - 12, 32, 24)
				if enemy_rect.colliderect(player_rect):
					self.player_hit()

	def player_hit(self):
		"""Handle player being hit"""
		self.lives -= 1
		if self.lives <= 0:
			self.game_over = True

	def start_next_wave(self):
		"""Start the next wave"""
		self.stage += 1
		self.enemies_spawned = 0
		self.wave_complete = False
		self.enemies.clear()
		self.enemy_bullets.clear()

	def draw_everything(self):
		"""Draw all game elements"""
		# Space background
		self.screen.fill(BLACK)

		# Draw stars
		for star in self.stars:
			alpha = int(star['brightness'] * (0.3 + 0.7 * abs(math.sin(self.animation_frame * 0.02 + star['x'] * 0.01))))
			alpha = max(0, min(255, alpha))  # Clamp between 0 and 255
			color = (alpha, alpha, alpha)
			pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), 1)

		# Draw player
		self.draw_player()

		# Draw enemies
		self.draw_enemies()

		# Draw bullets
		self.draw_bullets()

		# Draw UI
		self.draw_ui()

		if self.game_over:
			self.draw_game_over()

	def draw_player(self):
		"""Draw the player ship"""
		# Main body (triangular ship)
		ship_points = [
			(self.player_x + self.player_width // 2, self.player_y),
			(self.player_x + 4, self.player_y + self.player_height),
			(self.player_x + 8, self.player_y + self.player_height - 4),
			(self.player_x + self.player_width - 8, self.player_y + self.player_height - 4),
			(self.player_x + self.player_width - 4, self.player_y + self.player_height)
		]
		pygame.draw.polygon(self.screen, WHITE, ship_points)

		# Cockpit
		pygame.draw.circle(self.screen, CYAN, (self.player_x + self.player_width // 2, self.player_y + 8), 4)

		# Wings
		pygame.draw.polygon(self.screen, YELLOW, [
			(self.player_x, self.player_y + 12),
			(self.player_x + 8, self.player_y + 16),
			(self.player_x + 8, self.player_y + 20),
			(self.player_x, self.player_y + 18)
		])
		pygame.draw.polygon(self.screen, YELLOW, [
			(self.player_x + self.player_width, self.player_y + 12),
			(self.player_x + self.player_width - 8, self.player_y + 16),
			(self.player_x + self.player_width - 8, self.player_y + 20),
			(self.player_x + self.player_width, self.player_y + 18)
		])

	def draw_enemies(self):
		"""Draw all enemies"""
		for enemy in self.enemies:
			x, y = int(enemy['x']), int(enemy['y'])

			# Different colors and shapes for different enemy types
			if enemy['type'] == 'bee':
				color = YELLOW
				# Simple bee shape
				pygame.draw.ellipse(self.screen, color, (x - 12, y - 8, 24, 16))
				pygame.draw.circle(self.screen, BLACK, (x - 6, y - 3), 2)
				pygame.draw.circle(self.screen, BLACK, (x + 6, y - 3), 2)

			elif enemy['type'] == 'butterfly':
				color = RED
				# Butterfly shape with wings
				pygame.draw.ellipse(self.screen, color, (x - 10, y - 6, 20, 12))
				# Wings
				wing_frame = (self.animation_frame // 10) % 2
				wing_offset = 2 if wing_frame else 0
				pygame.draw.ellipse(self.screen, ORANGE, (x - 16, y - 4 - wing_offset, 8, 8))
				pygame.draw.ellipse(self.screen, ORANGE, (x + 8, y - 4 - wing_offset, 8, 8))

			elif enemy['type'] == 'boss':
				color = GREEN
				# Larger boss enemy
				pygame.draw.ellipse(self.screen, color, (x - 16, y - 10, 32, 20))
				pygame.draw.ellipse(self.screen, WHITE, (x - 12, y - 6, 24, 12))
				# Eyes
				pygame.draw.circle(self.screen, RED, (x - 6, y - 2), 3)
				pygame.draw.circle(self.screen, RED, (x + 6, y - 2), 3)

	def draw_bullets(self):
		"""Draw all bullets"""
		# Player bullets
		for bullet in self.bullets:
			if bullet['active']:
				pygame.draw.rect(self.screen, CYAN,
							   (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

		# Enemy bullets
		for bullet in self.enemy_bullets:
			pygame.draw.ellipse(self.screen, RED,
							  (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

	def draw_ui(self):
		"""Draw user interface"""
		# Score
		score_text = self.font.render(f"Score: {self.score}", True, WHITE)
		self.screen.blit(score_text, (20, 20))

		# Lives
		lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
		self.screen.blit(lives_text, (20, 60))

		# Stage
		stage_text = self.font.render(f"Stage: {self.stage}", True, WHITE)
		self.screen.blit(stage_text, (WINDOW_WIDTH - 150, 20))

		# Title
		title_text = self.font_large.render("G A L A G A", True, YELLOW)
		title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
		self.screen.blit(title_text, title_rect)

		# Controls
		controls_text = self.font.render("A/D or ←→: Move | SPACE: Shoot | ESC: Menu", True, GRAY)
		self.screen.blit(controls_text, (20, WINDOW_HEIGHT - 40))

		# Wave complete message
		if self.wave_complete:
			ready_text = self.font_large.render(f"STAGE {self.stage} READY", True, CYAN)
			ready_rect = ready_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
			self.screen.blit(ready_text, ready_rect)

	def draw_game_over(self):
		"""Draw game over screen"""
		# Semi-transparent overlay
		overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		overlay.set_alpha(180)
		overlay.fill(BLACK)
		self.screen.blit(overlay, (0, 0))

		# Game over text
		game_over_text = self.font_large.render("GAME OVER", True, RED)
		game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
		self.screen.blit(game_over_text, game_over_rect)

		# Final score
		score_text = self.font_large.render(f"Final Score: {self.score}", True, WHITE)
		score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
		self.screen.blit(score_text, score_rect)

		# Stage reached
		stage_text = self.font.render(f"Stage Reached: {self.stage}", True, WHITE)
		stage_rect = stage_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10))
		self.screen.blit(stage_text, stage_rect)

		# Restart instructions
		restart_text = self.font.render("Press R to restart | ESC for menu", True, YELLOW)
		restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
		self.screen.blit(restart_text, restart_rect)

	def restart_game(self):
		"""Restart the game"""
		self.player_x = WINDOW_WIDTH // 2
		self.bullets = []
		self.enemies = []
		self.enemy_bullets = []
		self.score = 0
		self.lives = 3
		self.game_over = False
		self.stage = 1
		self.enemies_spawned = 0
		self.spawn_timer = 0
		self.wave_complete = False
		self.next_wave_timer = 0