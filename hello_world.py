import time
import random
from colorama import init, Fore, Back, Style
import json
from typing import List, Dict

# Initialize colorama for Windows color support
init()

class Material:
    def __init__(self, name: str, rarity: str, exp_bonus: int, description: str):
        self.name = name
        self.rarity = rarity
        self.exp_bonus = exp_bonus
        self.description = description

    def __str__(self):
        rarity_colors = {
            "Common": Fore.WHITE,
            "Rare": Fore.BLUE,
            "Epic": Fore.MAGENTA,
            "Legendary": Fore.YELLOW,
            "Mythical": Fore.RED + Style.BRIGHT
        }
        color = rarity_colors.get(self.rarity, Fore.WHITE)
        return f"{color}{self.name} [{self.rarity}]\n{self.description}\n(+{self.exp_bonus} EXP){Style.RESET_ALL}"

class Boss:
    def __init__(self, name: str, domain: str, level: int, attack: int, health: int, 
                 materials: List[Material], description: str):
        self.name = name
        self.domain = domain
        self.level = level
        self.attack = attack
        self.health = health
        self.max_health = health
        self.materials = materials
        self.description = description

    def __str__(self):
        hp_percent = (self.health / self.max_health) * 100
        return f"{Fore.RED}Boss: {self.name} [{self.domain}] Lv.{self.level}{Style.RESET_ALL}\n{self.description}\nHP: {self.health}/{self.max_health} ({hp_percent:.1f}%)\nAttack: {self.attack}"

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
        self.materials_inventory: Dict[str, int] = {}  # Store materials and their counts

    def gain_exp(self, amount: int, material: Material = None) -> bool:
        """Returns True if leveled up"""
        bonus_exp = 0
        if material:
            bonus_exp = material.exp_bonus
            print_slow(f"{Fore.GREEN}Material bonus: +{bonus_exp} EXP!{Style.RESET_ALL}")
        
        total_exp = amount + bonus_exp
        self.exp += total_exp
        
        if self.exp >= self.exp_to_level:
            self.level_up()
            return True
        return False

    def add_material(self, material: Material):
        if material.name not in self.materials_inventory:
            self.materials_inventory[material.name] = 0
        self.materials_inventory[material.name] += 1

    def use_material(self, material_name: str) -> bool:
        if material_name in self.materials_inventory and self.materials_inventory[material_name] > 0:
            self.materials_inventory[material_name] -= 1
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

def train_character(character: Character, coins_spent: int) -> int:
    """Train a character using coins. Returns exp gained."""
    exp_per_coin = 10
    exp_gained = coins_spent * exp_per_coin
    
    print_slow(f"\n{Fore.CYAN}Training {character.name}...{Style.RESET_ALL}")
    time.sleep(1)
    
    leveled_up = character.gain_exp(exp_gained)
    if leveled_up:
        print_slow(f"\n{Fore.YELLOW}Level Up! {character.name} is now level {character.level}!{Style.RESET_ALL}")
        print_slow(f"Attack increased to {character.attack}")
        print_slow(f"Health increased to {character.max_health}")
    
    return exp_gained

def get_difficulty_multiplier(player_level: int, difficulty: str) -> tuple[float, float, int]:
    """Returns (attack_mult, health_mult, exp_mult) based on difficulty"""
    base_multipliers = {
        "Normal": (0.8, 0.8, 1),    # Reduced from 1.0 to 0.8
        "Hard": (1.2, 1.2, 2),      # Reduced from 1.5 to 1.2
        "Expert": (1.5, 1.5, 3),    # Reduced from 2.0 to 1.5
        "Master": (1.8, 1.8, 4),    # Reduced from 2.5 to 1.8
        "Nightmare": (2.2, 2.2, 5)   # Reduced from 3.0 to 2.2
    }
    
    # Reduced level scaling from 10% to 5% per level
    level_scaling = max(1.0, 1.0 + (player_level - 1) * 0.05)
    attack_mult, health_mult, exp_mult = base_multipliers[difficulty]
    
    return (attack_mult * level_scaling, health_mult * level_scaling, exp_mult)

def create_boss_list(player_level: int, difficulty: str = "Normal") -> List[Boss]:
    # Reduced base stat scaling
    base_attack = 35 + (player_level * 10)  # Reduced from 40 + 15 to 35 + 10
    base_health = 120 + (player_level * 20)  # Reduced from 150 + 25 to 120 + 20
    
    # Get multipliers based on difficulty
    attack_mult, health_mult, exp_mult = get_difficulty_multiplier(player_level, difficulty)
    
    bosses = [
        # Dragon Domain
        Boss(
            "Dragon Emperor",
            "Dragon's Peak",
            player_level,
            int(base_attack * 1.8 * attack_mult),  # Reduced from 2.0
            int(base_health * 2.0 * health_mult),  # Reduced from 2.5
            [
                Material(
                    "Emperor's Dragon Scale",
                    "Mythical",
                    3000 * exp_mult,
                    "A scale from the Dragon Emperor himself. Grants immense power to any character."
                ),
                Material(
                    "Dragon's Breath Crystal",
                    "Legendary",
                    2000 * exp_mult,
                    "Crystallized dragon breath, pulsing with raw energy."
                )
            ],
            f"The mighty ruler of all dragons, commanding both fire and lightning. [{difficulty} Mode]"
        ),
        Boss(
            "Ancient Frost Dragon",
            "Dragon's Peak",
            player_level,
            int(base_attack * 1.5 * attack_mult),  # Reduced from 1.8
            int(base_health * 1.8 * health_mult),  # Reduced from 2.2
            [
                Material(
                    "Frost Dragon Core",
                    "Legendary",
                    2000 * exp_mult,
                    "The frozen core of an ancient dragon. Enhances a character's power significantly."
                )
            ],
            "A dragon as old as winter itself, its breath freezes all in its path."
        ),
        
        # Demon Domain
        Boss(
            "Demon Lord Malphas",
            "Demon Realm",
            player_level,
            int(base_attack * 2.0 * attack_mult),  # Reduced from 2.5
            int(base_health * 1.8 * health_mult),  # Reduced from 2.0
            [
                Material(
                    "Demon Lord's Crown",
                    "Mythical",
                    3000 * exp_mult,
                    "The crown of a demon lord, pulsing with dark energy. Grants tremendous power."
                ),
                Material(
                    "Corrupted Soul Crystal",
                    "Legendary",
                    2000 * exp_mult,
                    "A crystal containing corrupted souls, offering great power at no cost."
                )
            ],
            "The ruler of the demon realm, wielding dark magic and corruption."
        ),
        Boss(
            "Shadow Demon General",
            "Demon Realm",
            player_level,
            int(base_attack * 1.8 * attack_mult),  # Reduced from 2.2
            int(base_health * 1.5 * health_mult),  # Reduced from 1.8
            [
                Material(
                    "Shadow Essence",
                    "Legendary",
                    2000 * exp_mult,
                    "Pure shadow energy from a demon general. Greatly enhances character power."
                )
            ],
            "A general in the demon army, master of shadow warfare."
        ),
        
        # Ancient Ruins
        Boss(
            "Ancient Golem King",
            "Forgotten Ruins",
            player_level,
            int(base_attack * 1.3 * attack_mult),  # Reduced from 1.5
            int(base_health * 2.5 * health_mult),  # Reduced from 3.0
            [
                Material(
                    "Golem King's Core",
                    "Mythical",
                    3000 * exp_mult,
                    "The central core of the Golem King. Contains the wisdom and power of ancient civilizations."
                ),
                Material(
                    "Ancient Rune Stone",
                    "Legendary",
                    2000 * exp_mult,
                    "A stone inscribed with powerful runes from a lost civilization."
                )
            ],
            "The last guardian of an ancient civilization, powered by forgotten magic."
        ),
        Boss(
            "Cursed Guardian Statue",
            "Forgotten Ruins",
            player_level,
            int(base_attack * 1.5 * attack_mult),  # Reduced from 1.7
            int(base_health * 2.0 * health_mult),  # Reduced from 2.5
            [
                Material(
                    "Guardian's Blessing",
                    "Legendary",
                    2000 * exp_mult,
                    "A blessed stone from an ancient guardian. Greatly increases character potential."
                )
            ],
            "A cursed statue brought to life by ancient magic, protecting sacred treasures."
        ),
        
        # Celestial Realm
        Boss(
            "Fallen Seraph",
            "Celestial Realm",
            player_level,
            int(base_attack * 1.8 * attack_mult),  # Reduced from 2.3
            int(base_health * 1.8 * health_mult),  # Reduced from 2.3
            [
                Material(
                    "Seraph's Feather",
                    "Mythical",
                    3000 * exp_mult,
                    "A feather from a fallen seraph, containing divine power."
                ),
                Material(
                    "Divine Light Crystal",
                    "Legendary",
                    2000 * exp_mult,
                    "Crystallized divine light, capable of enhancing any character."
                )
            ],
            "A fallen angel who still wields tremendous celestial power."
        ),
        Boss(
            "Celestial Arbiter",
            "Celestial Realm",
            player_level,
            int(base_attack * 1.6 * attack_mult),  # Reduced from 2.0
            int(base_health * 1.6 * health_mult),  # Reduced from 2.0
            [
                Material(
                    "Celestial Judgment",
                    "Legendary",
                    2000 * exp_mult,
                    "The embodiment of celestial judgment, granting great power to the worthy."
                )
            ],
            "A divine judge who tests the worth of all who enter the celestial realm."
        )
    ]
    return bosses

def select_boss_menu(player_level: int) -> Boss:
    difficulties = ["Normal", "Hard", "Expert", "Master", "Nightmare"]
    available_difficulties = [d for d in difficulties if player_level >= difficulties.index(d) * 5]
    
    while True:
        print_slow(f"\n{Fore.CYAN}=== Choose Difficulty ==={Style.RESET_ALL}")
        print("\nAvailable difficulties (based on your level):")
        for i, diff in enumerate(available_difficulties, 1):
            color = Fore.GREEN if diff == "Normal" else \
                    Fore.YELLOW if diff == "Hard" else \
                    Fore.MAGENTA if diff == "Expert" else \
                    Fore.RED if diff == "Master" else \
                    Fore.RED + Style.BRIGHT
            
            # Show rewards multiplier
            _, _, exp_mult = get_difficulty_multiplier(player_level, diff)
            print(f"{i}. {color}{diff}{Style.RESET_ALL} (Rewards x{exp_mult})")
        
        try:
            diff_choice = int(input("\nSelect difficulty (0 to cancel): ")) - 1
            if diff_choice == -1:
                return None
            if 0 <= diff_choice < len(available_difficulties):
                selected_difficulty = available_difficulties[diff_choice]
                
                # Get bosses for selected difficulty
                bosses = create_boss_list(player_level, selected_difficulty)
                domains = sorted(list(set(boss.domain for boss in bosses)))
                
                print_slow(f"\n{Fore.CYAN}=== Choose a Domain ==={Style.RESET_ALL}")
                for i, domain in enumerate(domains, 1):
                    print(f"{i}. {domain}")
                
                domain_choice = int(input("\nSelect a domain (0 to go back): ")) - 1
                if domain_choice == -1:
                    continue
                if 0 <= domain_choice < len(domains):
                    selected_domain = domains[domain_choice]
                    domain_bosses = [b for b in bosses if b.domain == selected_domain]
                    
                    print_slow(f"\n{Fore.CYAN}=== {selected_domain} Bosses ==={Style.RESET_ALL}")
                    print(f"\nDifficulty: {selected_difficulty}")
                    for i, boss in enumerate(domain_bosses, 1):
                        print(f"\n{i}. {boss.name}")
                        print(f"   {boss.description}")
                        print(f"   Level: {boss.level}")
                        print(f"   Attack: {boss.attack}")
                        print(f"   Health: {boss.health}")
                        print("\nDrops:")
                        for material in boss.materials:
                            print(f"• {material.name} [{material.rarity}] (+{material.exp_bonus} EXP)")
                    
                    boss_choice = int(input("\nSelect a boss (0 to go back): ")) - 1
                    if boss_choice == -1:
                        continue
                    if 0 <= boss_choice < len(domain_bosses):
                        return domain_bosses[boss_choice]
            print_slow(f"\n{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        except ValueError:
            print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")

def battle_boss(character: Character, boss: Boss) -> bool:
    print_slow(f"\n{Fore.RED}=== BOSS BATTLE START ==={Style.RESET_ALL}")
    print(boss)
    print(f"\nYour character: {character.name} Lv.{character.level}")
    print(f"Attack: {character.attack}")
    print(f"Health: {character.health}/{character.max_health}")
    
    character_hp = character.max_health
    
    while True:
        # Player turn
        crit_chance = min(35, 10 + character.level)  # Increased base crit chance from 5 to 10
        is_crit = random.randint(1, 100) <= crit_chance
        
        base_damage = random.randint(character.attack - 5, character.attack + 12)  # Increased max damage bonus from 10 to 12
        damage = int(base_damage * 1.8) if is_crit else base_damage  # Increased crit multiplier from 1.5 to 1.8
        
        boss.health -= damage
        if is_crit:
            print_slow(f"\n{Fore.YELLOW}CRITICAL HIT!{Style.RESET_ALL}")
        print_slow(f"\n{Fore.GREEN}Your {character.name} deals {damage} damage to {boss.name}!{Style.RESET_ALL}")
        print(f"Boss HP: {boss.health}/{boss.max_health}")
        
        if boss.health <= 0:
            return True
            
        time.sleep(1)
        
        # Boss turn
        boss_crit_chance = 8  # Reduced from 10
        is_boss_crit = random.randint(1, 100) <= boss_crit_chance
        
        base_damage = random.randint(boss.attack - 12, boss.attack + 12)  # More predictable boss damage
        damage = int(base_damage * 1.4) if is_boss_crit else base_damage  # Reduced boss crit multiplier from 1.5 to 1.4
        
        character_hp -= damage
        if is_boss_crit:
            print_slow(f"\n{Fore.RED}BOSS CRITICAL HIT!{Style.RESET_ALL}")
        print_slow(f"\n{Fore.RED}{boss.name} deals {damage} massive damage!{Style.RESET_ALL}")
        print(f"Your HP: {character_hp}/{character.max_health}")
        
        if character_hp <= 0:
            return False
            
        time.sleep(1)

def display_materials(character: Character):
    if not character.materials_inventory:
        print_slow(f"\n{Fore.YELLOW}No materials in inventory!{Style.RESET_ALL}")
        return
    
    print_slow(f"\n{Fore.CYAN}=== Materials Inventory ==={Style.RESET_ALL}")
    for material_name, count in character.materials_inventory.items():
        print(f"{material_name}: {count}")

def use_material_menu(character: Character):
    if not character.materials_inventory:
        print_slow(f"\n{Fore.RED}No materials available!{Style.RESET_ALL}")
        return
    
    print_slow(f"\n{Fore.CYAN}=== Use Materials ==={Style.RESET_ALL}")
    print("Available materials:")
    
    materials_list = []
    for material_name, count in character.materials_inventory.items():
        if count > 0:
            materials_list.append(material_name)
            print(f"{len(materials_list)}. {material_name} (x{count})")
    
    if not materials_list:
        print_slow(f"\n{Fore.RED}No materials available!{Style.RESET_ALL}")
        return
    
    try:
        choice = int(input("\nSelect material to use (0 to cancel): ")) - 1
        if 0 <= choice < len(materials_list):
            material_name = materials_list[choice]
            # Find material properties
            material_props = {
                "Dragon Scale": ("Epic", 1000),
                "Dragon Heart": ("Legendary", 2000),
                "Dragon Fang": ("Rare", 500),
                "Ancient Core": ("Epic", 800),
                "Mystic Stone": ("Rare", 400),
                "Golem Dust": ("Common", 200),
                "Demon Crystal": ("Legendary", 1500),
                "Dark Essence": ("Epic", 700),
                "Demon Horn": ("Rare", 300)
            }
            
            if material_name in material_props:
                rarity, exp_bonus = material_props[material_name]
                material = Material(material_name, rarity, exp_bonus, "")
                if character.use_material(material_name):
                    character.gain_exp(0, material)  # Apply material bonus
                    print_slow(f"\n{Fore.GREEN}Successfully used {material_name}!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Failed to use material!{Style.RESET_ALL}")
    except ValueError:
        print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")

def play_game():
    display_title()
    print_slow(Fore.YELLOW + "Welcome to Gacha Fantasy World!" + Style.RESET_ALL)
    time.sleep(1)
    
    player_name = input(Fore.GREEN + "\nWhat is your name, Summoner? " + Style.RESET_ALL)
    print_slow(f"\nWelcome, {Fore.CYAN}{player_name}{Style.RESET_ALL}! Your gacha adventure begins...")
    
    game = GachaGame()
    gems = 1000
    coins = 2000  # Starting coins for training
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
        print(f"\n{Fore.CYAN}Gems: {gems} | Coins: {coins}{Style.RESET_ALL}")
        print(Fore.MAGENTA + """
1. Summon Character (100 gems)
2. View Characters
3. Battle
4. Train Character
5. Daily Quest
6. Boss Battle
7. View/Use Materials
8. Quit Game
        """ + Style.RESET_ALL)
        
        choice = input("Enter your choice (1-8): ")
        
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
                    won = battle_boss(characters[char_choice], enemy)
                    
                    if won:
                        gem_reward = random.randint(50, 150)
                        coin_reward = random.randint(100, 300)  # Add coin rewards
                        gems += gem_reward
                        coins += coin_reward
                        print_slow(f"\n{Fore.GREEN}Victory! You earned {gem_reward} gems and {coin_reward} coins!{Style.RESET_ALL}")
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
                    print(f"\nYou have {coins} coins.")
                    print("Training costs: 50 coins = 500 EXP")
                    coins_to_spend = int(input("How many coins do you want to spend on training? "))
                    
                    if coins_to_spend <= coins and coins_to_spend >= 0:
                        coins -= coins_to_spend
                        exp_gained = train_character(characters[char_choice], coins_to_spend)
                        print_slow(f"\n{Fore.GREEN}Training complete! Gained {exp_gained} EXP!{Style.RESET_ALL}")
                    else:
                        print_slow(f"\n{Fore.RED}Not enough coins or invalid amount!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Invalid character number!{Style.RESET_ALL}")
            except ValueError:
                print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")
                
        elif choice == '5':
            # Daily quest - simple battle with guaranteed reward
            gem_reward = random.randint(80, 120)
            coin_reward = random.randint(150, 250)  # Add coin rewards to daily quest
            gems += gem_reward
            coins += coin_reward
            print_slow(f"\n{Fore.GREEN}Daily Quest completed! You earned {gem_reward} gems and {coin_reward} coins!{Style.RESET_ALL}")
            
        elif choice == '6':
            if not characters:
                print_slow(f"\n{Fore.RED}You need characters to battle bosses!{Style.RESET_ALL}")
                continue
            
            print_slow(f"\n{Fore.CYAN}Select your character for boss battle:{Style.RESET_ALL}")
            for i, char in enumerate(characters, 1):
                print(f"\n{i}. ", end="")
                display_character(char)
            
            try:
                char_choice = int(input("\nEnter character number: ")) - 1
                if 0 <= char_choice < len(characters):
                    boss = select_boss_menu(characters[char_choice].level)
                    if boss is None:
                        continue
                    
                    print_slow(f"\n{Fore.RED}Challenging {boss.name} in {boss.domain}!{Style.RESET_ALL}")
                    time.sleep(1)
                    
                    won = battle_boss(characters[char_choice], boss)
                    if won:
                        # Award materials
                        material_count = random.randint(1, len(boss.materials))
                        awarded_materials = random.sample(boss.materials, material_count)
                        
                        print_slow(f"\n{Fore.GREEN}Victory against {boss.name}!{Style.RESET_ALL}")
                        print_slow("\nReceived materials:")
                        for material in awarded_materials:
                            characters[char_choice].add_material(material)
                            print(f"• {material}")
                        
                        # Award extra rewards
                        gem_reward = random.randint(100, 300)
                        coin_reward = random.randint(200, 500)
                        gems += gem_reward
                        coins += coin_reward
                        print_slow(f"\n{Fore.GREEN}Also received {gem_reward} gems and {coin_reward} coins!{Style.RESET_ALL}")
                    else:
                        print_slow(f"\n{Fore.RED}Defeated by {boss.name}! Better luck next time!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Invalid character number!{Style.RESET_ALL}")
            except ValueError:
                print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")

        elif choice == '7':
            if not characters:
                print_slow(f"\n{Fore.RED}You need characters to view/use materials!{Style.RESET_ALL}")
                continue
            
            print_slow(f"\n{Fore.CYAN}Select character to view/use materials:{Style.RESET_ALL}")
            for i, char in enumerate(characters, 1):
                print(f"\n{i}. ", end="")
                display_character(char)
            
            try:
                char_choice = int(input("\nEnter character number: ")) - 1
                if 0 <= char_choice < len(characters):
                    print(Fore.MAGENTA + """
1. View Materials
2. Use Material
                    """ + Style.RESET_ALL)
                    
                    mat_choice = input("Enter your choice (1-2): ")
                    if mat_choice == '1':
                        display_materials(characters[char_choice])
                    elif mat_choice == '2':
                        use_material_menu(characters[char_choice])
                    else:
                        print_slow(f"\n{Fore.RED}Invalid choice!{Style.RESET_ALL}")
                else:
                    print_slow(f"\n{Fore.RED}Invalid character number!{Style.RESET_ALL}")
            except ValueError:
                print_slow(f"\n{Fore.RED}Invalid input!{Style.RESET_ALL}")
                
        elif choice == '8':
            print_slow(f"\n{Fore.YELLOW}Thanks for playing, {player_name}! Farewell!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    play_game() 