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
- **Coin & Boost System:** Collect coins to activate a temporary boost. While active, you fire multiple bullets and earn double points.
- **Boss Fight:** A climactic battle against "The Scientist" featuring a telegraphing lunge-and-slash attack pattern.
- **Platforming Physics:** Includes gravity, "Coyote Time" (allowing jumps shortly after leaving a ledge), and jump buffering for responsive controls.

## ⌨️ Controls
- **Movement:** `WASD` or Arrow Keys (`←` / `→` / `W` to Jump)
- **Shoot:** `Spacebar` (Bullet direction depends on facing side)
- **Menu Navigation:** `W`/`S` to select, `A`/`D` to adjust settings, `Enter`/`Space` to confirm.
- **Skip Slides/Menus:** `ESC`
- **Progress Slides:** `Enter`, `Space`, or Mouse Click.

## 🏆 Gamification Elements
The game implements the six core ingredients of gamification:
1. **Points:** Earned for kills, wave completion, and boss defeat. Includes a `2x` multiplier during boosts.
2. **Badges:** Progress through levels (Bronze to Ace) and earn special titles like *Zombie Hunter* (50 kills), *Survivor* (Wave 3 clear), and *Legend* (Boss defeat).
3. **Leaderboard:** Local persistence system tracking the Top 5 scores in `score.txt`.
4. **Challenges:** Bonus rewards for "Flawless Waves" (no damage taken) and specific targets like "20 Kills in Wave 1".
5. **Feedback Loops:** 
   - **Immediate:** Hit-flash effects, health bars, screen overlays, and on-screen "Toasts" for achievements.
   - **Delayed:** A comprehensive post-game feedback system that analyzes your playstyle (e.g., Accuracy, Efficiency).
6. **Narrative:** Cinematic intro and outro slideshows that frame the mission.

## 🛠️ Technical Details
- **Fullscreen Mode:** Uses `pygame.SCALED` for a crisp, aspect-ratio-correct fullscreen experience.
- **Chroma Key Transparency:** Since the game uses JPGs for creatures, the `load_creature_jpg` function implements a manual chroma key by sampling the pixel at `(0,0)` to create transparency.
- **Slide System:** A robust narrative sequence handler with auto-progression and manual overrides.
- **Collision System:** A custom vertical resolver handles interactions between the player, the ground, and floating platforms.
- **Settings Menu:** In-game controls for Master Volume (Music/SFX) and Screen Brightness.

## 📂 Asset Structure
To run correctly, the game expects the following directory structure:
```text
game/
├── main.py
├── score.txt
├── Images/
│   ├── survivor.png
│   ├── zombie.jpg
│   ├── coin.png
│   └── bronze.png, silver.png, etc.
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