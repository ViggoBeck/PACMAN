import pygame
import random
import math

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850

class SpaceInvadersGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.font_large = pygame.font.Font(None, 48)
		self.running = True

		# Player
		self.player_x = WINDOW_WIDTH // 2
		self.player_y = WINDOW_HEIGHT - 100
		self.player_width = 40
		self.player_height = 20
		self.player_speed = 5

		# Bullets
		self.bullets = []
		self.bullet_speed = 8

		# Aliens
		self.aliens = []
		self.alien_bullets = []
		self.alien_direction = 1
		self.alien_drop_speed = 20

		# Game state
		self.score = 0
		self.lives = 3
		self.game_over = False
		self.wave = 1

		# Animation
		self.animation_frame = 0

		# Create initial alien formation
		self.create_aliens()

	def create_aliens(self):
		"""Create a formation of aliens"""
		self.aliens = []
		rows = 5
		cols = 10
		alien_width = 30
		alien_height = 20

		start_x = 100
		start_y = 100

		for row in range(rows):
			for col in range(cols):
				alien = {
					'x': start_x + col * (alien_width + 10),
					'y': start_y + row * (alien_height + 10),
					'type': row,  # Different types for different rows
					'alive': True
				}
				self.aliens.append(alien)

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
		if len(self.bullets) < 3:  # Limit bullets
			bullet = {
				'x': self.player_x + self.player_width // 2 - 2,
				'y': self.player_y,
				'width': 4,
				'height': 10
			}
			self.bullets.append(bullet)

	def update_game(self):
		"""Update all game elements"""
		self.animation_frame += 1

		# Update player bullets
		for bullet in self.bullets[:]:
			bullet['y'] -= self.bullet_speed
			if bullet['y'] < 0:
				self.bullets.remove(bullet)

		# Check bullet-alien collisions
		for bullet in self.bullets[:]:
			bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])
			for alien in self.aliens:
				if alien['alive']:
					alien_rect = pygame.Rect(alien['x'], alien['y'], 30, 20)
					if bullet_rect.colliderect(alien_rect):
						alien['alive'] = False
						self.bullets.remove(bullet)
						self.score += (5 - alien['type']) * 10  # Higher rows worth more
						break

		# Move aliens
		self.move_aliens()

		# Alien shooting
		if random.random() < 0.01:  # 1% chance per frame
			self.alien_shoot()

		# Update alien bullets
		for bullet in self.alien_bullets[:]:
			bullet['y'] += 3
			if bullet['y'] > WINDOW_HEIGHT:
				self.alien_bullets.remove(bullet)

		# Check alien bullet hits player
		player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
		for bullet in self.alien_bullets[:]:
			bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['width'], bullet['height'])
			if bullet_rect.colliderect(player_rect):
				self.alien_bullets.remove(bullet)
				self.lives -= 1
				if self.lives <= 0:
					self.game_over = True

		# Check if all aliens destroyed
		if all(not alien['alive'] for alien in self.aliens):
			self.wave += 1
			self.create_aliens()

		# Check if aliens reached bottom
		for alien in self.aliens:
			if alien['alive'] and alien['y'] > WINDOW_HEIGHT - 200:
				self.game_over = True

	def move_aliens(self):
		"""Move the alien formation"""
		# Check if any alien hits the edge
		hit_edge = False
		for alien in self.aliens:
			if alien['alive']:
				if (alien['x'] <= 20 and self.alien_direction == -1) or \
				   (alien['x'] >= WINDOW_WIDTH - 50 and self.alien_direction == 1):
					hit_edge = True
					break

		if hit_edge:
			# Change direction and drop down
			self.alien_direction *= -1
			for alien in self.aliens:
				if alien['alive']:
					alien['y'] += self.alien_drop_speed
		else:
			# Move horizontally
			for alien in self.aliens:
				if alien['alive']:
					alien['x'] += self.alien_direction * 2

	def alien_shoot(self):
		"""Random alien shoots"""
		alive_aliens = [alien for alien in self.aliens if alien['alive']]
		if alive_aliens:
			shooter = random.choice(alive_aliens)
			bullet = {
				'x': shooter['x'] + 15,
				'y': shooter['y'] + 20,
				'width': 4,
				'height': 8
			}
			self.alien_bullets.append(bullet)

	def draw_everything(self):
		"""Draw all game elements"""
		# Space background
		self.screen.fill(BLACK)

		# Draw stars
		for i in range(50):
			x = (i * 97 + self.animation_frame) % WINDOW_WIDTH
			y = (i * 67) % (WINDOW_HEIGHT - 120)
			star_brightness = (self.animation_frame + i * 13) % 100
			if star_brightness > 95:
				pygame.draw.circle(self.screen, WHITE, (x, y), 1)

		# Draw player
		self.draw_player()

		# Draw aliens
		self.draw_aliens()

		# Draw bullets
		self.draw_bullets()

		# Draw UI
		self.draw_ui()

		if self.game_over:
			self.draw_game_over()

	def draw_player(self):
		"""Draw the player ship"""
		# Ship body
		ship_points = [
			(self.player_x + self.player_width // 2, self.player_y),
			(self.player_x, self.player_y + self.player_height),
			(self.player_x + 8, self.player_y + self.player_height - 5),
			(self.player_x + self.player_width - 8, self.player_y + self.player_height - 5),
			(self.player_x + self.player_width, self.player_y + self.player_height)
		]
		pygame.draw.polygon(self.screen, GREEN, ship_points)
		pygame.draw.polygon(self.screen, WHITE, ship_points, 2)

	def draw_aliens(self):
		"""Draw all aliens"""
		for alien in self.aliens:
			if alien['alive']:
				# Different colors for different alien types
				colors = [RED, ORANGE, YELLOW, GREEN, CYAN]
				color = colors[alien['type']]

				# Animate aliens
				frame = (self.animation_frame // 20) % 2

				if frame == 0:
					# Frame 1
					alien_rect = pygame.Rect(alien['x'], alien['y'], 30, 20)
					pygame.draw.rect(self.screen, color, alien_rect)
					pygame.draw.rect(self.screen, WHITE, alien_rect, 1)

					# Eyes
					pygame.draw.circle(self.screen, BLACK, (alien['x'] + 8, alien['y'] + 8), 2)
					pygame.draw.circle(self.screen, BLACK, (alien['x'] + 22, alien['y'] + 8), 2)
				else:
					# Frame 2 (slightly different)
					alien_rect = pygame.Rect(alien['x'] + 2, alien['y'], 26, 20)
					pygame.draw.rect(self.screen, color, alien_rect)
					pygame.draw.rect(self.screen, WHITE, alien_rect, 1)

					# Eyes
					pygame.draw.circle(self.screen, BLACK, (alien['x'] + 8, alien['y'] + 8), 3)
					pygame.draw.circle(self.screen, BLACK, (alien['x'] + 22, alien['y'] + 8), 3)

	def draw_bullets(self):
		"""Draw all bullets"""
		# Player bullets
		for bullet in self.bullets:
			pygame.draw.rect(self.screen, YELLOW,
						   (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

		# Alien bullets
		for bullet in self.alien_bullets:
			pygame.draw.rect(self.screen, RED,
						   (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

	def draw_ui(self):
		"""Draw user interface"""
		# Score
		score_text = self.font.render(f"Score: {self.score}", True, WHITE)
		self.screen.blit(score_text, (20, 20))

		# Lives
		lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
		self.screen.blit(lives_text, (20, 60))

		# Wave
		wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
		self.screen.blit(wave_text, (WINDOW_WIDTH - 150, 20))

		# Title
		title_text = self.font_large.render("SPACE INVADERS", True, CYAN)
		title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
		self.screen.blit(title_text, title_rect)

		# Controls
		controls_text = self.font.render("A/D or ←→: Move | SPACE: Shoot | ESC: Menu", True, GRAY)
		self.screen.blit(controls_text, (20, WINDOW_HEIGHT - 40))

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

		# Wave reached
		wave_text = self.font.render(f"Wave Reached: {self.wave}", True, WHITE)
		wave_rect = wave_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10))
		self.screen.blit(wave_text, wave_rect)

		# Restart instructions
		restart_text = self.font.render("Press R to restart | ESC for menu", True, CYAN)
		restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
		self.screen.blit(restart_text, restart_rect)

	def restart_game(self):
		"""Restart the game"""
		self.player_x = WINDOW_WIDTH // 2
		self.bullets = []
		self.alien_bullets = []
		self.score = 0
		self.lives = 3
		self.game_over = False
		self.wave = 1
		self.alien_direction = 1
		self.create_aliens()