
import math
import os
import random
import sys

import pygame

pygame.init()
pygame.mixer.init(frequency=44100, channels=2, buffer=512)

# =============================
# PATHS & WINDOW
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Virus: Last Survivor")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 26)
big_font = pygame.font.SysFont("arial", 54)
story_font = pygame.font.SysFont("arial", 23)
story_hint_font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 20)

# =============================
# COLORS
# =============================
WHITE = (255, 255, 255)
RED = (220, 40, 40)
GREEN = (60, 200, 90)
YELLOW = (255, 230, 80)
BLACK = (0, 0, 0)
SKY = (120, 185, 230)
GRASS_TOP = (72, 140, 62)
GRASS_DARK = (45, 95, 42)
STONE = (110, 105, 100)
STONE_EDGE = (70, 68, 65)
UI_BG = (20, 24, 30)
BAR_BACK = (40, 44, 52)
BAR_HP = (220, 70, 70)
BAR_HP_OK = (80, 200, 120)
BOSS_BAR = (200, 60, 200)
SLASH_COLOR = (255, 90, 40, 200)
XP_BAR = (90, 160, 255)
TOAST_BG = (30, 35, 50)

# Scoring & persistence
SCORE_FILE = os.path.join(BASE_DIR, "score.txt")
POINTS_PER_KILL = 10
POINTS_PER_WAVE = 50
POINTS_BOSS_DEFEAT = 200
POINTS_FLAWLESS_WAVE = 25
MISSION_ZOMBIES = 100
WAVE_ZOMBIE_COUNT = 20
MAX_ZOMBIES_ALIVE = 14

ZOMBIE_SPECS = {
    "normal": {"w": 55, "h": 65, "hp": 1, "speed": 2.0},
    "fast": {"w": 52, "h": 62, "hp": 1, "speed": 3.35},
    "tank": {"w": 68, "h": 76, "hp": 3, "speed": 1.1},
}

# spawn_every = frames between spawns (lower = faster)
WAVE_CONFIG = [
    {"spawn_every": 48, "weights": [("normal", 1.0)]},
    {"spawn_every": 36, "weights": [("normal", 0.5), ("fast", 0.5)]},
    {"spawn_every": 34, "weights": [("normal", 0.35), ("fast", 0.35), ("tank", 0.3)]},
    {"spawn_every": 22, "weights": [("normal", 0.25), ("fast", 0.45), ("tank", 0.3)]},
    {"spawn_every": 18, "weights": [("fast", 0.4), ("tank", 0.35), ("normal", 0.25)]},
]

# Story cutscenes (image files in BASE_DIR: Lab.png, Breach.jpg, etc.)
SLIDE_AUTO_MS = 8500

INTRO_SLIDES = [
    {
        "stem": "Lab",
        "lines": [
            "A rogue scientist forged a virus to 'upgrade humanity'.",
            "In secret labs, evolution was rewritten—until it broke free.",
        ],
    },
    {
        "stem": "Breach",
        "lines": [
            "Containment shattered. The pathogen flooded the streets.",
            "No vaccine could outrun what had already escaped.",
        ],
    },
    {
        "stem": "News",
        "lines": [
            "The world watched the collapse in real time.",
            "Truth, panic, and infection spread together.",
        ],
    },
    {
        "stem": "Collapsed",
        "lines": [
            "Cities fell silent. The infected rose everywhere.",
            "Civilization unraveled under a green-gray sky.",
        ],
    },
    {
        "stem": "SurvivorBrief",
        "lines": [
            "You are the last trained survivor soldier.",
            "Command sends you into the dead zone—alone, armed, unstoppable.",
        ],
    },
    {
        "stem": "Threshold",
        "lines": [
            "Mission: eliminate 100 infected across five waves.",
            "End the Scientist Boss. Recover the cure. Save what remains of us.",
        ],
    },
]

OUTRO_SLIDES = [
    {
        "stem": "Aftermath",
        "lines": [
            "The Scientist’s final mutation crashes to the floor.",
            "The mind behind the plague is gone—silenced forever.",
        ],
    },
    {
        "stem": "Cure",
        "lines": [
            "The cure is synthesized. Stable. Real. Humanity’s second chance.",
            "The virus dies with its maker.",
        ],
    },
    {
        "stem": "Helicopter",
        "lines": [
            "Extraction arrives. The infected zone is sealed behind you.",
            "The world can heal—because you finished the mission.",
        ],
    },
    {
        "stem": "End",
        "lines": [
            "Virus: Last Survivor — mission complete. The world is saved.",
            "Press ENTER when you are ready for the menu.",
        ],
    },
]


def load_png(path, size):
    if not os.path.isfile(path):
        # Create a colored placeholder if file is missing
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((200, 200, 200))
        return surf
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


def load_creature_jpg(path, size):
    """Remove flat backdrop via corner chroma key (looks transparent in-game)."""
    if not os.path.isfile(path):
        # Create a colored placeholder if file is missing
        surf = pygame.Surface(size)
        surf.fill((100, 100, 100))
        return surf
    img = pygame.image.load(path).convert()
    key = img.get_at((0, 0))
    img.set_colorkey(key, pygame.RLEACCEL)
    return pygame.transform.scale(img, size)


PLAYER_W, PLAYER_H = 60, 70
ZOMBIE_W, ZOMBIE_H = 55, 65
BOSS_W, BOSS_H = 160, 185
_p_path = os.path.join(BASE_DIR, "Images", "survivor.png")
if not os.path.isfile(_p_path): _p_path = os.path.join(BASE_DIR, "survivor.png")
player_img_right = load_png(_p_path, (PLAYER_W, PLAYER_H))
player_img_left = pygame.transform.flip(player_img_right, True, False)

_z_path = os.path.join(BASE_DIR, "Images", "zombie.jpg")
if not os.path.isfile(_z_path): _z_path = os.path.join(BASE_DIR, "zombie.jpg")
zombie_img_right = load_creature_jpg(_z_path, (ZOMBIE_W, ZOMBIE_H))
zombie_img_left = pygame.transform.flip(zombie_img_right, True, False)

boss_img_right = load_creature_jpg(_z_path, (BOSS_W, BOSS_H))
boss_img_left = pygame.transform.flip(boss_img_right, True, False)

# =============================
# MAP
# =============================
ground = pygame.Rect(0, 550, 1000, 50)
platforms = []

# =============================
# TUNING
# =============================
MAX_HEALTH = 5
MAX_BOSS_HP = 30
PLAYER_SPEED = 5.2
GRAVITY = 0.62
JUMP_VEL = -14.2
JUMP_CUT = -5.5
MAX_FALL = 16.0
COYOTE_FRAMES = 8
JUMP_BUFFER_FRAMES = 10
BULLET_SPEED = 12
BOSS_CHASE_SPEED = 2.8
BOSS_ATTACK_RANGE = 95
BOSS_ATTACK_COOLDOWN = 75
BOSS_ATTACK_DURATION = 32
BOSS_LUNGE = 20

MUSIC_VOL = 0.32
SFX_VOL = 0.55
GLOBAL_BRIGHTNESS = 1.0
ALL_SFX = []


def _load_sound(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(path):
        return None
    s = pygame.mixer.Sound(path)
    s.set_volume(SFX_VOL)
    ALL_SFX.append(s)
    return s

def update_sfx_volumes():
    for s in ALL_SFX:
        s.set_volume(SFX_VOL)

sfx_gunshot = _load_sound("Sounds/gunshot.wav")
sfx_hit = _load_sound("Sounds/hit.wav")
sfx_jump = _load_sound("Sounds/jump.wav")
sfx_player_hurt = _load_sound("Sounds/PlayerHurt.wav")
sfx_game_over = _load_sound("Sounds/GameOver.wav")
sfx_zombie_roar = _load_sound("Sounds/ZombieRoar.wav")
sfx_boss_death = _load_sound("Sounds/ZombieBossDeath.wav")
sfx_click = _load_sound("Sounds/MenuClick.wav")

# Define specific music paths
MENU_MUSIC_PATH = os.path.join(BASE_DIR, "Sounds/IndustrialDarkAmbient.wav")
# Fallback for menu music
if not os.path.isfile(MENU_MUSIC_PATH):
    MENU_MUSIC_PATH = os.path.join(BASE_DIR, "Sounds/IndustrialDarkAAmbient.wav") # Corrected typo from previous
if not os.path.isfile(MENU_MUSIC_PATH):
    MENU_MUSIC_PATH = os.path.join(BASE_DIR, "Sounds/Industrial Dark Ambient.wav")

GAME_MUSIC_PATH = os.path.join(BASE_DIR, "Sounds/backgroundMusic.wav")
# No fallback for game music, assume it exists or game will be silent.


def _play_sfx(sound):
    if sound is not None:
        sound.play()

def _play_music(music_file_path):
    """Loads and plays the specified music file on a loop."""
    if not os.path.isfile(music_file_path):
        print(f"Warning: Music file not found: {music_file_path}")
        return
    pygame.mixer.music.load(music_file_path)
    pygame.mixer.music.set_volume(MUSIC_VOL)
    pygame.mixer.music.play(-1)


# =============================
# LOAD IMAGES
# =============================
_bg_path = os.path.join(BASE_DIR, "background.png")
if not os.path.isfile(_bg_path):
    _bg_path = os.path.join(BASE_DIR, "Images", "background.png")
if not os.path.isfile(_bg_path):
    _bg_path = os.path.join(BASE_DIR, "assets", "bg.png")
if not os.path.isfile(_bg_path):
    _bg_path = os.path.join(BASE_DIR, "Images", "bg.png")

if _bg_path and os.path.isfile(_bg_path):
    bg = pygame.image.load(_bg_path).convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
else:
    bg = None


def draw_map(surf):
    """Draws the gameplay map (sky, ground, platforms). Does NOT draw background.png."""
    if bg:
        surf.blit(bg, (0, 0))
    else:
        surf.fill(SKY)

    pygame.draw.rect(surf, GRASS_DARK, ground)


def draw_text(surf, text, color, x, y, use_big=False):
    f = big_font if use_big else font
    img = f.render(text, True, color)
    surf.blit(img, (x, y))


def find_story_image_path(stem):
    """Resolve Lab -> Lab.png / lab.jpg / etc. in game folder."""
    exts = (".png", ".jpg", ".jpeg", ".webp")
    for name in [stem, stem.lower()]:
        for ext in exts:
            filename = name + ext
            # Check root first, then the Images folder
            for folder in ["", "Images"]:
                p = os.path.join(BASE_DIR, folder, filename)
                if os.path.isfile(p):
                    return p
    return None


def load_story_slide_surface(stem):
    path = find_story_image_path(stem)
    if path is None:
        return None
    img = pygame.image.load(path)
    if path.lower().endswith((".jpg", ".jpeg")):
        img = img.convert()
    else:
        img = img.convert_alpha()
    return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))


def draw_story_slide(surf, image, lines, index, total, stem, esc_skip_target):
    if image is not None:
        surf.blit(image, (0, 0))
    else:
        surf.fill((28, 32, 42))
        draw_text(surf, "Image not found", YELLOW, 40, 40)
        draw_text(surf, f"Add {stem}.png or {stem}.jpg in the game folder.", (180, 180, 200), 40, 90)

    y = HEIGHT - 138
    for line in lines:
        surf.blit(story_font.render(line, True, WHITE), (36, y))
        y += 30

    hint = f"CLICK / ENTER / SPACE — next     ESC — skip to {esc_skip_target}"
    surf.blit(story_hint_font.render(hint, True, (190, 195, 205)), (36, HEIGHT - 34))
    surf.blit(
        story_hint_font.render(f"{index + 1} / {total}", True, (140, 145, 155)),
        (WIDTH - 90, HEIGHT - 34),
    )


def run_slideshow(slides, esc_skip_target="game"):
    """
    Shows each slide with text. Returns 'quit', 'done' (finished), or 'skip' (ESC).
    esc_skip_target: short label for hint ('game' or 'menu').
    """
    cache = {}
    i = 0
    timer = 0

    while i < len(slides):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "skip"
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    i += 1
                    timer = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                i += 1
                timer = 0

        timer += clock.tick(60)
        if timer >= SLIDE_AUTO_MS:
            i += 1
            timer = 0

        if i >= len(slides):
            break

        stem = slides[i]["stem"]
        if stem not in cache:
            cache[stem] = load_story_slide_surface(stem)

        draw_story_slide(
            screen,
            cache[stem],
            slides[i]["lines"],
            i,
            len(slides),
            stem,
            esc_skip_target,
        )
        pygame.display.update()

    return "done"


def load_leaderboard_scores():
    scores = []
    if os.path.isfile(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        scores.append(int(line))
        except OSError:
            pass
    return sorted(scores, reverse=True)[:5]


def save_leaderboard_score(score):
    scores = load_leaderboard_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            for s in scores:
                f.write(f"{s}\n")
    except OSError:
        pass


def pick_zombie_type(weights):
    total = sum(w for _, w in weights)
    r = random.random() * total
    for ztype, w in weights:
        r -= w
        if r <= 0:
            return ztype
    return weights[-1][0]


def create_zombie(ztype):
    spec = ZOMBIE_SPECS[ztype]
    w, h = spec["w"], spec["h"]
    
    # Randomly choose side: 0 for Left, 1 for Right
    side = random.randint(0, 1)
    if side == 0:
        x = random.randint(-150, -w)  # Spawn off-screen left
        vx = spec["speed"]            # Move right
    else:
        x = random.randint(WIDTH, WIDTH + 150) # Spawn off-screen right
        vx = -spec["speed"]                     # Move left

    return {
        "type": ztype,
        "rect": pygame.Rect(x, ground.top - h, w, h),
        "hp": spec["hp"],
        "speed": spec["speed"],
        "vx": vx,
        "hit_flash": 0,
    }


def wave_transition_with_movement(wave_num, extra_lines, player, current_score, flawless=False):
    """
    Character moves across screen while showing wave completion overlay.
    Returns 'quit' or 'ok'.
    """
    # Save original position
    start_x = player.x
    start_y = player.y
    end_x = WIDTH // 2 - player.width // 2

    move_duration = 80
    move_timer = 0
    overlay_alpha = 0
    pulse_timer = 0

    # Create completion message
    completion_msg = [f"WAVE {wave_num} COMPLETE!", f"Kills: 20"]
    if flawless:
        completion_msg.append(f"FLAWLESS! +{POINTS_FLAWLESS_WAVE}")
    completion_msg.append(f"Bonus: +{POINTS_PER_WAVE} points")

    # Small bounce animation
    bounce_amplitude = 8
    bounce_speed = 0.15

    while True:
        dt = clock.tick(60)
        pulse_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return "ok"

        if move_timer < move_duration:
            # Move character with easing
            t = move_timer / move_duration
            eased = 1 - (1 - t) ** 3  # Ease out cubic
            player.x = start_x + (end_x - start_x) * eased

            # Add bounce effect
            player.y = start_y + math.sin(t * math.pi) * bounce_amplitude * (1 - t)

            move_timer += 1
            overlay_alpha = min(180, overlay_alpha + 5)
        else:
            # Hold position then fade out
            player.x = end_x
            player.y = start_y
            overlay_alpha = max(0, overlay_alpha - 3)
            if overlay_alpha == 0:
                # Reset player position for next wave
                player.x = 80
                return "ok"

        # Draw everything
        draw_map(screen) # Gameplay map

        # Draw player
        p_img = player_img_right
        screen.blit(p_img, (player.x, player.y))

        # Draw ground and platforms again for context
        pygame.draw.rect(screen, GRASS_DARK, ground)

        # Draw overlay with fade effect
        if overlay_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha // 2))
            screen.blit(overlay, (0, 0))

            # Draw wave title with glow effect
            title = completion_msg[0]
            glow_size = 3
            for offset in [(-glow_size, -glow_size), (glow_size, glow_size),
                           (-glow_size, glow_size), (glow_size, -glow_size)]:
                draw_text(screen, title, (80, 80, 80),
                          WIDTH // 2 - 150 + offset[0], 200 + offset[1], use_big=True)

            # Main title
            draw_text(screen, title, YELLOW, WIDTH // 2 - 150, 200, use_big=True)

            # Draw extra lines with fade
            y = 280
            for i, line in enumerate(completion_msg[1:]):
                line_alpha = max(0, min(255, overlay_alpha - i * 20))
                if line_alpha > 0:
                    color = GREEN if "FLAWLESS" in line else WHITE
                    line_surf = font.render(line, True, color)
                    line_surf.set_alpha(line_alpha)
                    screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y))
                    y += 34

            # Draw score
            score_text = f"Score: {current_score}"
            score_surf = font.render(score_text, True, XP_BAR)
            score_surf.set_alpha(overlay_alpha)
            screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, y + 20))

            # Draw continue hint with pulse effect
            pulse = abs(math.sin(pulse_timer * 0.003)) * 0.5 + 0.5
            hint_alpha = int(overlay_alpha * (0.4 + pulse * 0.6))
            if hint_alpha > 0:
                hint_text = "Press ENTER/SPACE to continue..."
                hint_surf = small_font.render(hint_text, True, (200, 200, 200))
                hint_surf.set_alpha(hint_alpha)
                screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, 520))

        pygame.display.update()


def boss_intro_cutscene():
    """Short narrative before Scientist boss. Returns 'quit' or 'ok'."""
    pages = [
        [
            "WAVE 5 — BOSS APPROACHING",
            "The horde thins... but something worse stirs in the lab ruins.",
        ],
        [
            "THE SCIENTIST — FINAL MUTATION",
            "Twisted by his own virus, he guards the cure with fury.",
            "End him. Secure the formula. Walk out alive.",
        ],
    ]
    for page in pages:
        t0 = pygame.time.get_ticks()
        done_page = False
        while not done_page:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        done_page = True
            if pygame.time.get_ticks() - t0 > 5500:
                done_page = True

            screen.fill((18, 8, 12))
            y = 140
            for line in page:
                sw, _ = font.size(line)
                col = (255, 200, 200) if "SCIENTIST" in line else WHITE
                draw_text(screen, line, col, WIDTH // 2 - sw // 2, y)
                y += 40
            draw_text(screen, "ENTER / SPACE — continue", YELLOW, WIDTH // 2 - 180, 400)
            pygame.display.update()
            clock.tick(60)
    return "ok"


def apply_brightness(surf):
    if GLOBAL_BRIGHTNESS >= 1.0:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(int(255 * (1.0 - GLOBAL_BRIGHTNESS)))
    surf.blit(overlay, (0, 0))

def draw_bar(surf, x, y, w, h, frac, fill_color, back_color=BAR_BACK, border=(90, 94, 102)):
    frac = max(0.0, min(1.0, frac))
    pygame.draw.rect(surf, back_color, (x, y, w, h))
    pygame.draw.rect(surf, fill_color, (x, y, int(w * frac), h))
    pygame.draw.rect(surf, border, (x, y, w, h), 2)


def resolve_vertical(player, vel_y, prev_bottom):
    """Returns (new_vel_y, on_ground)."""
    vy = vel_y
    on_ground = False

    if player.colliderect(ground):
        player.bottom = ground.top
        vy = 0.0
        on_ground = True
        return vy, on_ground

    for plat in platforms:
        if not player.colliderect(plat):
            continue
        if vy >= 0 and prev_bottom <= plat.top + 10:
            player.bottom = plat.top
            vy = 0.0
            on_ground = True
            return vy, on_ground
        if vy < 0 and player.top < plat.bottom <= player.top - vy + 12:
            player.top = plat.bottom
            vy = 0.0

    return vy, on_ground


def draw_zombie_entity(surf, z):
    r = z["rect"]
    # Face right if moving right, left if moving left
    base_img = zombie_img_right if z["vx"] > 0 else zombie_img_left
    scaled = pygame.transform.smoothscale(base_img, (r.w, r.h))
    surf.blit(scaled, r.topleft)
    if z["type"] == "tank":
        tint = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        tint.fill((30, 90, 40, 95))
        surf.blit(tint, r.topleft)
    if z["hit_flash"] > 0:
        flash = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        a = min(160, z["hit_flash"] * 22)
        flash.fill((255, 255, 255, a))
        surf.blit(flash, r.topleft)


def draw_player_health_bar(surf, player, health, max_h):
    bw = 64
    bh = 8
    bx = player.centerx - bw // 2
    by = player.y - 14
    col = BAR_HP_OK if health > max_h // 2 else BAR_HP
    draw_bar(surf, bx, by, bw, bh, health / max_h, col)


def draw_boss_attack_fx(surf, boss_rect, facing_right, phase, max_phase):
    if phase <= 0:
        return
    t = 1.0 - (phase / max_phase)
    span = 70 + 40 * t
    cx = boss_rect.right if facing_right else boss_rect.left
    cy = boss_rect.centery - 10
    start = math.radians(-40 if facing_right else -140)
    end = math.radians(50 if facing_right else 140)
    thick = max(3, int(8 * (1 - abs(0.5 - t))))
    slash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.arc(
        slash,
        (*SLASH_COLOR[:3], int(90 + 120 * (1 - t))),
        (cx - span, cy - span, span * 2, span * 2),
        start,
        end,
        thick,
    )
    surf.blit(slash, (0, 0))


def wrap_text(text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if current == "" else current + " " + word
        if fnt.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def build_feedback(stats):
    feedback = []

    acc = stats.get("accuracy", 0)
    taken = stats.get("taken", 0)
    jumps = stats.get("jumps", 0)
    kills = stats.get("kills", {})
    time = stats.get("time", 0)

    # Combat Precision
    if acc > 85:
        feedback.append(f"Marksman: Exceptional trigger discipline with {acc:.1f}% accuracy.")
    elif acc < 35:
        feedback.append(f"Suppression Specialist: You prioritized volume over precision ({acc:.1f}% accuracy).")

    # Survival Skills
    if taken == 0:
        feedback.append("Ghost: You cleared the entire mission without taking a single hit. Flawless.")
    elif taken < 4:
        feedback.append(f"Evasive Survivor: Only {taken} hits taken. You managed space and threats effectively.")
    else:
        feedback.append(f"Battered Veteran: You took {taken} hits. You survived by the skin of your teeth.")

    # Movement Style
    if jumps > 150:
        feedback.append(f"Acrobat: With {jumps} jumps, you utilized verticality to stay ahead of the horde.")
    
    # Mission Efficiency
    if time < 180:
        feedback.append(f"Blitz Operative: Record time mission clear in {time}s. Maximum efficiency.")

    # Target Focus
    tanks = kills.get("tank", 0)
    if tanks > 10:
        feedback.append(f"Tank Buster: You neutralized {tanks} Tank-class infected. Heavy targets were your focus.")

    if not feedback:
        feedback.append("Solid Performance: You followed standard protocols and completed the mission.")

    return feedback


def start_menu():
    global MUSIC_VOL, SFX_VOL, GLOBAL_BRIGHTNESS
    selected_idx = 0
    menu_items = ["PLAY", "SETTINGS", "EXIT"]
    in_settings = False
    settings_idx = 0
    settings_items = ["Brightness", "Sound", "Back"]

    while True:
        clock.tick(60)
        screen.fill(UI_BG)
        if bg: # Draw background.png for the menu
            screen.blit(bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160)) # More transparent to show background.png better
        screen.blit(overlay, (0, 0))

        draw_text(screen, "VIRUS: LAST SURVIVOR", WHITE, WIDTH // 2 - 280, 80, use_big=True)

        if not in_settings:
            for i, item in enumerate(menu_items):
                color = GREEN if i == selected_idx else WHITE
                text = f"> {item} <" if i == selected_idx else item
                draw_text(screen, text, color, WIDTH // 2 - 80, 240 + i * 60)
            top = load_leaderboard_scores()
            if top:
                draw_text(screen, f"Top Score: {top[0]}", YELLOW, WIDTH // 2 - 80, 450)
        else:
            for i, item in enumerate(settings_items):
                color = YELLOW if i == settings_idx else WHITE
                text = f"> {item} <" if i == settings_idx else item
                if item == "Brightness":
                    text += f" : {int(GLOBAL_BRIGHTNESS * 100)}%"
                elif item == "Sound":
                    text += f" : {int(MUSIC_VOL * 100)}%"
                draw_text(screen, text, color, WIDTH // 2 - 130, 240 + i * 60)
            draw_text(screen, "W/S: Navigate   A/D or Arrows: Adjust", (170, 175, 185), WIDTH // 2 - 180, 450)

        apply_brightness(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if in_settings: settings_idx = (settings_idx - 1) % len(settings_items)
                    else: selected_idx = (selected_idx - 1) % len(menu_items)
                    _play_sfx(sfx_click)
                elif event.key == pygame.K_s:
                    if in_settings: settings_idx = (settings_idx + 1) % len(settings_items)
                    else: selected_idx = (selected_idx + 1) % len(menu_items)
                    _play_sfx(sfx_click)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    _play_sfx(sfx_click)
                    if not in_settings:
                        if menu_items[selected_idx] == "PLAY": return True
                        elif menu_items[selected_idx] == "EXIT": return False
                        elif menu_items[selected_idx] == "SETTINGS": in_settings = True
                    else:
                        if settings_items[settings_idx] == "Back": in_settings = False
                elif in_settings:
                    if event.key in (pygame.K_d, pygame.K_RIGHT):
                        if settings_items[settings_idx] == "Brightness":
                            GLOBAL_BRIGHTNESS = min(1.0, GLOBAL_BRIGHTNESS + 0.05)
                        elif settings_items[settings_idx] == "Sound":
                            MUSIC_VOL = min(1.0, MUSIC_VOL + 0.1)
                            SFX_VOL = min(1.0, SFX_VOL + 0.1)
                            pygame.mixer.music.set_volume(MUSIC_VOL)
                            update_sfx_volumes()
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        if settings_items[settings_idx] == "Brightness":
                            GLOBAL_BRIGHTNESS = max(0.1, GLOBAL_BRIGHTNESS - 0.05)
                        elif settings_items[settings_idx] == "Sound":
                            MUSIC_VOL = max(0.0, MUSIC_VOL - 0.1)
                            SFX_VOL = max(0.0, SFX_VOL - 0.1)
                            pygame.mixer.music.set_volume(MUSIC_VOL)
                            update_sfx_volumes()
                if event.key == pygame.K_ESCAPE:
                    if in_settings: in_settings = False
                    else: return False


def game_over_menu():
    """Returns 'again', 'menu', or 'quit'."""
    pygame.mixer.music.pause()
    _play_sfx(sfx_game_over)
    try:
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "again"
                    if event.key == pygame.K_m:
                        return "menu"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"

            screen.fill(UI_BG)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            draw_text(screen, "GAME OVER", RED, WIDTH // 2 - 170, 200, use_big=True)
            draw_text(screen, "R — Play again      M — Main menu      ESC — Quit", WHITE, 200, 300)
            apply_brightness(screen)
            pygame.display.update()
    finally:
        pygame.mixer.music.unpause()


def win_menu(stats):
    """stats dict: score, badges (list of str), challenges (list of str). Returns 'menu' or 'quit'."""
    feedback_list = build_feedback(stats)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_m, pygame.K_RETURN):
                    return "menu"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        screen.fill((10, 25, 15))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 40, 20, 175))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "YOU WON!", GREEN, WIDTH // 2 - 150, 40, use_big=True)
        draw_text(screen, f"Final score: {stats.get('score', 0)}", WHITE, WIDTH // 2 - 100, 100)
        draw_text(screen, "Saved to score.txt if in top 5.", (180, 200, 180), WIDTH // 2 - 160, 135)

        # Summary of tracked performance
        perf_sum = f"Acc: {stats.get('accuracy',0):.1f}% | Damage Taken: {stats.get('taken',0)} | Time: {stats.get('time',0)}s"
        draw_text(screen, perf_sum, (200, 200, 200), WIDTH // 2 - 250, 165)

        badge_y = 205
        draw_text(screen, "Badges:", YELLOW, 70, badge_y)
        badge_y += 35
        if stats.get("badges"):
            for b in stats.get("badges", []):
                draw_text(screen, f"- {b}", WHITE, 90, badge_y)
                badge_y += 28
        else:
            draw_text(screen, "- None", WHITE, 90, badge_y)

        draw_text(screen, "Challenges:", (160, 220, 255), 70, 280)
        cy = 315
        if stats.get("challenges"):
            for c in stats.get("challenges", []):
                wrapped = wrap_text(f"- {c}", small_font, 350)
                for line in wrapped:
                    screen.blit(small_font.render(line, True, WHITE), (90, cy))
                    cy += 24
                cy += 4
        else:
            screen.blit(small_font.render("- No bonus challenges completed", True, WHITE), (90, cy))

        draw_text(screen, "Feedback:", GREEN, 540, 175)
        fy = 210
        for fb in feedback_list:
            wrapped = wrap_text(f"- {fb}", small_font, 360)
            for line in wrapped:
                screen.blit(small_font.render(line, True, WHITE), (560, fy))
                fy += 24
            fy += 6

        draw_text(screen, "M / ENTER — Main menu      ESC — Quit", WHITE, 220, 550)

        apply_brightness(screen)
        pygame.display.update()


def play_round():
    """
    Wave-based run. Returns 'quit', 'dead', or ('win', stats_dict).
    """
    wave_help = [
        ["Wave 1 — basic infected only.", "Clear 20 to advance. Challenge: eliminate all 20."],
        ["Wave 2 — faster strains join the horde.", "Spawns accelerate. Keep moving."],
        ["Wave 3 — tanks appear (extra HP).", "Pour damage into brutes before they reach you."],
        ["Wave 4 — mixed swarm, rapid deployment.", "Control space. Break priority targets."],
        ["Wave 5 — last 20 infected before the Scientist.", "Then the boss fight begins."],
    ]

    player = pygame.Rect(80, ground.top - PLAYER_H, PLAYER_W, PLAYER_H)
    vel_y = 0.0
    facing_right = True
    coyote = 0
    jump_buffer = 0

    health = MAX_HEALTH
    score = 0
    total_zombie_kills = 0
    bullets = []
    zombies = []

    # Live performance tracking
    stats_tracking = {
        "fired": 0,
        "hits": 0,
        "taken": 0,
        "jumps": 0,
        "kills": {"normal": 0, "fast": 0, "tank": 0},
        "start_ticks": pygame.time.get_ticks()
    }

    wave_index = 0
    spawned_this_wave = 0
    killed_this_wave = 0
    spawn_timer = 0
    damage_this_wave = False
    boss_fight = False

    boss = pygame.Rect(WIDTH - BOSS_W - 40, ground.top - BOSS_H, BOSS_W, BOSS_H)
    boss_health = MAX_BOSS_HP
    boss_active = False
    boss_facing_right = True
    boss_attack_timer = 0
    boss_attack_cd = 0
    boss_hit_done = False
    boss_hit_flash = 0

    badges = {"hunter": False, "survivor": False, "legend": False}
    challenges_done = []
    toast = ("", 0)
    hurt_overlay = 0

    def set_toast(msg, frames=120):
        nonlocal toast
        toast = (msg, frames)

    def reset_player():
        nonlocal vel_y, coyote, jump_buffer
        player.x = 80
        player.y = ground.top - PLAYER_H
        vel_y = 0.0
        coyote = COYOTE_FRAMES
        jump_buffer = 0

    def register_damage():
        nonlocal health, damage_this_wave, hurt_overlay
        health -= 1
        stats_tracking["taken"] += 1
        damage_this_wave = True
        hurt_overlay = 14
        _play_sfx(sfx_player_hurt)

    def advance_wave_or_boss():
        nonlocal wave_index, killed_this_wave, spawned_this_wave, spawn_timer
        nonlocal damage_this_wave, boss_fight, boss_active, bullets, zombies, score, badges

        score += POINTS_PER_WAVE
        flawless = not damage_this_wave

        if flawless:
            score += POINTS_FLAWLESS_WAVE
            msg = f"No damage Wave {wave_index + 1}"
            if msg not in challenges_done:
                challenges_done.append(msg)
            set_toast(f"Challenge: Flawless wave! +{POINTS_FLAWLESS_WAVE}", 100)

        if wave_index == 0 and killed_this_wave >= WAVE_ZOMBIE_COUNT:
            msg = "Kill 20 zombies in Wave 1"
            if msg not in challenges_done:
                challenges_done.append(msg)
            set_toast("Challenge: 20 kills in Wave 1 — complete!", 100)

        if wave_index == 2 and not badges["survivor"]:
            badges["survivor"] = True
            set_toast("Badge unlocked: Survivor (cleared Wave 3)", 140)

        # Show transition with movement for waves 1-4 (not boss wave)
        if wave_index < 4:
            if wave_transition_with_movement(wave_index + 1, wave_help[wave_index], player, score, flawless) == "quit":
                return "quit"

            wave_index += 1
            killed_this_wave = 0
            spawned_this_wave = 0
            spawn_timer = 0
            damage_this_wave = False
        else:
            # This is wave 4 completing, next is boss
            zombies.clear()
            bullets.clear()
            if boss_intro_cutscene() == "quit":
                return "quit"
            boss_fight = True
            boss_active = True
            boss_health = MAX_BOSS_HP
            boss.x = WIDTH - BOSS_W - 40
            boss.y = ground.top - BOSS_H
            _play_sfx(sfx_zombie_roar)
        return None

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    jump_buffer = JUMP_BUFFER_FRAMES

                if event.key == pygame.K_SPACE:
                    if facing_right:
                        bx = player.right - 4
                        vx = BULLET_SPEED
                    else:
                        bx = player.left - 11
                        vx = -BULLET_SPEED
                    bullets.append({"rect": pygame.Rect(bx, player.centery - 3, 14, 6), "vx": vx})
                    stats_tracking["fired"] += 1
                    _play_sfx(sfx_gunshot)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w and vel_y < JUMP_CUT:
                    vel_y = JUMP_CUT

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED
            facing_right = False
        if keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED
            facing_right = True

        player.x = max(0, min(player.x, WIDTH - player.width))

        prev_bottom = player.bottom
        vel_y += GRAVITY
        if vel_y > MAX_FALL:
            vel_y = MAX_FALL

        player.y += int(vel_y)
        vel_y, on_ground = resolve_vertical(player, vel_y, prev_bottom)

        if on_ground:
            coyote = COYOTE_FRAMES
        else:
            coyote = max(0, coyote - 1)

        if jump_buffer > 0:
            if on_ground or coyote > 0:
                vel_y = JUMP_VEL
                jump_buffer = 0
                coyote = 0
                stats_tracking["jumps"] += 1
                _play_sfx(sfx_jump)
            else:
                jump_buffer -= 1

        cfg = WAVE_CONFIG[wave_index] if wave_index < len(WAVE_CONFIG) else WAVE_CONFIG[-1]
        if not boss_fight and spawned_this_wave < WAVE_ZOMBIE_COUNT and len(zombies) < MAX_ZOMBIES_ALIVE:
            spawn_timer += 1
            if spawn_timer >= cfg["spawn_every"]:
                spawn_timer = 0
                zt = pick_zombie_type(cfg["weights"])
                zombies.append(create_zombie(zt))
                spawned_this_wave += 1

        for z in zombies:
            z["rect"].x += int(z["vx"])
            if z["hit_flash"] > 0:
                z["hit_flash"] -= 1
        
        # Clean up zombies that walk off either side of the screen
        for z in zombies[:]:
            if (z["vx"] < 0 and z["rect"].right < 0) or (z["vx"] > 0 and z["rect"].left > WIDTH):
                zombies.remove(z)
                spawned_this_wave -= 1 # Allow a replacement to spawn

        for b in bullets[:]:
            b["rect"].x += b["vx"]
            if b["rect"].right < 0 or b["rect"].left > WIDTH:
                continue

            hit = False
            if boss_fight and boss_active and b["rect"].colliderect(boss):
                boss_health -= 1
                boss_hit_flash = 8
                hit = True
                stats_tracking["hits"] += 1
            elif not boss_fight:
                for z in zombies[:]:
                    if b["rect"].colliderect(z["rect"]):
                        z["hp"] -= 1
                        z["hit_flash"] = 7
                        _play_sfx(sfx_hit)
                        stats_tracking["hits"] += 1
                        if z["hp"] <= 0:
                            score += POINTS_PER_KILL
                            stats_tracking["kills"][z["type"]] += 1
                            total_zombie_kills += 1
                            killed_this_wave += 1
                            zombies.remove(z)
                            if total_zombie_kills >= 50 and not badges["hunter"]:
                                badges["hunter"] = True
                                set_toast("Badge unlocked: Zombie Hunter (50 kills)", 140)

                            if killed_this_wave >= WAVE_ZOMBIE_COUNT:
                                r = advance_wave_or_boss()
                                if r == "quit":
                                    return "quit"
                        hit = True
                        break

            if hit and b in bullets:
                bullets.remove(b)

        if not boss_fight:
            for z in zombies[:]:
                if z["rect"].colliderect(player):
                    register_damage()
                    if z in zombies: zombies.remove(z)
                    spawned_this_wave -= 1 # Allow a replacement to spawn
                    reset_player()
                    if health <= 0:
                        return "dead"

        if boss_fight and boss_active:
            if boss_attack_cd > 0:
                boss_attack_cd -= 1
            if boss_attack_timer > 0:
                boss_attack_timer -= 1

            dx = player.centerx - boss.centerx
            dy = player.centery - boss.centery
            dist = math.hypot(dx, dy)
            boss_facing_right = dx > 0

            if boss_attack_timer == 0:
                step = BOSS_CHASE_SPEED
                if dx > step:
                    boss.x += int(step)
                elif dx < -step:
                    boss.x -= int(step)
                else:
                    boss.x += int(dx)

            if boss_attack_timer > BOSS_ATTACK_DURATION - 10:
                lunge = int(BOSS_LUNGE * (boss_attack_timer / BOSS_ATTACK_DURATION))
                boss.x += lunge if boss_facing_right else -lunge

            boss.x = max(0, min(boss.x, WIDTH - boss.width))

            if (
                    boss_attack_timer == 0
                    and boss_attack_cd == 0
                    and dist < BOSS_ATTACK_RANGE
                    and abs(dy) < 120
            ):
                boss_attack_timer = BOSS_ATTACK_DURATION
                boss_attack_cd = BOSS_ATTACK_COOLDOWN
                boss_hit_done = False

            strike_window = 12 < boss_attack_timer < 24
            if strike_window and not boss_hit_done and boss.colliderect(player):
                register_damage()
                boss_hit_done = True
                reset_player()
                if health <= 0:
                    return "dead"

            if boss_health <= 0:
                score += POINTS_BOSS_DEFEAT
                badges["legend"] = True
                _play_sfx(sfx_boss_death)
                badge_names = []
                if badges["hunter"]:
                    badge_names.append("Zombie Hunter")
                if badges["survivor"]:
                    badge_names.append("Survivor")
                if badges["legend"]:
                    badge_names.append("Legend")

                # Compile final gameplay statistics
                duration = (pygame.time.get_ticks() - stats_tracking["start_ticks"]) // 1000
                accuracy = (stats_tracking["hits"] / max(1, stats_tracking["fired"])) * 100

                return (
                    "win",
                    {
                        "score": score,
                        "badges": badge_names,
                        "challenges": list(challenges_done),
                        "accuracy": accuracy,
                        "taken": stats_tracking["taken"],
                        "jumps": stats_tracking["jumps"],
                        "kills": stats_tracking["kills"],
                        "time": duration
                    },
                )

        if boss_hit_flash > 0:
            boss_hit_flash -= 1
        if hurt_overlay > 0:
            hurt_overlay -= 1
        if toast[1] > 0:
            toast = (toast[0], toast[1] - 1)

        if health <= 0:
            return "dead"

        draw_map(screen) # Call to draw_map, now only draws sky/ground/platforms

        p_img = player_img_right if facing_right else player_img_left
        screen.blit(p_img, (player.x, player.y))

        for z in zombies:
            draw_zombie_entity(screen, z)
            # Draw health bar for zombies (primarily for high-HP types like Tanks)
            max_z_hp = ZOMBIE_SPECS[z["type"]]["hp"]
            if max_z_hp > 1:
                bz_w, bz_h = 44, 6
                draw_bar(screen, z["rect"].centerx - bz_w // 2, z["rect"].y - 12, bz_w, bz_h, z["hp"] / max_z_hp, RED)

        for b in bullets:
            pygame.draw.rect(screen, YELLOW, b["rect"])

        if boss_fight and boss_active:
            draw_boss_attack_fx(screen, boss, boss_facing_right, boss_attack_timer, BOSS_ATTACK_DURATION)
            b_img = boss_img_right if boss_facing_right else boss_img_left
            if boss_hit_flash > 0:
                sh = pygame.Surface((boss.width, boss.height), pygame.SRCALPHA)
                sh.fill((255, 255, 255, min(140, boss_hit_flash * 20)))
                screen.blit(b_img, (boss.x, boss.y))
                screen.blit(sh, boss.topleft)
            else:
                screen.blit(b_img, (boss.x, boss.y))

            # Boss Health Bar at top center
            draw_text(screen, "SCIENTIST BOSS", BOSS_BAR, WIDTH // 2 - 80, 60)
            draw_bar(screen, WIDTH // 2 - 150, 95, 300, 16, boss_health / MAX_BOSS_HP, BOSS_BAR)

        draw_text(screen, f"Wave {wave_index + 1}/5   Wave kills: {killed_this_wave}/{WAVE_ZOMBIE_COUNT}", WHITE, 20,
                  12)
        draw_text(screen, f"Mission: {total_zombie_kills}/{MISSION_ZOMBIES}   Score: {score}", WHITE, 20, 40)
        draw_text(screen, "← → move   W jump   SPACE shoot", WHITE, 420, 12)

        draw_player_health_bar(screen, player, health, MAX_HEALTH)

        if hurt_overlay > 0:
            red = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red.fill((180, 0, 0, min(120, hurt_overlay * 12)))
            screen.blit(red, (0, 0))

        if toast[1] > 0 and toast[0]:
            tw, _ = font.size(toast[0])
            draw_text(screen, toast[0], YELLOW, WIDTH // 2 - tw // 2, 526)

        apply_brightness(screen)
        pygame.display.update()


def main():
    _play_music(MENU_MUSIC_PATH) # Start menu music on launch
    while True:
        if not start_menu():
            pygame.quit()
            sys.exit()
        _play_music(GAME_MUSIC_PATH)

        intro_result = run_slideshow(INTRO_SLIDES, esc_skip_target="game")
        if intro_result == "quit":
            pygame.quit()
            sys.exit()

        while True:
            outcome = play_round()
            if outcome == "quit":
                pygame.quit()
                sys.exit()
            if isinstance(outcome, tuple) and outcome[0] == "win":
                _, win_stats = outcome
                save_leaderboard_score(win_stats["score"])
                outro_result = run_slideshow(OUTRO_SLIDES, esc_skip_target="menu")
                if outro_result == "quit":
                    pygame.quit()
                    sys.exit()
                if win_menu(win_stats) == "quit": # win_menu returns 'menu' or 'quit'
                    pygame.quit()
                    sys.exit()
                pygame.mixer.music.stop() # Stop game music
                _play_music(MENU_MUSIC_PATH) # Restart menu music
                break # Go back to main menu
            if outcome == "dead":
                choice = game_over_menu()
                if choice == "quit":
                    pygame.quit()
                    sys.exit()
                if choice == "menu":
                    pygame.mixer.music.stop() # Stop game music
                    _play_music(MENU_MUSIC_PATH) # Restart menu music
                    break
                # again: stay in inner loop


if __name__ == "__main__":
    main()