# Python Gacha Game

A simple command-line gacha game implemented in Python where you can summon characters of different rarities, level them up through battles, and make them stronger!

## Features

- 5 different character rarities: N (Normal), R (Rare), SR (Super Rare), SSR (Super Super Rare), and LR (Legendary Rare)
- Colored output for better visualization
- Single and Multi-summon options
- Inventory system
- Currency system (Gems)
- Level up system with experience points
- Battle system with enemies
- Character stats that increase with levels
- Rarity-based stat multipliers

## Character Stats

Each character has:
- Level (starts at 1)
- Experience points
- Attack (increases with level)
- HP (increases with level)
- Rarity multipliers:
  - N: x1.0
  - R: x1.2
  - SR: x1.5
  - SSR: x2.0
  - LR: x3.0

## Battle System

- Select a character to battle with
- Fight enemies near your character's level
- Gain experience points and gems from victories
- Even get some experience points from defeats
- Characters get stronger as they level up
- Higher rarity characters have better base stats

## Rarity Rates

- N: 50% chance
- R: 30% chance
- SR: 15% chance
- SSR: 4% chance
- LR: 1% chance

## Requirements

- Python 3.6 or higher
- colorama package

## Installation

1. Install the required package:
```bash
pip install -r requirements.txt
```

## How to Run

```bash
python gacha_game.py
```

## Game Instructions

1. You start with 1000 gems
2. Each summon costs 100 gems
3. You can choose between:
   - Single Summon (100 gems)
   - Multi Summon (1000 gems for 10 summons)
4. View and select characters from your inventory
5. Battle with your selected character to gain experience and gems
6. Level up your characters to make them stronger
7. Check the summon rates to see your chances

Enjoy the game and good luck getting those LR characters!