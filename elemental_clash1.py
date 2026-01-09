import pygame 
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Elemental Clash")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont("arial", 32, bold=True)
small_font = pygame.font.SysFont("arial", 24)

# Load background image
try:
    bg_image = pygame.transform.scale(pygame.image.load("assets/characters/battle_bg.png"), (WIDTH, HEIGHT))
except Exception as e:
    print("\u274c Failed to load battle_bg.png:", e)
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((0, 100, 200))

# Sound functions
def play_sound(file_path):
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.play()
    except:
        pass

def play_bgm(file_path):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)
    except:
        pass

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Character data
character_data = [
    {"name": "Pyra", "file": "assets/characters/pyra.png", "type": "fire"},
    {"name": "Terros", "file": "assets/characters/terros.png", "type": "earth"},
    {"name": "Voltra", "file": "assets/characters/voltra.png", "type": "lightning"},
    {"name": "Aquon", "file": "assets/characters/aquon.png", "type": "water"}
]

for char in character_data:
    try:
        char["image"] = pygame.transform.scale(pygame.image.load(char["file"]), (200, 200))
    except:
        char["image"] = pygame.Surface((200, 200))
        char["image"].fill(GRAY)

# Overlay effect
overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
def show_effect(effect):
    overlay_surface.fill((0, 0, 0, 0))
    if effect == "shatter":
        overlay_surface.fill((255, 0, 0, 80))
        play_sound("assets/sounds/shatter.mp3")
    elif effect == "glow":
        overlay_surface.fill((0, 255, 0, 80))
        play_sound("assets/sounds/glow.mp3")
    screen.blit(overlay_surface, (0, 0))
    pygame.display.flip()
    pygame.time.delay(600)

# Music and SFX
play_bgm("assets/sounds/bgm.mp3")
sound_effects = {
    "fire": "assets/sounds/fire.mp3",
    "water": "assets/sounds/water.mp3",
    "earth": "assets/sounds/earth.mp3",
    "lightning": "assets/sounds/lightning.mp3",
    "victory": "assets/sounds/victory.mp3"
}

def play_element_sound(element):
    file = sound_effects.get(element)
    if file:
        try:
            sound = pygame.mixer.Sound(file)
            sound.set_volume(1.0)
            sound.play(maxtime=2000)
        except:
            pass

# Type advantages
weaknesses = {
    "fire": {"water": 2, "lightning": 1},
    "earth": {"fire": 2, "water": 1},
    "lightning": {"earth": 2, "fire": 1},
    "water": {"lightning": 2, "earth": 1}
}

# Game state
show_welcome = True
battle_started = False
character_selecting = False
player1_character = None
player2_character = None
current_turn = 1
move_result_text = ""
winner = None
hp = {1: 100, 2: 100}
poisoned = {1: False, 2: False}
move_choices = []

# UI buttons
start_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 60, "Start the War")
replay_button = Button(WIDTH//2 - 150, HEIGHT//2, 130, 60, "Replay", GREEN)
quit_button = Button(WIDTH//2 + 20, HEIGHT//2, 130, 60, "Quit", RED)

# Moves
all_moves = {
    "fire": [
        {"name": "Fire Flick", "damage": 20, "type": "fire"},
        {"name": "Flame Kick", "damage": 25, "type": "fire"},
        {"name": "Dragon Flame", "damage": 30, "type": "fire"}
    ],
    "earth": [
        {"name": "Rock Slam", "damage": 20, "type": "earth"},
        {"name": "Quake Smash", "damage": 25, "type": "earth"},
        {"name": "Mega Quake", "damage": 30, "type": "earth"}
    ],
    "lightning": [
        {"name": "Shock Hit", "damage": 20, "type": "lightning"},
        {"name": "Light Hit", "damage": 25, "type": "lightning"},
        {"name": "Big Thunder", "damage": 30, "type": "lightning"}
    ],
    "water": [
        {"name": "Water Jet", "damage": 20, "type": "water"},
        {"name": "Aqua Blade", "damage": 25, "type": "water"},
        {"name": "Wave Smash", "damage": 30, "type": "water"}
    ],
    "status": [
        {"name": "Heal Spark", "effect": "heal", "type": "status"},
        {"name": "Poison Bite", "effect": "poison", "type": "status"}
    ]
}

def generate_moves(player_type):
    base = random.sample(all_moves[player_type], 2)
    if random.random() < 0.7:
        base.append(random.choice(all_moves["status"]))
    return base

def calculate_damage(move, attacker_type, defender_type):
    if move["type"] == "status":
        return 0
    base = move["damage"]
    multiplier = weaknesses.get(defender_type, {}).get(attacker_type, 1)
    return base * multiplier

def draw_battle_screen():
    screen.blit(bg_image, (0, 0))
    screen.blit(player1_character["image"], (WIDTH//6 - 100, HEIGHT//2 - 100))
    screen.blit(player2_character["image"], (WIDTH*5//6 - 100, HEIGHT//2 - 100))

    hp1 = small_font.render(f"HP: {hp[1]}" + (" (Poisoned)" if poisoned[1] else ""), True, RED if poisoned[1] else GREEN)
    hp2 = small_font.render(f"HP: {hp[2]}" + (" (Poisoned)" if poisoned[2] else ""), True, RED if poisoned[2] else GREEN)
    screen.blit(hp1, (WIDTH//6 - 100, HEIGHT//2 + 120))
    screen.blit(hp2, (WIDTH*5//6 - 100, HEIGHT//2 + 120))

    if winner is None:
        info_text = font.render(f"Player {current_turn}'s Turn", True, WHITE)
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 30))

        result_text = small_font.render(move_result_text, True, BLUE)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT - 100))

        for i, move in enumerate(move_choices):
            x = WIDTH//2 - 200 + (i % 2) * 200
            y = 100 + (i // 2) * 80
            pygame.draw.rect(screen, GRAY, (x, y, 180, 60))
            txt = small_font.render(move['name'], True, BLACK)
            screen.blit(txt, (x + 90 - txt.get_width() // 2, y + 15))
    else:
        victory_text = font.render(f"Player {winner} Wins!", True, YELLOW)
        screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, 100))
        replay_button.draw(screen)
        quit_button.draw(screen)

# Main game loop
running = True
while running:
    screen.blit(bg_image, (0, 0))

    if show_welcome:
        welcome = font.render("Gear Up for the ultimate Battle with Elemental Clash", True, WHITE)
        screen.blit(welcome, (WIDTH // 2 - welcome.get_width() // 2, HEIGHT // 3))
        start_button.draw(screen)

    elif character_selecting and not battle_started:
        current = 1 if not player1_character else 2
        title_text = font.render(f"Player {current} - Choose Your Character", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 6))

        total_width = len(character_data) * 220
        start_x = (WIDTH - total_width) // 2 + 10
        y = HEIGHT // 2 - 100
        for i, char in enumerate(character_data):
            x = start_x + i * 220
            screen.blit(char["image"], (x, y))
            name_text = font.render(char["name"], True, WHITE)
            screen.blit(name_text, (x + 100 - name_text.get_width() // 2, y + 220))

    elif battle_started:
        draw_battle_screen()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if show_welcome and start_button.is_clicked(pos):
                show_welcome = False
                character_selecting = True

            elif character_selecting and not battle_started:
                total_width = len(character_data) * 220
                start_x = (WIDTH - total_width) // 2 + 10
                y = HEIGHT // 2 - 100
                for i, char in enumerate(character_data):
                    x = start_x + i * 220
                    rect = pygame.Rect(x, y, 200, 200)
                    if rect.collidepoint(pos):
                        if not player1_character:
                            player1_character = char
                        elif not player2_character:
                            player2_character = char
                            character_selecting = False
                            battle_started = True
                            move_choices = generate_moves(player1_character['type'])

            elif battle_started:
                if winner:
                    if replay_button.is_clicked(pos):
                        show_welcome = True
                        battle_started = False
                        character_selecting = False
                        player1_character = None
                        player2_character = None
                        current_turn = 1
                        move_result_text = ""
                        winner = None
                        hp = {1: 100, 2: 100}
                        poisoned = {1: False, 2: False}
                    elif quit_button.is_clicked(pos):
                        running = False
                else:
                    for i in range(len(move_choices)):
                        x = WIDTH//2 - 200 + (i % 2) * 200
                        y = 100 + (i // 2) * 80
                        rect = pygame.Rect(x, y, 180, 60)
                        if rect.collidepoint(pos):
                            attacker = player1_character if current_turn == 1 else player2_character
                            defender = player2_character if current_turn == 1 else player1_character
                            atk = move_choices[i]

                            if atk['type'] == 'status':
                                if atk['effect'] == 'heal':
                                    if poisoned[current_turn]:
                                        poisoned[current_turn] = False
                                        move_result_text = f"Player {current_turn} cured poison!"
                                    else:
                                        hp[current_turn] = min(100, hp[current_turn] + 20)
                                        move_result_text = f"Player {current_turn} healed 20 HP!"
                                    show_effect("glow")
                                elif atk['effect'] == 'poison':
                                    if not poisoned[3 - current_turn]:
                                        poisoned[3 - current_turn] = True
                                        move_result_text = f"Player {3 - current_turn} is poisoned!"
                                    else:
                                        move_result_text = f"Already poisoned!"
                                    show_effect("shatter")
                            else:
                                damage = calculate_damage(atk, attacker['type'], defender['type'])
                                hp[3 - current_turn] -= damage
                                move_result_text = f"Player {current_turn} used {atk['name']} and dealt {damage} damage!"
                                play_element_sound(atk['type'])
                                show_effect("glow" if damage >= 30 else "shatter")

                            if hp[3 - current_turn] <= 0:
                                winner = current_turn
                                move_result_text = f"Player {winner} wins!"
                                play_sound("assets/sounds/victory.mp3")
                            else:
                                if poisoned[3 - current_turn]:
                                    hp[3 - current_turn] -= 5
                                    move_result_text += f"\nPlayer {3 - current_turn} suffers 5 poison damage!"
                                current_turn = 2 if current_turn == 1 else 1
                                move_choices = generate_moves((player1_character if current_turn == 1 else player2_character)['type'])

pygame.quit()
sys.exit()
