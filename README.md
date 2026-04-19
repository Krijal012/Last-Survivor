# Virus: Last Survivor

A 2D side-scrolling action-platformer developed in Pygame. Navigate through a world ravaged by a rogue scientist's virus, eliminate the infected across multiple waves, and recover the cure in a final boss encounter.

## 📖 Story
A rogue scientist created a virus to "upgrade" humanity, but it escaped containment. As the last survivor soldier, you are sent into the dead zone to eliminate 100 infected individuals and take down the Scientist Boss to retrieve the cure.

## 🎮 Gameplay Mechanics
- **Waves:** 5 distinct waves with increasing difficulty and changing enemy compositions.
- **Enemy Types:**
  - **Normal:** Standard speed and health.
  - **Fast:** High movement speed, low health.
  - **Tank:** Slow movement, significantly higher health.
- **Boss Fight:** A climactic battle against "The Scientist" featuring a telegraphing lunge-and-slash attack pattern.
- **Platforming Physics:** Includes gravity, "Coyote Time" (allowing jumps shortly after leaving a ledge), and jump buffering for responsive controls.

## ⌨️ Controls
- **Move Left/Right:** Arrow Keys (← / →)
- **Jump:** `W`
- **Shoot:** `Spacebar` (Bullet direction depends on the side the player is facing)
- **Skip Slides/Menus:** `ESC`
- **Progress Slides/Start:** `Enter` or `Space`

## 🏆 Gamification Elements
- **Score System:** Points awarded for kills, wave completion, and defeating the boss.
- **Leaderboard:** Persistence system tracking the Top 5 scores in `score.txt`.
- **Badges:** Earn specific titles like *Zombie Hunter* (50 kills), *Survivor* (Wave 3 clear), and *Legend* (Boss defeat).
- **Challenges:** Bonus rewards for "Flawless Waves" (no damage taken) and specific kill targets.
- **Visual Feedback:** XP bars, health bars, hit-flash effects on enemies, and on-screen "Toasts" for achievements.

## 🛠️ Technical Details
- **Chroma Key Transparency:** Since the game uses JPGs for creatures, the `load_creature_jpg` function implements a manual chroma key by sampling the pixel at `(0,0)` to create transparency.
- **Slide System:** A robust `run_slideshow` function handles both the intro and outro narrative sequences with automatic and manual progression.
- **Collision System:** A custom vertical resolver handles interactions between the player, the ground, and floating platforms.

## 📂 Asset Structure
To run correctly, the game expects the following directory structure:
```text
game/
├── main.py
├── constants.py
├── score.txt
├── Images/
│   ├── survivor.png
│   └── zombie.jpg
├── assets/
│   └── bg.png
├── Sounds/
│   ├── gunshot.wav
│   ├── hit.wav
│   ├── backgroundMusic.wav
│   └── ... (other SFX)
└── Lab.png, Breach.jpg, etc. (Story Slides)
```

## 🚀 Getting Started
1. Ensure Python 3.x and Pygame are installed:
   ```bash
   pip install pygame
   ```
2. Run the game:
   ```bash
   python main.py
   ```