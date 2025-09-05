import pygame
import random
import math

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 850

class SnakeGame:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.Font(None, 36)
		self.font_large = pygame.font.Font(None, 48)
		self.running = True
		self.snake = [(10, 10), (9, 10), (8, 10)]
		self.food = (15, 15)
		self.direction = (1, 0)
		self.score = 0
		self.cell_size = 24  # Slightly larger for better graphics
		self.last_move_time = 0
		self.food_animation = 0  # For animated food
		self.game_over = False
		self.high_score = 0

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
					elif event.key == pygame.K_r and self.game_over:
						# Restart game
						self.restart_game()
					elif not self.game_over:
						if event.key == pygame.K_UP and self.direction != (0, 1):
							self.direction = (0, -1)
						elif event.key == pygame.K_DOWN and self.direction != (0, -1):
							self.direction = (0, 1)
						elif event.key == pygame.K_LEFT and self.direction != (1, 0):
							self.direction = (-1, 0)
						elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
							self.direction = (1, 0)

			# Move snake every 120ms (slightly faster)
			if current_time - self.last_move_time > 120 and not self.game_over:
				self.last_move_time = current_time
				head = self.snake[0]
				new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

				# Check boundaries
				if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH // self.cell_size or
					new_head[1] < 0 or new_head[1] >= (WINDOW_HEIGHT - 120) // self.cell_size):
					self.game_over = True

				# Check self collision
				if new_head in self.snake:
					self.game_over = True

				if self.game_over:
					# Update high score
					if self.score > self.high_score:
						self.high_score = self.score
					continue

				self.snake.insert(0, new_head)

				# Check food collision
				if new_head == self.food:
					self.score += 10
					# Generate new food
					while True:
						new_food = (random.randint(0, WINDOW_WIDTH // self.cell_size - 1),
								   random.randint(0, (WINDOW_HEIGHT - 120) // self.cell_size - 1))
						if new_food not in self.snake:
							self.food = new_food
							break
				else:
					self.snake.pop()

			# Update animation
			self.food_animation += 1

			# Draw everything
			self.draw_background()
			self.draw_snake()
			self.draw_food()
			self.draw_ui()

			if self.game_over:
				self.draw_game_over()

			pygame.display.flip()
			clock.tick(60)

		return "menu"

	def restart_game(self):
		"""Restart the game to initial state"""
		self.snake = [(10, 10), (9, 10), (8, 10)]
		self.direction = (1, 0)
		self.score = 0
		self.food = (15, 15)
		self.game_over = False
		self.food_animation = 0

	def draw_background(self):
		"""Draw enhanced background with grid"""
		# Dark green gradient background
		for y in range(0, WINDOW_HEIGHT - 120, 2):
			color_intensity = int(10 + 5 * math.sin(y * 0.05))
			color = (0, 15 + color_intensity, 0)
			pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
			pygame.draw.line(self.screen, color, (0, y + 1), (WINDOW_WIDTH, y + 1))

		# Draw grid lines (subtle)
		grid_color = (0, 40, 0)
		for x in range(0, WINDOW_WIDTH, self.cell_size):
			pygame.draw.line(self.screen, grid_color, (x, 0), (x, WINDOW_HEIGHT - 120))
		for y in range(0, WINDOW_HEIGHT - 120, self.cell_size):
			pygame.draw.line(self.screen, grid_color, (0, y), (WINDOW_WIDTH, y))

	def draw_snake(self):
		"""Draw enhanced snake with gradient and borders"""
		for i, segment in enumerate(self.snake):
			x = segment[0] * self.cell_size
			y = segment[1] * self.cell_size

			if i == 0:  # Head
				# Snake head - brighter green with eyes
				head_color = (50, 255, 50)
				pygame.draw.rect(self.screen, head_color,
							   (x + 2, y + 2, self.cell_size - 4, self.cell_size - 4))
				pygame.draw.rect(self.screen, (0, 200, 0),
							   (x + 2, y + 2, self.cell_size - 4, self.cell_size - 4), 2)

				# Eyes based on direction
				eye_size = 4
				if self.direction == (1, 0):  # Right
					pygame.draw.circle(self.screen, WHITE, (x + self.cell_size - 8, y + 6), eye_size)
					pygame.draw.circle(self.screen, WHITE, (x + self.cell_size - 8, y + self.cell_size - 6), eye_size)
					pygame.draw.circle(self.screen, BLACK, (x + self.cell_size - 6, y + 6), 2)
					pygame.draw.circle(self.screen, BLACK, (x + self.cell_size - 6, y + self.cell_size - 6), 2)
				elif self.direction == (-1, 0):  # Left
					pygame.draw.circle(self.screen, WHITE, (x + 8, y + 6), eye_size)
					pygame.draw.circle(self.screen, WHITE, (x + 8, y + self.cell_size - 6), eye_size)
					pygame.draw.circle(self.screen, BLACK, (x + 6, y + 6), 2)
					pygame.draw.circle(self.screen, BLACK, (x + 6, y + self.cell_size - 6), 2)
				elif self.direction == (0, -1):  # Up
					pygame.draw.circle(self.screen, WHITE, (x + 6, y + 8), eye_size)
					pygame.draw.circle(self.screen, WHITE, (x + self.cell_size - 6, y + 8), eye_size)
					pygame.draw.circle(self.screen, BLACK, (x + 6, y + 6), 2)
					pygame.draw.circle(self.screen, BLACK, (x + self.cell_size - 6, y + 6), 2)
				else:  # Down
					pygame.draw.circle(self.screen, WHITE, (x + 6, y + self.cell_size - 8), eye_size)
					pygame.draw.circle(self.screen, WHITE, (x + self.cell_size - 6, y + self.cell_size - 8), eye_size)
					pygame.draw.circle(self.screen, BLACK, (x + 6, y + self.cell_size - 6), 2)
					pygame.draw.circle(self.screen, BLACK, (x + self.cell_size - 6, y + self.cell_size - 6), 2)
			else:
				# Body segments - gradient from bright to dark green
				intensity = max(100, 255 - (i * 10))
				body_color = (0, intensity, 0)
				pygame.draw.rect(self.screen, body_color,
							   (x + 3, y + 3, self.cell_size - 6, self.cell_size - 6))
				pygame.draw.rect(self.screen, (0, max(50, intensity - 50), 0),
							   (x + 3, y + 3, self.cell_size - 6, self.cell_size - 6), 2)

				# Add scales pattern
				if i % 2 == 0:
					scale_color = (0, min(255, intensity + 30), 0)
					pygame.draw.circle(self.screen, scale_color,
									 (x + self.cell_size//2, y + self.cell_size//2), 3)

	def draw_food(self):
		"""Draw animated apple-like food"""
		x = self.food[0] * self.cell_size
		y = self.food[1] * self.cell_size

		# Pulsing animation
		pulse = math.sin(self.food_animation * 0.2) * 2
		size_offset = int(pulse)

		# Apple body (red with gradient)
		apple_size = self.cell_size - 6 + size_offset
		apple_rect = (x + 3 - size_offset//2, y + 5 - size_offset//2, apple_size, apple_size - 2)
		pygame.draw.ellipse(self.screen, (255, 50, 50), apple_rect)

		# Apple highlight
		highlight_size = apple_size // 2
		highlight_rect = (x + 6 - size_offset//4, y + 7 - size_offset//4, highlight_size, highlight_size)
		pygame.draw.ellipse(self.screen, (255, 150, 150), highlight_rect)

		# Apple stem
		stem_rect = (x + self.cell_size//2 - 1, y + 2, 3, 6)
		pygame.draw.rect(self.screen, (139, 69, 19), stem_rect)

		# Apple leaf
		leaf_points = [
			(x + self.cell_size//2 + 2, y + 3),
			(x + self.cell_size//2 + 6, y + 2),
			(x + self.cell_size//2 + 5, y + 6),
			(x + self.cell_size//2 + 3, y + 5)
		]
		pygame.draw.polygon(self.screen, (0, 150, 0), leaf_points)

	def draw_ui(self):
		"""Draw enhanced UI"""
		# Bottom panel background
		panel_rect = (0, WINDOW_HEIGHT - 120, WINDOW_WIDTH, 120)
		pygame.draw.rect(self.screen, (20, 20, 20), panel_rect)
		pygame.draw.line(self.screen, (100, 100, 100), (0, WINDOW_HEIGHT - 120), (WINDOW_WIDTH, WINDOW_HEIGHT - 120), 2)

		# Title
		title_text = self.font_large.render("S N A K E", True, (50, 255, 50))
		title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
		self.screen.blit(title_text, title_rect)

		# Score
		score_text = self.font.render(f"Score: {self.score}", True, WHITE)
		self.screen.blit(score_text, (20, WINDOW_HEIGHT - 70))

		# High Score
		if self.high_score > 0:
			high_score_text = self.font.render(f"Best: {self.high_score}", True, YELLOW)
			self.screen.blit(high_score_text, (20, WINDOW_HEIGHT - 40))

		# Length
		length_text = self.font.render(f"Length: {len(self.snake)}", True, WHITE)
		length_rect = length_text.get_rect(right=WINDOW_WIDTH - 20, y=WINDOW_HEIGHT - 70)
		self.screen.blit(length_text, length_rect)

		# Controls
		controls_text = self.font.render("Arrow keys to move | ESC: Menu", True, GRAY)
		controls_rect = controls_text.get_rect(right=WINDOW_WIDTH - 20, y=WINDOW_HEIGHT - 40)
		self.screen.blit(controls_text, controls_rect)

	def draw_game_over(self):
		"""Draw game over screen"""
		# Semi-transparent overlay
		overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 120))
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

		# Length achieved
		length_text = self.font.render(f"Snake Length: {len(self.snake)}", True, WHITE)
		length_rect = length_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10))
		self.screen.blit(length_text, length_rect)

		# New high score
		if self.score == self.high_score and self.high_score > 0:
			new_high_text = self.font.render("NEW HIGH SCORE!", True, YELLOW)
			new_high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
			self.screen.blit(new_high_text, new_high_rect)

		# Restart instructions
		restart_text = self.font.render("Press R to restart | ESC for menu", True, GREEN)
		restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
		self.screen.blit(restart_text, restart_rect)