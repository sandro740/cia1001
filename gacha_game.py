import random
import time
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

class Character:
    def __init__(self, name, rarity, is_special=False):
        self.name = name
        self.rarity = rarity
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        # Base stats are influenced by rarity
        rarity_multiplier = {
            'N': 1,
            'R': 1.2,
            'SR': 1.5,
            'SSR': 2,
            'LR': 3,
            'MYTHIC': 10  # New special rarity for OP character
        }
        
        if is_special:  # Special stats for starter character
            self.base_attack = 500  # Extremely high base attack
            self.base_hp = 2000     # Extremely high base HP
        else:
            self.base_attack = int(20 * rarity_multiplier[rarity])
            self.base_hp = int(100 * rarity_multiplier[rarity])
        
    def get_stats(self):
        # Stats increase with level
        level_multiplier = 1 + (self.level - 1) * 0.1
        return {
            'attack': int(self.base_attack * level_multiplier),
            'hp': int(self.base_hp * level_multiplier)
        }
        
    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.exp -= self.exp_to_next_level
        self.level += 1
        self.exp_to_next_level = int(self.exp_to_next_level * 1.2)  # Each level requires more exp
        stats = self.get_stats()
        print(f"{Fore.GREEN}🎉 {self.name} leveled up to level {self.level}!")
        print(f"New stats - Attack: {stats['attack']}, HP: {stats['hp']}{Style.RESET_ALL}")
        
    def __str__(self):
        color = {
            'N': Fore.WHITE,
            'R': Fore.BLUE,
            'SR': Fore.MAGENTA,
            'SSR': Fore.YELLOW,
            'LR': Fore.RED,
            'MYTHIC': Fore.LIGHTCYAN_EX  # Special color for MYTHIC rarity
        }
        stats = self.get_stats()
        return f"{color[self.rarity]}{self.name} [{self.rarity}] Lv.{self.level} (EXP: {self.exp}/{self.exp_to_next_level}) ATK:{stats['attack']} HP:{stats['hp']}{Style.RESET_ALL}"

class Enemy:
    def __init__(self, level):
        self.level = level
        self.name = random.choice(["Slime", "Goblin", "Wolf", "Orc", "Dragon"])
        self.attack = int(15 * (1 + (level - 1) * 0.1))
        self.hp = int(80 * (1 + (level - 1) * 0.1))
        self.max_hp = self.hp
        
    def __str__(self):
        hp_percent = (self.hp / self.max_hp) * 100
        return f"{self.name} Lv.{self.level} (HP: {self.hp}/{self.max_hp} - {hp_percent:.1f}%) ATK:{self.attack}"

class GachaGame:
    def __init__(self):
        self.characters = []
        self.player_gems = 1000
        self.summon_cost = 100
        self.inventory = []
        self.selected_character = None
        
        # Initialize character pool
        self.initialize_characters()
        
        # Add special starter character
        starter_char = Character("The Chosen One", "MYTHIC", is_special=True)
        self.inventory.append(starter_char)
        self.selected_character = starter_char  # Auto-select the starter character
        print(f"\n{Fore.LIGHTCYAN_EX}✨ Special Character Unlocked: {starter_char}{Style.RESET_ALL}")
        
    def initialize_characters(self):
        # Normal Characters (N)
        normal_chars = ["Warrior", "Archer", "Mage", "Knight", "Thief"]
        for char in normal_chars:
            self.characters.append(Character(char, "N"))
            
        # Rare Characters (R)
        rare_chars = ["Fire Mage", "Ice Knight", "Thunder Archer", "Dark Warrior", "Light Priest"]
        for char in rare_chars:
            self.characters.append(Character(char, "R"))
            
        # Super Rare Characters (SR)
        sr_chars = ["Dragon Knight", "Phoenix Mage", "Shadow Assassin", "Holy Paladin"]
        for char in sr_chars:
            self.characters.append(Character(char, "SR"))
            
        # Super Super Rare Characters (SSR)
        ssr_chars = ["Celestial Guardian", "Demon Lord", "Ancient Dragon"]
        for char in ssr_chars:
            self.characters.append(Character(char, "SSR"))
            
        # Legendary Rare Characters (LR)
        lr_chars = ["Divine Emperor", "Chaos God"]
        for char in lr_chars:
            self.characters.append(Character(char, "LR"))
    
    def get_summon_rates(self):
        return {
            "N": 50,    # 50% chance
            "R": 30,    # 30% chance
            "SR": 15,   # 15% chance
            "SSR": 4,   # 4% chance
            "LR": 1     # 1% chance
        }
    
    def summon(self):
        if self.player_gems < self.summon_cost:
            print(f"{Fore.RED}Not enough gems! You need {self.summon_cost} gems to summon.{Style.RESET_ALL}")
            return None
            
        self.player_gems -= self.summon_cost
        rates = self.get_summon_rates()
        rarity = random.choices(
            list(rates.keys()),
            weights=list(rates.values()),
            k=1
        )[0]
        
        possible_chars = [char for char in self.characters if char.rarity == rarity]
        summoned_char = random.choice(possible_chars)
        new_char = Character(summoned_char.name, summoned_char.rarity)
        self.inventory.append(new_char)
        return new_char
    
    def multi_summon(self, count=10):
        if self.player_gems < self.summon_cost * count:
            print(f"{Fore.RED}Not enough gems! You need {self.summon_cost * count} gems for {count} summons.{Style.RESET_ALL}")
            return []
            
        results = []
        for _ in range(count):
            result = self.summon()
            if result:
                results.append(result)
        return results
    
    def show_inventory(self):
        if not self.inventory:
            print(f"{Fore.YELLOW}Your inventory is empty!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}=== Your Inventory ==={Style.RESET_ALL}")
        for i, char in enumerate(self.inventory, 1):
            prefix = "➤" if char == self.selected_character else " "
            print(f"{prefix} {i}. {char}")
            
    def select_character(self):
        self.show_inventory()
        if not self.inventory:
            return False
            
        while True:
            try:
                choice = int(input("\nSelect a character number (0 to cancel): "))
                if choice == 0:
                    return False
                if 1 <= choice <= len(self.inventory):
                    self.selected_character = self.inventory[choice - 1]
                    print(f"\n{Fore.GREEN}Selected: {self.selected_character}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")
                
    def battle(self):
        if not self.selected_character:
            print(f"{Fore.RED}No character selected! Please select a character first.{Style.RESET_ALL}")
            return
            
        # Create an enemy with level close to player's level
        level_range = max(1, self.selected_character.level - 2), self.selected_character.level + 2
        enemy_level = random.randint(*level_range)
        enemy = Enemy(enemy_level)
        
        print(f"\n{Fore.YELLOW}=== Battle Start ==={Style.RESET_ALL}")
        print(f"Your character: {self.selected_character}")
        print(f"Enemy: {enemy}")
        
        char_stats = self.selected_character.get_stats()
        char_hp = char_stats['hp']
        
        while True:
            # Player turn
            damage = char_stats['attack']
            enemy.hp -= damage
            print(f"\n{Fore.CYAN}Your {self.selected_character.name} attacks for {damage} damage!{Style.RESET_ALL}")
            print(f"Enemy {enemy}")
            
            if enemy.hp <= 0:
                exp_gain = int(50 * (1 + (enemy_level - 1) * 0.2))
                gems_gain = int(10 * (1 + (enemy_level - 1) * 0.1))
                print(f"\n{Fore.GREEN}Victory! Gained {exp_gain} EXP and {gems_gain} gems!{Style.RESET_ALL}")
                self.selected_character.gain_exp(exp_gain)
                self.player_gems += gems_gain
                break
                
            time.sleep(1)
            
            # Enemy turn
            char_hp -= enemy.attack
            print(f"\n{Fore.RED}{enemy.name} attacks for {enemy.attack} damage!{Style.RESET_ALL}")
            print(f"Your HP: {char_hp}/{char_stats['hp']}")
            
            if char_hp <= 0:
                exp_gain = int(20 * (1 + (enemy_level - 1) * 0.2))
                print(f"\n{Fore.RED}Defeat! Gained {exp_gain} EXP for trying.{Style.RESET_ALL}")
                self.selected_character.gain_exp(exp_gain)
                break
                
            time.sleep(1)

def main():
    print(f"{Fore.CYAN}Welcome to Python Gacha Game!{Style.RESET_ALL}")
    game = GachaGame()
    
    while True:
        print(f"\n{Fore.YELLOW}Your Gems: {game.player_gems}{Style.RESET_ALL}")
        if game.selected_character:
            print(f"Selected Character: {game.selected_character}")
            
        print("\nWhat would you like to do?")
        print("1. Single Summon (100 gems)")
        print("2. Multi Summon - 10x (1000 gems)")
        print("3. View/Select Character")
        print("4. Battle")
        print("5. View Summon Rates")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            print("\n=== Single Summon ===")
            result = game.summon()
            if result:
                print(f"\nYou summoned: {result}")
                time.sleep(1)
                
        elif choice == "2":
            print("\n=== Multi Summon ===")
            results = game.multi_summon()
            if results:
                print("\nYou summoned:")
                for char in results:
                    print(f"• {char}")
                    time.sleep(0.5)
                    
        elif choice == "3":
            game.select_character()
            
        elif choice == "4":
            game.battle()
            
        elif choice == "5":
            rates = game.get_summon_rates()
            print(f"\n{Fore.CYAN}=== Summon Rates ==={Style.RESET_ALL}")
            for rarity, rate in rates.items():
                print(f"{rarity}: {rate}%")
                
        elif choice == "6":
            print(f"\n{Fore.CYAN}Thanks for playing! Goodbye!{Style.RESET_ALL}")
            break
            
        else:
            print(f"{Fore.RED}Invalid choice! Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 