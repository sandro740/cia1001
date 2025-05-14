import time
import random
from colorama import init, Fore, Back, Style
import json
from typing import List, Dict

# Initialize colorama for Windows color support
init()

class Character:
    def __init__(self, name: str, rarity: str, attack: int, health: int):
        self.name = name
        self.rarity = rarity
        self.attack = attack
        self.health = health
        self.max_health = health
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100  # Base EXP needed to level up

    def gain_exp(self, amount: int) -> bool:
        """Returns True if leveled up"""
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        # Stat increases based on rarity
        rarity_multiplier = {
            "6★": 1.5,
            "5★": 1.3,
            "4★": 1.2,
            "3★": 1.1
        }
        multiplier = rarity_multiplier.get(self.rarity, 1.1)
        
        self.attack += int(2 * multiplier)
        self.max_health += int(5 * multiplier)
        self.health = self.max_health
        self.exp -= self.exp_to_level
        # Increase exp needed for next level
        self.exp_to_level = int(self.exp_to_level * 1.2)

    def to_dict(self):
        return {
            "name": self.name,
            "rarity": self.rarity,
            "attack": self.attack,
            "health": self.health,
            "max_health": self.max_health,
            "level": self.level,
            "exp": self.exp,
            "exp_to_level": self.exp_to_level
        }

    @classmethod
    def from_dict(cls, data):
        char = cls(data["name"], data["rarity"], data["attack"], data["health"])
        char.level = data["level"]
        char.max_health = data["max_health"]
        char.exp = data.get("exp", 0)
        char.exp_to_level = data.get("exp_to_level", 100)
        return char

class GachaGame:
    def __init__(self):
        self.characters_pool = {
            "6★": [
                ("Ultimate Dragon Emperor", 70, 130),
                ("Legendary Hero King", 65, 140),
                ("Ancient God Mage", 80, 110)
            ],
            "5★": [
                ("Celestial Dragon", 50, 100),
                ("Divine Knight", 45, 110),
                ("Mystic Sage", 55, 90)
            ],
            "4★": [
                ("Fire Warrior", 35, 80),
                ("Ice Mage", 40, 70),
                ("Earth Guardian", 30, 90),
                ("Lightning Ninja", 45, 60)
            ],
            "3★": [
                ("Forest Scout", 25, 60),
                ("Desert Wanderer", 20, 70),
                ("Mountain Dweller", 30, 50),
                ("Sea Raider", 28, 55)
            ]
        }
        self.rarity_rates = {
            "6★": 0.01,  # 1% chance for legendary
            "5★": 0.09,  # 9% chance
            "4★": 0.30,  # 30% chance
            "3★": 0.60   # 60% chance
        }
        
    def summon(self) -> Character:
        rarity = random.choices(
            list(self.rarity_rates.keys()),
            list(self.rarity_rates.values())
        )[0]
        
        char_template = random.choice(self.characters_pool[rarity])
        return Character(char_template[0], rarity, char_template[1], char_template[2])

def print_slow(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def display_title():
    title = '''
    ╔═══════════════════════════════════════╗
    ║         Gacha Fantasy World           ║
    ╚═══════════════════════════════════════╝
    '''
    print(Fore.CYAN + title + Style.RESET_ALL)

def display_character(character: Character):
    rarity_colors = {
        "6★": Fore.RED + Style.BRIGHT,
        "5★": Fore.YELLOW,
        "4★": Fore.MAGENTA,
        "3★": Fore.BLUE
    }
    color = rarity_colors.get(character.rarity, Fore.WHITE)
    print(f"{color}{character.rarity} {character.name}{Style.RESET_ALL}")
    print(f"Level: {character.level}")
    print(f"EXP: {character.exp}/{character.exp_to_level}")
    print(f"Attack: {character.attack}")
    print(f"Health: {character.health}/{character.max_health}")

def train_character(character: Character, gems_spent: int) -> int:
    """Train a character using gems. Returns exp gained."""
    exp_per_gem = 10
    exp_gained = gems_spent * exp_per_gem
    
    print_slow(f"\n{Fore.CYAN}Training {character.name}...{Style.RESET_ALL}")
    time.sleep(1)
    
    leveled_up = character.gain_exp(exp_gained)
    if leveled_up:
        print_slow(f"\n{Fore.YELLOW}Level Up! {character.name} is now level {character.level}!{Style.RESET_ALL}")
        print_slow(f"Attack increased to {character.attack}")
        print_slow(f"Health increased to {character.max_health}")
    
    return exp_gained

def battle(player_char: Character, enemy_char: Character) -> bool:
    print_slow(f"\n{Fore.YELLOW}Battle Start!{Style.RESET_ALL}")
    print_slow(f"Your {player_char.name} vs Enemy {enemy_char.name}")
    
    while player_char.health > 0 and enemy_char.health > 0:
        # Player attack
        damage = random.randint(player_char.attack - 5, player_char.attack + 5)
        enemy_char.health -= damage
        print_slow(f"{Fore.GREEN}Your {player_char.name} deals {damage} damage!{Style.RESET_ALL}")
        
        if enemy_char.health <= 0:
            break
            
        # Enemy attack
        damage = random.randint(enemy_char.attack - 5, enemy_char.attack + 5)
        player_char.health -= damage
        print_slow(f"{Fore.RED}Enemy {enemy_char.name} deals {damage} damage!{Style.RESET_ALL}")
        
        print(f"\nYour HP: {player_char.health}/{player_char.max_health}")
        print(f"Enemy HP: {enemy_char.health}/{enemy_char.max_health}")
        time.sleep(1)
    
    won = player_char.health > 0
    player_char.health = player_char.max_health  # Heal after battle
    
    if won:
        # Grant exp based on enemy's level and rarity
        exp_multiplier = {
            "6★": 2.0,
            "5★": 1.5,
            "4★": 1.2,
            "3★": 1.0
        }
        base_exp = 50
        exp_gain = int(base_exp * exp_multiplier.get(enemy_char.rarity, 1.0))
        leveled = player_char.gain_exp(exp_gain)
        print_slow(f"\n{Fore.GREEN}Gained {exp_gain} EXP!{Style.RESET_ALL}")
        if leveled:
            print_slow(f"\n{Fore.YELLOW}Level Up! {player_char.name} is now level {player_char.level}!{Style.RESET_ALL}")
    
    return won

def play_game():
    display_title()
    print_slow(Fore.YELLOW + "Welcome to Gacha Fantasy World!" + Style.RESET_ALL)
    time.sleep(1)
    
    player_name = input(Fore.GREEN + "\nWhat is your name, Summoner? " + Style.RESET_ALL)
    print_slow(f"\nWelcome, {Fore.CYAN}{player_name}{Style.RESET_ALL}! Your gacha adventure begins...")
    
    game = GachaGame()
    gems = 1000
    characters: List[Character] = []
    
    # Let player choose their 5★ or 6★ starter character
    print_slow(f"\n{Fore.YELLOW}Choose your starter character:{Style.RESET_ALL}")
    print_slow(f"\n{Fore.RED + Style.BRIGHT}=== 6★ LEGENDARY CHARACTERS ==={Style.RESET_ALL}")
    legendary_options = game.characters_pool["6★"]
    for i, (name, atk, hp) in enumerate(legendary_options, 1):
        print(f"\n{i}. {Fore.RED + Style.BRIGHT}{name}{Style.RESET_ALL}")
        print(f"   Attack: {atk}")
        print(f"   Health: {hp}")

    print_slow(f"\n{Fore.YELLOW}=== 5★ RARE CHARACTERS ==={Style.RESET_ALL}")
    five_star_options = game.characters_pool["5★"]
    for i, (name, atk, hp) in enumerate(five_star_options, len(legendary_options) + 1):
        print(f"\n{i}. {Fore.YELLOW}{name}{Style.RESET_ALL}")
        print(f"   Attack: {atk}")
        print(f"   Health: {hp}")
    
    total_options = len(legendary_options) + len(five_star_options)
    while True:
        try:
            choice = int(input(f"\nEnter the number of your chosen character (1-{total_options}): "))
            if 1 <= choice <= total_options:
                if choice <= len(legendary_options):
                    starter_char = legendary_options[choice - 1]
                    rarity = "6★"
                else:
                    starter_char = five_star_options[choice - len(legendary_options) - 1]
                    rarity = "5★"
                break
            else:
                print(f"{Fore.RED}Please enter a number between 1 and {total_options}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
    
    starter = Character(starter_char[0], rarity, starter_char[1], starter_char[2])
    characters.append(starter)
    print_slow(f"\n{Fore.YELLOW}Excellent choice! You received your chosen character:{Style.RESET_ALL}")
    display_character(starter)
    
    while True:
        print(f"\n{Fore.CYAN}Gems: {gems}{Style.RESET_ALL}")
        print(Fore.MAGENTA + """
1. Summon Character (100 gems)
2. View Characters
3. Battle
4. Train Character
5. Daily Quest
6. Quit Game
        """ + Style.RESET_ALL)
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            if gems >= 100:
                gems -= 100
                new_char = game.summon()
                characters.append(new_char)
                print_slow(f"\n{Fore.YELLOW}✨ Summoning... ✨{Style.RESET_ALL}")
                time.sleep(1)
                print_slow(f"\n{Fore.GREEN}You got:{Style.RESET_ALL}")
                display_character(new_char)
            else:
                print_slow(f"\n{Fore.RED}Not enough gems!{Style.RESET_ALL}")
                
        elif choice == '2':
            print_slow(f"\n{Fore.CYAN}Your Characters:{Style.RESET_ALL}")
            for i, char in enumerate(characters, 1):
                print(f"\n{i}. ", end="")
                display_character(char)
                
        elif choice == '3':
            if not characters:
                print_slow(f"\n{Fore.RED}You need characters to battle!{Style.RESET_ALL}")
                continue
                
            print_slow(f"\n{Fore.CYAN}Select your character for battle:{Style.RESET_ALL}")
            for i, char in enumerate(characters, 1):
                print(f"\n{i}. ", end="")
                display_character(char)
                
            try:
                char_choice = int(input("\nEnter character number: ")) - 1
                if 0 <= char_choice < len(characters):
                    # Create random enemy
                    enemy = game.summon()
                    won = battle(characters[char_choice], enemy)
                    
                    if won:
                        reward = random.randint(50, 150)
                        gems += reward
                        print_slow(f"\n{Fore.GREEN}Victory! You earned {reward} gems!{Style.RESET_ALL}")
                        # Level up character
                        characters[char_choice].level += 1
                        characters[char_choice].attack += 2
                        characters[char_choice].max_health += 5
                        characters[char_choice].health = characters[char_choice].max_health
                    else:
                        print_slow(f"\n{Fore.RED}Defeat! Better luck next time!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Invalid character number!{Style.RESET_ALL}")
            except ValueError:
                print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")
                
        elif choice == '4':
            if not characters:
                print_slow(f"\n{Fore.RED}You need characters to train!{Style.RESET_ALL}")
                continue
                
            print_slow(f"\n{Fore.CYAN}Select a character to train:{Style.RESET_ALL}")
            for i, char in enumerate(characters, 1):
                print(f"\n{i}. ", end="")
                display_character(char)
                
            try:
                char_choice = int(input("\nEnter character number: ")) - 1
                if 0 <= char_choice < len(characters):
                    print(f"\nYou have {gems} gems.")
                    print("Training costs: 50 gems = 500 EXP")
                    gems_to_spend = int(input("How many gems do you want to spend on training? "))
                    
                    if gems_to_spend <= gems and gems_to_spend >= 0:
                        gems -= gems_to_spend
                        exp_gained = train_character(characters[char_choice], gems_to_spend)
                        print_slow(f"\n{Fore.GREEN}Training complete! Gained {exp_gained} EXP!{Style.RESET_ALL}")
                    else:
                        print_slow(f"\n{Fore.RED}Not enough gems or invalid amount!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Invalid character number!{Style.RESET_ALL}")
            except ValueError:
                print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")
                
        elif choice == '5':
            # Daily quest - simple battle with guaranteed reward
            reward = random.randint(80, 120)
            gems += reward
            print_slow(f"\n{Fore.GREEN}Daily Quest completed! You earned {reward} gems!{Style.RESET_ALL}")
            
        elif choice == '6':
            print_slow(f"\n{Fore.YELLOW}Thanks for playing, {player_name}! Farewell!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    play_game() 