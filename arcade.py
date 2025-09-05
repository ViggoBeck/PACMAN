import pygame
import sys
import random
import math
import time
from collections import deque
from pacman import Game as PacManGame
from donkey_kong import DonkeyKongGame
from snake import SnakeGame
from space_invaders import SpaceInvadersGame
from galaga import GalagaGame

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
			{"name": "SPACE INVADERS", "color": CYAN, "description": "Defend Earth from aliens!"},
			{"name": "GALAGA", "color": YELLOW, "description": "Classic arcade space shooter!"},
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
			3: SpaceInvadersGame,
			4: GalagaGame,
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