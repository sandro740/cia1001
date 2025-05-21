import pygame
import sys
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# Fonts
FONT_PATH = pygame.font.get_default_font()
TITLE_FONT = pygame.font.Font(FONT_PATH, 48)
HEADER_FONT = pygame.font.Font(FONT_PATH, 32)
NORMAL_FONT = pygame.font.Font(FONT_PATH, 24)
SMALL_FONT = pygame.font.Font(FONT_PATH, 18)

@dataclass
class Button:
    rect: pygame.Rect
    text: str
    color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    font: pygame.font.Font
    action: callable
    enabled: bool = True

    def draw(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        color = self.color
        if self.enabled and self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Character:
    def __init__(self, name: str, rarity: str, attack: int, health: int):
        self.name = name
        self.rarity = rarity
        self.attack = attack
        self.health = health
        self.max_health = health
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.materials_inventory: Dict[str, int] = {}
        self.sprite = None  # Will hold character sprite
        self.animation_frames = []  # Will hold animation frames
        self.current_frame = 0

    def gain_exp(self, amount: int, material=None) -> bool:
        bonus_exp = material.exp_bonus if material else 0
        total_exp = amount + bonus_exp
        self.exp += total_exp
        
        if self.exp >= self.exp_to_level:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        rarity_multiplier = {
            "6★": 1.5, "5★": 1.3, "4★": 1.2, "3★": 1.1
        }
        multiplier = rarity_multiplier.get(self.rarity, 1.1)
        
        self.attack += int(2 * multiplier)
        self.max_health += int(5 * multiplier)
        self.health = self.max_health
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.2)

class GachaGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Gacha Fantasy World")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = "main_menu"  # main_menu, character_select, battle, etc.
        self.characters: List[Character] = []
        self.selected_character: Optional[Character] = None
        self.gems = 1000
        self.coins = 2000
        
        # Additional game state
        self.current_page = 0  # For character list pagination
        self.chars_per_page = 4
        self.current_boss = None
        self.battle_animation_frame = 0
        self.battle_message = ""
        self.battle_message_timer = 0
        
        # Initialize boss data
        self.boss_data = [
            {"name": "Dragon King", "level": 10, "attack": 15, "health": 200, "rarity": "5★"},
            {"name": "Dark Overlord", "level": 15, "attack": 20, "health": 250, "rarity": "5★"},
            {"name": "Ancient Golem", "level": 20, "attack": 25, "health": 300, "rarity": "5★"},
            {"name": "Demon Lord", "level": 25, "attack": 30, "health": 350, "rarity": "6★"}
        ]
        
        # Load assets
        self.load_assets()
        
        # Create UI elements
        self.create_buttons()
        self.create_character_buttons()
        self.create_battle_buttons()
        
    def load_assets(self):
        # Load background images
        self.backgrounds = {
            "main_menu": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)),  # Placeholder
            "battle": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)),     # Placeholder
            "summon": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))      # Placeholder
        }
        
        # Fill placeholders with gradients
        for bg in self.backgrounds.values():
            self.create_gradient_background(bg)
        
        # Load character sprites (placeholder)
        self.character_sprites = {
            "warrior": pygame.Surface((100, 100)),
            "mage": pygame.Surface((100, 100)),
            "archer": pygame.Surface((100, 100))
        }
        
        # Fill character sprites with colors
        self.character_sprites["warrior"].fill(RED)
        self.character_sprites["mage"].fill(BLUE)
        self.character_sprites["archer"].fill(GREEN)

    def create_gradient_background(self, surface: pygame.Surface):
        for y in range(WINDOW_HEIGHT):
            color = (
                int(20 + (y / WINDOW_HEIGHT) * 40),
                int(10 + (y / WINDOW_HEIGHT) * 20),
                int(50 + (y / WINDOW_HEIGHT) * 70)
            )
            pygame.draw.line(surface, color, (0, y), (WINDOW_WIDTH, y))

    def create_buttons(self):
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = WINDOW_HEIGHT // 2
        
        self.main_menu_buttons = [
            Button(
                pygame.Rect(
                    (WINDOW_WIDTH - button_width) // 2,
                    start_y + i * (button_height + spacing),
                    button_width,
                    button_height
                ),
                text,
                BLUE,
                PURPLE,
                NORMAL_FONT,
                action
            )
            for i, (text, action) in enumerate([
                ("Summon", lambda: self.set_state("summon")),
                ("Characters", lambda: self.set_state("character_select")),
                ("Battle", lambda: self.set_state("battle_prep")),
                ("Shop", lambda: self.set_state("shop")),
                ("Quit", self.quit_game)
            ])
        ]

        # Add summon buttons
        self.summon_buttons = [
            Button(
                pygame.Rect(
                    (WINDOW_WIDTH - button_width) // 2,
                    start_y + i * (button_height + spacing),
                    button_width,
                    button_height
                ),
                text,
                BLUE,
                PURPLE,
                NORMAL_FONT,
                action
            )
            for i, (text, action) in enumerate([
                ("Single Summon (100 Gems)", lambda: self.perform_summon(False)),
                ("Multi Summon (1000 Gems)", lambda: self.perform_summon(True)),
                ("Back", lambda: self.set_state("main_menu"))
            ])
        ]

    def create_character_buttons(self):
        button_width = 150
        button_height = 40
        spacing = 10
        
        # Navigation buttons
        self.character_nav_buttons = [
            Button(
                pygame.Rect(20, WINDOW_HEIGHT - 60, 100, 40),
                "Previous",
                BLUE,
                PURPLE,
                NORMAL_FONT,
                lambda: self.change_page(-1)
            ),
            Button(
                pygame.Rect(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60, 100, 40),
                "Next",
                BLUE,
                PURPLE,
                NORMAL_FONT,
                lambda: self.change_page(1)
            ),
            Button(
                pygame.Rect(20, 20, 100, 40),
                "Back",
                RED,
                PURPLE,
                NORMAL_FONT,
                lambda: self.set_state("main_menu")
            )
        ]

    def create_battle_buttons(self):
        self.battle_buttons = [
            Button(
                pygame.Rect(20, WINDOW_HEIGHT - 60, 100, 40),
                "Attack",
                RED,
                PURPLE,
                NORMAL_FONT,
                self.perform_attack
            ),
            Button(
                pygame.Rect(130, WINDOW_HEIGHT - 60, 100, 40),
                "Skill",
                BLUE,
                PURPLE,
                NORMAL_FONT,
                self.use_skill
            ),
            Button(
                pygame.Rect(240, WINDOW_HEIGHT - 60, 100, 40),
                "Item",
                GREEN,
                PURPLE,
                NORMAL_FONT,
                self.use_item
            ),
            Button(
                pygame.Rect(20, 20, 100, 40),
                "Retreat",
                RED,
                PURPLE,
                NORMAL_FONT,
                lambda: self.set_state("main_menu")
            )
        ]

    def set_state(self, new_state: str):
        self.state = new_state
        # Additional state initialization can be done here

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def draw_main_menu(self):
        # Draw background
        self.screen.blit(self.backgrounds["main_menu"], (0, 0))
        
        # Draw title
        title = TITLE_FONT.render("Gacha Fantasy World", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw currency
        gems_text = NORMAL_FONT.render(f"Gems: {self.gems}", True, WHITE)
        coins_text = NORMAL_FONT.render(f"Coins: {self.coins}", True, WHITE)
        self.screen.blit(gems_text, (20, 20))
        self.screen.blit(coins_text, (20, 50))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons:
            button.draw(self.screen, mouse_pos)

    def handle_main_menu_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.main_menu_buttons:
                if button.enabled and button.rect.collidepoint(mouse_pos):
                    button.action()

    def draw_character_select(self):
        # Draw background
        self.screen.blit(self.backgrounds["main_menu"], (0, 0))
        
        # Draw title
        title = HEADER_FONT.render("Character Selection", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw character slots
        start_idx = self.current_page * self.chars_per_page
        end_idx = min(start_idx + self.chars_per_page, len(self.characters))
        
        for i, char in enumerate(self.characters[start_idx:end_idx]):
            # Calculate position
            x = (WINDOW_WIDTH // 2) - 400 + (i % 2) * 400
            y = 150 + (i // 2) * 250
            
            # Draw character card
            self.draw_character_card(char, x, y, char == self.selected_character)
        
        # Draw navigation buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.character_nav_buttons:
            button.enabled = (
                (button.text != "Previous" or self.current_page > 0) and
                (button.text != "Next" or (self.current_page + 1) * self.chars_per_page < len(self.characters))
            )
            button.draw(self.screen, mouse_pos)

    def draw_character_card(self, char: Character, x: int, y: int, selected: bool):
        # Draw card background
        card_width = 350
        card_height = 200
        card_rect = pygame.Rect(x, y, card_width, card_height)
        
        # Different background color based on rarity
        rarity_colors = {
            "6★": (150, 50, 150),
            "5★": (150, 150, 50),
            "4★": (100, 100, 150),
            "3★": (100, 100, 100)
        }
        bg_color = rarity_colors.get(char.rarity, GRAY)
        
        pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)
        if selected:
            pygame.draw.rect(self.screen, GOLD, card_rect, 3, border_radius=15)
        else:
            pygame.draw.rect(self.screen, WHITE, card_rect, 1, border_radius=15)
        
        # Draw character sprite
        sprite_rect = pygame.Rect(x + 10, y + 10, 80, 80)
        if char.sprite:
            self.screen.blit(char.sprite, sprite_rect)
        else:
            pygame.draw.rect(self.screen, RED, sprite_rect)  # Placeholder
        
        # Draw character info
        name_text = NORMAL_FONT.render(f"{char.name} [{char.rarity}]", True, WHITE)
        level_text = SMALL_FONT.render(f"Level {char.level}", True, WHITE)
        stats_text = SMALL_FONT.render(f"ATK: {char.attack} | HP: {char.health}/{char.max_health}", True, WHITE)
        exp_text = SMALL_FONT.render(f"EXP: {char.exp}/{char.exp_to_level}", True, WHITE)
        
        self.screen.blit(name_text, (x + 100, y + 20))
        self.screen.blit(level_text, (x + 100, y + 50))
        self.screen.blit(stats_text, (x + 100, y + 80))
        self.screen.blit(exp_text, (x + 100, y + 110))
        
        # Draw exp bar
        exp_bar_rect = pygame.Rect(x + 100, y + 140, 200, 20)
        pygame.draw.rect(self.screen, GRAY, exp_bar_rect)
        exp_fill_rect = pygame.Rect(
            exp_bar_rect.x,
            exp_bar_rect.y,
            exp_bar_rect.width * (char.exp / char.exp_to_level),
            exp_bar_rect.height
        )
        pygame.draw.rect(self.screen, BLUE, exp_fill_rect)
        pygame.draw.rect(self.screen, WHITE, exp_bar_rect, 1)

    def draw_battle(self):
        # Draw background
        self.screen.blit(self.backgrounds["battle"], (0, 0))
        
        if not self.selected_character or not self.current_boss:
            return
        
        # Draw character
        char_x = 200
        char_y = WINDOW_HEIGHT - 300
        self.draw_battle_character(self.selected_character, char_x, char_y, True)
        
        # Draw boss
        boss_x = WINDOW_WIDTH - 300
        boss_y = 100
        self.draw_battle_character(self.current_boss, boss_x, boss_y, False)
        
        # Draw battle message
        if self.battle_message and self.battle_message_timer > 0:
            msg_text = HEADER_FONT.render(self.battle_message, True, WHITE)
            msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.battle_buttons:
            button.draw(self.screen, mouse_pos)

    def draw_battle_character(self, char, x: int, y: int, is_player: bool):
        # Draw character sprite
        sprite_rect = pygame.Rect(x, y, 100, 100)
        if char.sprite:
            self.screen.blit(char.sprite, sprite_rect)
        else:
            pygame.draw.rect(self.screen, RED if is_player else PURPLE, sprite_rect)
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_rect = pygame.Rect(x - 50, y - 30, health_width, health_height)
        pygame.draw.rect(self.screen, RED, health_rect)
        
        health_percent = char.health / char.max_health
        health_fill_rect = pygame.Rect(
            health_rect.x,
            health_rect.y,
            health_rect.width * health_percent,
            health_rect.height
        )
        pygame.draw.rect(self.screen, GREEN, health_fill_rect)
        pygame.draw.rect(self.screen, WHITE, health_rect, 1)
        
        # Draw character info
        name_text = NORMAL_FONT.render(f"{char.name} Lv.{char.level}", True, WHITE)
        hp_text = SMALL_FONT.render(f"HP: {char.health}/{char.max_health}", True, WHITE)
        
        self.screen.blit(name_text, (x - 50, y - 60))
        self.screen.blit(hp_text, (x - 50, y + 110))

    def handle_character_select_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle navigation buttons
            for button in self.character_nav_buttons:
                if button.enabled and button.rect.collidepoint(mouse_pos):
                    button.action()
                    return
            
            # Handle character selection
            start_idx = self.current_page * self.chars_per_page
            end_idx = min(start_idx + self.chars_per_page, len(self.characters))
            
            for i, char in enumerate(self.characters[start_idx:end_idx]):
                x = (WINDOW_WIDTH // 2) - 400 + (i % 2) * 400
                y = 150 + (i // 2) * 250
                card_rect = pygame.Rect(x, y, 350, 200)
                
                if card_rect.collidepoint(mouse_pos):
                    self.selected_character = char
                    return

    def handle_battle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.battle_buttons:
                if button.enabled and button.rect.collidepoint(mouse_pos):
                    button.action()

    def perform_attack(self):
        if not self.selected_character or not self.current_boss:
            return
        
        # Calculate damage
        damage = random.randint(
            self.selected_character.attack - 5,
            self.selected_character.attack + 12
        )
        
        # Apply damage and show message
        self.current_boss.health -= damage
        self.battle_message = f"Dealt {damage} damage!"
        self.battle_message_timer = 60  # Show message for 60 frames

    def use_skill(self):
        # Implement skill usage
        pass

    def use_item(self):
        # Implement item usage
        pass

    def change_page(self, delta: int):
        new_page = self.current_page + delta
        if 0 <= new_page * self.chars_per_page < len(self.characters):
            self.current_page = new_page

    def update(self):
        if self.state == "battle" and self.battle_message_timer > 0:
            self.battle_message_timer -= 1

    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw current state
        if self.state == "main_menu":
            self.draw_main_menu()
        elif self.state == "character_select":
            self.draw_character_select()
        elif self.state == "battle":
            self.draw_battle()
        elif self.state == "summon":
            self.draw_summon()
        elif self.state == "battle_prep":
            self.draw_battle_prep()
        # Add more states here

    def handle_input(self, event):
        if self.state == "main_menu":
            self.handle_main_menu_input(event)
        elif self.state == "character_select":
            self.handle_character_select_input(event)
        elif self.state == "battle":
            self.handle_battle_input(event)
        elif self.state == "summon":
            self.handle_summon_input(event)
        elif self.state == "battle_prep":
            self.handle_battle_prep_input(event)

    def draw_summon(self):
        # Draw background
        self.screen.blit(self.backgrounds["summon"], (0, 0))
        
        # Draw title
        title = TITLE_FONT.render("Summon Characters", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw currency
        gems_text = NORMAL_FONT.render(f"Gems: {self.gems}", True, WHITE)
        self.screen.blit(gems_text, (20, 20))
        
        # Draw rates info
        rates_text = [
            "Summon Rates:",
            "6★ (LR): 1%",
            "5★ (SSR): 4%",
            "4★ (SR): 15%",
            "3★ (R): 30%",
            "2★ (N): 50%"
        ]
        
        for i, text in enumerate(rates_text):
            rate_surface = SMALL_FONT.render(text, True, WHITE)
            self.screen.blit(rate_surface, (WINDOW_WIDTH - 200, 100 + i * 30))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.summon_buttons:
            button.draw(self.screen, mouse_pos)

    def handle_summon_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.summon_buttons:
                if button.enabled and button.rect.collidepoint(mouse_pos):
                    button.action()

    def perform_summon(self, is_multi: bool):
        cost = 1000 if is_multi else 100
        if self.gems < cost:
            self.battle_message = "Not enough gems!"
            self.battle_message_timer = 60
            return
        
        self.gems -= cost
        summons = 10 if is_multi else 1
        
        for _ in range(summons):
            roll = random.random() * 100
            if roll < 1:  # 1% LR
                rarity = "6★"
                base_attack = random.randint(25, 30)
                base_health = random.randint(120, 150)
            elif roll < 5:  # 4% SSR
                rarity = "5★"
                base_attack = random.randint(20, 25)
                base_health = random.randint(100, 120)
            elif roll < 20:  # 15% SR
                rarity = "4★"
                base_attack = random.randint(15, 20)
                base_health = random.randint(80, 100)
            elif roll < 50:  # 30% R
                rarity = "3★"
                base_attack = random.randint(10, 15)
                base_health = random.randint(60, 80)
            else:  # 50% N
                rarity = "2★"
                base_attack = random.randint(5, 10)
                base_health = random.randint(40, 60)
            
            # Generate random character name
            prefixes = ["Dark", "Light", "Fire", "Water", "Earth", "Wind"]
            classes = ["Warrior", "Mage", "Archer", "Knight", "Assassin", "Healer"]
            name = f"{random.choice(prefixes)} {random.choice(classes)}"
            
            # Create and add character
            character = Character(name, rarity, base_attack, base_health)
            self.characters.append(character)
            
            # Show summon result
            self.battle_message = f"Summoned {name} ({rarity})!"
            self.battle_message_timer = 60

    def draw_battle_prep(self):
        # Draw background
        self.screen.blit(self.backgrounds["battle"], (0, 0))
        
        # Draw title
        title = TITLE_FONT.render("Battle Preparation", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        if not self.characters:
            msg = HEADER_FONT.render("No characters available! Summon some first.", True, WHITE)
            msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(msg, msg_rect)
            
            # Back button
            back_button = Button(
                pygame.Rect(20, 20, 100, 40),
                "Back",
                RED,
                PURPLE,
                NORMAL_FONT,
                lambda: self.set_state("main_menu")
            )
            back_button.draw(self.screen, pygame.mouse.get_pos())
            return
        
        # Draw character selection section
        char_select_text = HEADER_FONT.render("Select Your Character:", True, WHITE)
        self.screen.blit(char_select_text, (50, 120))
        
        # Draw available characters
        start_idx = self.current_page * self.chars_per_page
        end_idx = min(start_idx + self.chars_per_page, len(self.characters))
        
        for i, char in enumerate(self.characters[start_idx:end_idx]):
            x = 50 + (i % 2) * 400
            y = 180 + (i // 2) * 250
            self.draw_character_card(char, x, y, char == self.selected_character)
        
        # Draw boss selection section
        boss_select_text = HEADER_FONT.render("Select Your Opponent:", True, WHITE)
        self.screen.blit(boss_select_text, (50, 500))
        
        # Draw boss options
        for i, boss in enumerate(self.boss_data):
            button = Button(
                pygame.Rect(50 + i * 250, 550, 200, 50),
                f"{boss['name']} Lv.{boss['level']}",
                PURPLE,
                RED,
                NORMAL_FONT,
                lambda b=boss: self.start_battle(b)
            )
            button.draw(self.screen, pygame.mouse.get_pos())
        
        # Back button
        back_button = Button(
            pygame.Rect(20, 20, 100, 40),
            "Back",
            RED,
            PURPLE,
            NORMAL_FONT,
            lambda: self.set_state("main_menu")
        )
        back_button.draw(self.screen, pygame.mouse.get_pos())

    def handle_battle_prep_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle back button
            back_button = Button(
                pygame.Rect(20, 20, 100, 40),
                "Back",
                RED,
                PURPLE,
                NORMAL_FONT,
                lambda: self.set_state("main_menu")
            )
            if back_button.rect.collidepoint(mouse_pos):
                back_button.action()
                return
            
            # Handle character selection
            start_idx = self.current_page * self.chars_per_page
            end_idx = min(start_idx + self.chars_per_page, len(self.characters))
            
            for i, char in enumerate(self.characters[start_idx:end_idx]):
                x = 50 + (i % 2) * 400
                y = 180 + (i // 2) * 250
                card_rect = pygame.Rect(x, y, 350, 200)
                
                if card_rect.collidepoint(mouse_pos):
                    self.selected_character = char
                    return
            
            # Handle boss selection
            if self.selected_character:  # Only allow boss selection if character is selected
                for i, boss in enumerate(self.boss_data):
                    button_rect = pygame.Rect(50 + i * 250, 550, 200, 50)
                    if button_rect.collidepoint(mouse_pos):
                        self.start_battle(boss)
                        return

    def start_battle(self, boss_data: dict):
        if not self.selected_character:
            self.battle_message = "Select a character first!"
            self.battle_message_timer = 60
            return
        
        # Create boss character
        self.current_boss = Character(
            boss_data["name"],
            boss_data["rarity"],
            boss_data["attack"],
            boss_data["health"]
        )
        self.current_boss.level = boss_data["level"]
        
        # Switch to battle state
        self.state = "battle"
        self.battle_message = "Battle Start!"
        self.battle_message_timer = 60

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                self.handle_input(event)
            
            # Update game state
            self.update()
            
            # Draw current state
            self.draw()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = GachaGame()
    game.run() 