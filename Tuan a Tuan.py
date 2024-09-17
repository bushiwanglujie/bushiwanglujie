import pygame
import random
import time
import json
import os

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 450
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tuan a Tuan")

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GREEN = (144, 238, 144)  # 浅绿色
LIGHT_BLUE = (173, 216, 230)   # 浅蓝色
LIGHT_RED = (255, 182, 193)    # 浅红色

# Define difficulty constants
EASY = 0
MEDIUM = 1
HARD = 2


# Load images
def load_images():
    images = {}
    for filename in os.listdir("patterns"):
        if filename.endswith(".jpg"):
            image = pygame.image.load(os.path.join("patterns", filename))
            image = pygame.transform.scale(image, (70, 70))  # Resize to 70x70
            images[filename[:-4]] = image
    return images


IMAGES = load_images()


# Modify BACKGROUNDS loading
def load_backgrounds():
    backgrounds = {
        'menu': pygame.image.load(os.path.join("backgrounds", "menu_background.jpg")),
        EASY: pygame.image.load(os.path.join("backgrounds", "easy_background.jpg")),
        MEDIUM: pygame.image.load(os.path.join("backgrounds", "medium_background.jpg")),
        HARD: pygame.image.load(os.path.join("backgrounds", "hard_background.jpg")),
        'success': pygame.image.load(os.path.join("backgrounds", "success_background.jpg")),
        'failure': pygame.image.load(os.path.join("backgrounds", "failure_background.jpg"))
    }
    for key, bg in backgrounds.items():
        backgrounds[key] = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    return backgrounds


BACKGROUNDS = load_backgrounds()

# Game states
MENU = 0
PLAYING = 1
GAMEOVER = 2
DIFFICULTY_SELECT = 3
HIGH_SCORES = 4  # New state for high scores


class Icon:
    def __init__(self, image, x, y, layer):
        self.image = image
        self.x = x
        self.y = y
        self.layer = layer
        self.selected = False


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        self.state = MENU
        self.icons = []
        self.score = 0
        self.time_left = 60
        self.last_time = time.time()
        self.selected_icons = []
        self.difficulty = EASY
        self.hints = 3
        self.undos = 2
        self.last_removed = []
        self.high_scores = self.load_high_scores()
        self.background = BACKGROUNDS['menu']
        self.menu_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Start Game", LIGHT_GREEN),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "High Scores", LIGHT_BLUE),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "Quit", LIGHT_RED)
        ]
        self.difficulty_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50, "Easy", LIGHT_GREEN),
            Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Medium", LIGHT_BLUE),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Hard", LIGHT_RED)
        ]
        self.game_result = None
        self.game_over_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Continue", LIGHT_GREEN),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 130, 200, 50, "Quit", LIGHT_RED)
        ]

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                scores = json.load(f)
                # 确保所有难度都有对应的分数
                return {EASY: scores.get(str(EASY), 0),
                        MEDIUM: scores.get(str(MEDIUM), 0),
                        HARD: scores.get(str(HARD), 0)}
        except (FileNotFoundError, json.JSONDecodeError):
            return {EASY: 0, MEDIUM: 0, HARD: 0}

    def save_high_scores(self):
        scores_to_save = {str(k): v for k, v in self.high_scores.items()}
        with open('high_scores.json', 'w') as f:
            json.dump(scores_to_save, f)

    def start_game(self):
        self.state = PLAYING
        self.icons = []
        self.score = 0
        self.time_left = 60  # 所有难度等级都设置为60秒
        self.last_time = time.time()
        self.selected_icons = []
        self.hints = 3
        self.undos = 2
        self.last_removed = []
        self.generate_icons()
        self.background = BACKGROUNDS[self.difficulty]
        self.game_result = None

    def generate_icons(self):
        if self.difficulty == EASY:
            layers = 3
            icons_per_layer = 12
        elif self.difficulty == MEDIUM:
            layers = 4
            icons_per_layer = 15
        else:  # HARD
            layers = 5
            icons_per_layer = 18

        total_icons = layers * icons_per_layer
        icon_types = list(IMAGES.keys())

        icon_counts = {icon_type: 0 for icon_type in icon_types}
        for _ in range(total_icons):
            icon_type = random.choice(icon_types)
            icon_counts[icon_type] += 1

        for icon_type in icon_counts:
            remainder = icon_counts[icon_type] % 3
            if remainder != 0:
                icon_counts[icon_type] += (3 - remainder)

        self.icons = []
        for icon_type, count in icon_counts.items():
            for _ in range(count):
                x = random.randint(0, WIDTH - 70)
                y = random.randint(50, HEIGHT - 70)
                layer = random.randint(0, layers - 1)
                self.icons.append(Icon(IMAGES[icon_type], x, y, layer))

        random.shuffle(self.icons)

    def update(self):
        if self.state == PLAYING:
            current_time = time.time()
            self.time_left -= current_time - self.last_time
            self.last_time = current_time

            if self.time_left <= 0 or len(self.icons) == 0:
                self.state = GAMEOVER
                self.game_result = 'success' if len(self.icons) == 0 else 'failure'
                self.update_high_score()

    def update_high_score(self):
        if self.score > self.high_scores[self.difficulty]:
            self.high_scores[self.difficulty] = self.score
            self.save_high_scores()

    def draw(self):
        if self.state == MENU or self.state == HIGH_SCORES:
            self.background = BACKGROUNDS['menu']
        elif self.state == PLAYING:
            self.background = BACKGROUNDS[self.difficulty]
        elif self.state == GAMEOVER:
            self.background = BACKGROUNDS['success'] if self.game_result == 'success' else BACKGROUNDS['failure']

        screen.blit(self.background, (0, 0))

        if self.state == MENU:
            self.draw_menu()
        elif self.state == DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAMEOVER:
            self.draw_game_over()
        elif self.state == HIGH_SCORES:
            self.draw_high_scores()

        pygame.display.flip()

    def draw_menu(self):
        font = pygame.font.Font(None, 74)
        text = font.render("Tuan a Tuan", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        for button in self.menu_buttons:
            button.draw(screen)

    def draw_difficulty_select(self):
        font = pygame.font.Font(None, 74)
        text = font.render("Select Difficulty", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        for button in self.difficulty_buttons:
            button.draw(screen)

    def draw_high_scores(self):
        screen.blit(self.background, (0, 0))  # 确保使用与主菜单相同的背景

        font = pygame.font.Font(None, 74)
        text = font.render("High Scores", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        font = pygame.font.Font(None, 48)
        y = HEIGHT // 2 - 75
        difficulties = [("Easy", EASY), ("Medium", MEDIUM), ("Hard", HARD)]
        for diff_text, difficulty in difficulties:
            score = self.high_scores.get(difficulty, 0)  # 使用 get 方法，如果键不存在则返回 0
            score_text = font.render(f"{diff_text}: {score}", True, BLACK)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y))
            y += 60

        font = pygame.font.Font(None, 36)
        back_text = font.render("Press any key to return", True, BLACK)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 100))

    def draw_game(self):
        for icon in sorted(self.icons, key=lambda x: x.layer):
            screen.blit(icon.image, (icon.x, icon.y))
            if icon.selected:
                pygame.draw.rect(screen, RED, (icon.x, icon.y, 70, 70), 2)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        time_text = font.render(f"Time: {int(self.time_left)}", True, BLACK)
        hint_text = font.render(f"Hints: {self.hints}", True, BLACK)
        undo_text = font.render(f"Undos: {self.undos}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (WIDTH - 150, 10))
        screen.blit(hint_text, (10, 50))
        screen.blit(undo_text, (10, 90))

    def draw_game_over(self):
        if self.game_result == 'success':
            text = "Congratulations!"
        else:
            text = "Game Over"

        font = pygame.font.Font(None, 74)
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 4))

        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Your Score: {self.score}", True, BLACK)
        high_score_text = font.render(f"High Score: {self.high_scores[self.difficulty]}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT * 3 // 4))

        for button in self.game_over_buttons:
            button.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == MENU:
                for i, button in enumerate(self.menu_buttons):
                    if button.is_clicked(event.pos):
                        if i == 0:  # Start Game
                            self.state = DIFFICULTY_SELECT
                        elif i == 1:  # High Scores
                            self.state = HIGH_SCORES
                        elif i == 2:  # Quit
                            return False  # End the game
            elif self.state == DIFFICULTY_SELECT:
                for i, button in enumerate(self.difficulty_buttons):
                    if button.is_clicked(event.pos):
                        self.difficulty = i
                        self.start_game()
            elif self.state == PLAYING:
                self.check_click(event.pos)
            elif self.state == GAMEOVER:
                for i, button in enumerate(self.game_over_buttons):
                    if button.is_clicked(event.pos):
                        if i == 0:  # Continue
                            self.state = DIFFICULTY_SELECT
                        elif i == 1:  # Quit
                            return False  # End the game
        elif event.type == pygame.KEYDOWN:
            if self.state == HIGH_SCORES:
                self.state = MENU
            elif self.state == PLAYING:
                if event.key == pygame.K_h and self.hints > 0:
                    self.use_hint()
                elif event.key == pygame.K_u and self.undos > 0:
                    self.use_undo()
        return True

    def check_click(self, pos):
        for icon in reversed(self.icons):
            if icon.x < pos[0] < icon.x + 70 and icon.y < pos[1] < icon.y + 70:
                if icon not in self.selected_icons:
                    icon.selected = True
                    self.selected_icons.append(icon)
                    if len(self.selected_icons) == 3:
                        if self.check_match():
                            self.remove_matched_icons()
                        else:
                            for selected_icon in self.selected_icons:
                                selected_icon.selected = False
                        self.selected_icons = []
                break

    def check_match(self):
        return len(set(icon.image for icon in self.selected_icons)) == 1

    def remove_matched_icons(self):
        self.last_removed = self.selected_icons.copy()
        for icon in self.selected_icons:
            self.icons.remove(icon)
        self.score += 30

    def use_hint(self):
        self.hints -= 1
        matching_icons = [icon for icon in self.icons if sum(1 for i in self.icons if i.image == icon.image) >= 3]
        if matching_icons:
            for icon in random.sample(matching_icons, 3):
                icon.selected = True
                self.selected_icons.append(icon)
            self.remove_matched_icons()
            self.selected_icons = []

    def use_undo(self):
        if self.last_removed:
            self.undos -= 1
            for icon in self.last_removed:
                self.icons.append(icon)
                icon.selected = False
            self.score -= 30
            self.last_removed = []


def main():
    game = Game()
    clock = pygame.time.Clock()

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                running = game.handle_event(event)

        # Update game state
        game.update()

        # Draw the game
        screen.fill(WHITE)
        game.draw()

        # 添加调试信息
        print(f"Current state: {game.state}")

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(60)

    # Save high scores before quitting
    game.save_high_scores()
    pygame.quit()


if __name__ == "__main__":
    main()