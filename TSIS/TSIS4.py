import pygame
import random
import json
import os
import psycopg2
from datetime import datetime
 
pygame.init()
 
WIDTH, HEIGHT = 800, 800
SNAKE_BLOCK = 10
BASE_SPEED = 25
EAT_RADIUS = 40
SETTINGS_FILE = "settings.json"
 
# ── Palette ────────────────────────────────────────────────────────────────────
BG          = (8,    4,   20)
WHITE       = (220, 210, 255)
NEON_PINK   = (255,  20, 147)
NEON_CYAN   = (0,   255, 220)
NEON_GREEN  = (57,  255,  20)
NEON_YELLOW = (255, 240,   0)
NEON_ORANGE = (255, 100,   0)
NEON_PURPLE = (180,   0, 255)
DARK_PURPLE = (40,    0,  80)
MID_PURPLE  = (70,   10, 120)
DIM_PINK    = (100,   0,  60)
GRID_COLOR  = (20,    8,  40)
POISON_COL  = (180,   0,  50)
 
PU_SPEED  = "speed_boost"
PU_SLOW   = "slow_motion"
PU_SHIELD = "shield"
PU_COLORS = {PU_SPEED: NEON_CYAN, PU_SLOW: NEON_PURPLE, PU_SHIELD: NEON_ORANGE}
 
font_sm    = pygame.font.SysFont("consolas", 18)
font_md    = pygame.font.SysFont("consolas", 26)
font_lg    = pygame.font.SysFont("consolas", 40)
font_xl    = pygame.font.SysFont("consolas", 56)
font_input = pygame.font.SysFont("consolas", 30)
 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape from KBTU")
clock = pygame.time.Clock()
 
DEFAULT_SETTINGS = {
    "snake_color": list(NEON_PINK),
    "grid_overlay": False
}
 
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()
 
def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)
 
settings = load_settings()
 
# ── Database ───────────────────────────────────────────────────────────────────
os.environ["PGCLIENTENCODING"] = "UTF8"
 
DB_CONFIG = {
    "host":     "localhost",
    "dbname":   "phonebook",
    "user":     "postgres",
    "password": "adminpp2",
    "options":  "-c lc_messages=en_US.UTF-8",
}
 
def get_connection():
    return psycopg2.connect(**DB_CONFIG)
 
def init_db():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close(); conn.close()
        print("[DB] Connected successfully to 'phonebook'")
        return True
    except Exception as e:
        print(f"[DB] init error: {e}")
        return False
 
def get_or_create_player(username):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;", (username,))
        conn.commit()
        cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
        pid = cur.fetchone()[0]
        cur.close(); conn.close()
        return pid
    except Exception as e:
        print(f"[DB] get_or_create error: {e}")
        return None
 
def save_game_session(player_id, score, level_reached):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s);",
            (player_id, score, level_reached)
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"[DB] save session error: {e}")
 
def get_personal_best(player_id):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s;", (player_id,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return row[0] if row and row[0] is not None else 0
    except Exception as e:
        print(f"[DB] personal best error: {e}")
        return 0
 
def get_leaderboard():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached, gs.played_at
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception as e:
        print(f"[DB] leaderboard error: {e}")
        return []
 
db_available = init_db()
 
# ── Helpers ────────────────────────────────────────────────────────────────────
def draw_bg():
    screen.fill(BG)
 
def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center: rect.center = (x, y)
    else:      rect.topleft = (x, y)
    screen.blit(surf, rect)
 
def draw_button(text, rect, color, hover_color, font=font_md):
    mx, my = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mx, my)
    col = hover_color if hovered else color
    pygame.draw.rect(screen, DARK_PURPLE, rect, border_radius=6)
    pygame.draw.rect(screen, col, rect, 2, border_radius=6)
    draw_text(text, font, col, rect.centerx, rect.centery, center=True)
    return hovered
 
def draw_grid():
    for x in range(0, WIDTH, SNAKE_BLOCK):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SNAKE_BLOCK):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
 
def snap(v):
    return round(v / SNAKE_BLOCK) * SNAKE_BLOCK
 
def random_pos(exclude=None, margin_top=40):
    for _ in range(300):
        x = snap(random.randrange(0, WIDTH  - SNAKE_BLOCK))
        y = snap(random.randrange(margin_top, HEIGHT - SNAKE_BLOCK))
        if exclude is None or (x, y) not in exclude:
            return x, y
    return snap(WIDTH // 2), snap(HEIGHT // 2)
 
# ── Username Screen ────────────────────────────────────────────────────────────
def username_screen():
    username = ""
    error    = ""
    cursor_visible = True
    cursor_timer   = pygame.time.get_ticks()
 
    while True:
        now = pygame.time.get_ticks()
        if now - cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer   = now
 
        draw_bg()
        pygame.draw.line(screen, NEON_PURPLE, (60, 0), (60, HEIGHT), 1)
        pygame.draw.line(screen, NEON_PURPLE, (WIDTH-60, 0), (WIDTH-60, HEIGHT), 1)
 
        draw_text("ESCAPE FROM KBTU", font_xl, NEON_PINK, WIDTH//2, 170, center=True)
        draw_text(">> ENTER IN THE GAME <<", font_sm, NEON_CYAN, WIDTH//2, 270, center=True)
 
        box = pygame.Rect(WIDTH//2 - 190, 310, 380, 50)
        pygame.draw.rect(screen, (15, 5, 35), box, border_radius=4)
        pygame.draw.rect(screen, NEON_CYAN, box, 2, border_radius=4)
        display_name = username + ("|" if cursor_visible else " ")
        draw_text(display_name, font_input, WHITE, box.x + 14, box.y + 10)
 
        if error:
            draw_text(error, font_sm, NEON_PINK, WIDTH//2, 380, center=True)
 
        btn = pygame.Rect(WIDTH//2 - 110, 420, 220, 52)
        draw_button("[PLAY]", btn, NEON_CYAN, NEON_PINK)
        draw_text("ENTER or click to start", font_sm, MID_PURPLE, WIDTH//2, 492, center=True)
        pygame.display.update()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = username.strip()
                    if len(name) < 1: error = "Name cannot be empty!"
                    elif len(name) > 50: error = "Name too long!"
                    else: return name
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 50 and event.unicode.isprintable():
                        username += event.unicode
                error = ""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(event.pos):
                    name = username.strip()
                    if len(name) < 1: error = "Name cannot be empty!"
                    else: return name
        clock.tick(60)
 
# ── Main Menu ──────────────────────────────────────────────────────────────────
def main_menu():
    while True:
        draw_bg()
        if settings.get("grid_overlay"): draw_grid()
 
        pygame.draw.line(screen, NEON_PURPLE, (0, 85), (WIDTH, 85), 1)
        pygame.draw.line(screen, NEON_PURPLE, (0, HEIGHT-85), (WIDTH, HEIGHT-85), 1)
 
        draw_text("ESCAPE FROM KBTU", font_xl, NEON_PINK, WIDTH//2, 45, center=True)
 
        btn_play = pygame.Rect(WIDTH//2 - 130, 240, 260, 56)
        btn_lb   = pygame.Rect(WIDTH//2 - 130, 315, 260, 56)
        btn_set  = pygame.Rect(WIDTH//2 - 130, 390, 260, 56)
        btn_quit = pygame.Rect(WIDTH//2 - 130, 465, 260, 56)
 
        draw_button("[ PLAY ]",        btn_play, NEON_GREEN,  NEON_CYAN)
        draw_button("[ LEADERBOARD ]", btn_lb,   NEON_CYAN,   NEON_PURPLE)
        draw_button("[ SETTINGS ]",    btn_set,  NEON_PURPLE, NEON_PINK)
        draw_button("[ QUIT ]",        btn_quit, DIM_PINK,    NEON_PINK)
 
        pygame.display.update()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(event.pos):  return "play"
                if btn_lb.collidepoint(event.pos):    return "leaderboard"
                if btn_set.collidepoint(event.pos):   return "settings"
                if btn_quit.collidepoint(event.pos):  pygame.quit(); quit()
        clock.tick(60)
 
# ── Leaderboard ────────────────────────────────────────────────────────────────
def leaderboard_screen():
    rows = get_leaderboard()
    while True:
        draw_bg()
        pygame.draw.line(screen, NEON_CYAN, (0, 85), (WIDTH, 85), 1)
        draw_text("TOP 10", font_xl, NEON_CYAN, WIDTH//2, 45, center=True)
 
        headers = ["#", "USERNAME", "SCORE", "LVL", "DATE"]
        col_x   = [40, 100, 390, 490, 570]
        for i, h in enumerate(headers):
            draw_text(h, font_sm, NEON_PURPLE, col_x[i], 100)
        pygame.draw.line(screen, NEON_PURPLE, (30, 122), (770, 122), 1)
 
        rank_colors = [NEON_YELLOW, WHITE, NEON_ORANGE]
 
        if not rows:
            draw_text("No records yet.", font_md, MID_PURPLE, WIDTH//2, 300, center=True)
        else:
            for i, (uname, score, level, played_at) in enumerate(rows):
                y = 135 + i * 52
                col = rank_colors[i] if i < 3 else WHITE
                date_str = played_at.strftime("%Y-%m-%d") if isinstance(played_at, datetime) else str(played_at)[:10]
                draw_text(str(i+1),        font_sm, col,         col_x[0], y)
                draw_text(str(uname)[:18], font_sm, WHITE,       col_x[1], y)
                draw_text(str(score),      font_sm, NEON_GREEN,  col_x[2], y)
                draw_text(str(level),      font_sm, NEON_CYAN,   col_x[3], y)
                draw_text(date_str,        font_sm, WHITE,       col_x[4], y)
 
        btn_back = pygame.Rect(WIDTH//2 - 110, 740, 220, 48)
        draw_button("[ BACK ]", btn_back, NEON_PINK, NEON_PURPLE)
        pygame.display.update()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(event.pos): return
        clock.tick(60)
 
# ── Settings ───────────────────────────────────────────────────────────────────
COLOR_PRESETS = [
    ("Pink",   NEON_PINK),
    ("Cyan",   NEON_CYAN),
    ("Green",  NEON_GREEN),
    ("Orange", NEON_ORANGE),
    ("Yellow", NEON_YELLOW),
]
 
def settings_screen():
    global settings
    local = settings.copy()
    selected_color_idx = 0
    for i, (_, c) in enumerate(COLOR_PRESETS):
        if list(c) == local["snake_color"]:
            selected_color_idx = i; break
 
    while True:
        draw_bg()
        pygame.draw.line(screen, NEON_PINK, (0, 85), (WIDTH, 85), 1)
        draw_text("SETTINGS", font_xl, NEON_PINK, WIDTH//2, 45, center=True)
 
        draw_text("Grid Overlay:", font_md, WHITE, 100, 160)
        btn_grid = pygame.Rect(440, 155, 140, 44)
        lbl_grid = "ON" if local["grid_overlay"] else "OFF"
        col_grid = NEON_GREEN if local["grid_overlay"] else NEON_PINK
        draw_button(lbl_grid, btn_grid, col_grid, col_grid)
 
        draw_text("Snake Color:", font_md, WHITE, 100, 250)
        color_rects = []
        for i, (name, col) in enumerate(COLOR_PRESETS):
            r = pygame.Rect(90 + i * 125, 300, 110, 42)
            color_rects.append(r)
            pygame.draw.rect(screen, DARK_PURPLE, r, border_radius=6)
            border_col = col if i == selected_color_idx else MID_PURPLE
            pygame.draw.rect(screen, border_col, r, 2, border_radius=6)
            draw_text(name, font_sm, col, r.centerx, r.centery, center=True)
 
        btn_save = pygame.Rect(WIDTH//2 - 140, 560, 280, 52)
        draw_button("[ SAVE & BACK ]", btn_save, NEON_GREEN, NEON_CYAN)
        pygame.display.update()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_grid.collidepoint(event.pos):
                    local["grid_overlay"] = not local["grid_overlay"]
                for i, r in enumerate(color_rects):
                    if r.collidepoint(event.pos):
                        selected_color_idx = i
                        local["snake_color"] = list(COLOR_PRESETS[i][1])
                if btn_save.collidepoint(event.pos):
                    settings = local
                    save_settings(settings)
                    return
        clock.tick(60)
 
# ── Game Over ──────────────────────────────────────────────────────────────────
def game_over_screen(score, level, personal_best):
    while True:
        draw_bg()
        pygame.draw.line(screen, NEON_PINK, (0, 100), (WIDTH, 100), 1)
        pygame.draw.line(screen, NEON_PINK, (0, HEIGHT-100), (WIDTH, HEIGHT-100), 1)
 
        draw_text("GAME OVER", font_xl, NEON_PINK, WIDTH//2, 55, center=True)
        draw_text(f"Score  : {score}",         font_md, WHITE,       WIDTH//2, 230, center=True)
        draw_text(f"Level  : {level}",         font_md, NEON_CYAN,   WIDTH//2, 275, center=True)
        draw_text(f"Best   : {personal_best}", font_md, NEON_YELLOW, WIDTH//2, 320, center=True)
 
        btn_retry = pygame.Rect(WIDTH//2 - 230, 440, 200, 52)
        btn_menu  = pygame.Rect(WIDTH//2 + 30,  440, 200, 52)
        draw_button("[ RETRY ]",     btn_retry, NEON_GREEN,  NEON_CYAN)
        draw_button("[ MAIN MENU ]", btn_menu,  NEON_PURPLE, NEON_PINK)
        pygame.display.update()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(event.pos): return "retry"
                if btn_menu.collidepoint(event.pos):  return "menu"
        clock.tick(60)
 
# ── Obstacle generation ────────────────────────────────────────────────────────
def generate_obstacles(level, snake_pos):
    count = 3 + (level * 2)
    obstacles = set()
    sx, sy = snake_pos
 
    for _ in range(count * 20):
        if len(obstacles) >= count * 4:
            break
        ox = snap(random.randrange(0, WIDTH - 20))
        oy = snap(random.randrange(40, HEIGHT - 20))
        if abs(ox - sx) <= 60 and abs(oy - sy) <= 60:
            continue
        obstacles.add((ox, oy))
        obstacles.add((ox + SNAKE_BLOCK, oy))
        obstacles.add((ox, oy + SNAKE_BLOCK))
        obstacles.add((ox + SNAKE_BLOCK, oy + SNAKE_BLOCK))
 
    return obstacles
 
# ── Main game ──────────────────────────────────────────────────────────────────
def run_game(username, player_id, personal_best_ref):
    snake_color = tuple(settings["snake_color"])
    current_speed = BASE_SPEED
    score, level = 0, 1
    points_for_next_level = 10
 
    x, y = snap(WIDTH // 2), snap(HEIGHT // 2)
    x_change, y_change = 0, 0
    snake_list = [[x, y]]
    length_of_snake = 1
    obstacles = generate_obstacles(level, (x, y))
 
    def excluded(): return set(map(tuple, snake_list)) | obstacles
 
    def spawn_food():
        fx, fy = random_pos(excluded())
        w = random.choices([1, 3, 5], weights=[70, 20, 10])[0]
        return fx, fy, w, pygame.time.get_ticks()
 
    food_x, food_y, food_weight, food_spawn_time = spawn_food()
 
    px, py = random_pos(excluded())
    poison_x, poison_y, poison_spawn = px, py, pygame.time.get_ticks()
 
    pu_active = False
    pu_x, pu_y, pu_type, pu_spawn = 0, 0, PU_SPEED, 0
    active_effect, effect_start, shield_ready = None, 0, False
 
    food_colors = {1: NEON_PINK, 3: NEON_CYAN, 5: NEON_YELLOW}
 
    running = True
    while running:
        now = pygame.time.get_ticks()
 
        if not pu_active and random.random() < 0.01:
            pu_x, pu_y = random_pos(excluded())
            pu_type = random.choice([PU_SPEED, PU_SLOW, PU_SHIELD])
            pu_spawn, pu_active = now, True
 
        if active_effect in (PU_SPEED, PU_SLOW) and (now - effect_start) > 5000:
            current_speed = BASE_SPEED + (level - 1) * 2
            active_effect = None
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT  and x_change == 0: x_change, y_change = -10, 0
                elif event.key == pygame.K_RIGHT and x_change == 0: x_change, y_change = 10, 0
                elif event.key == pygame.K_UP   and y_change == 0: x_change, y_change = 0, -10
                elif event.key == pygame.K_DOWN and y_change == 0: x_change, y_change = 0, 10
 
        x += x_change
        y += y_change
 
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0 or (x, y) in obstacles:
            if shield_ready:
                if (x, y) in obstacles: x -= x_change; y -= y_change
                else: x = max(0, min(x, WIDTH-10)); y = max(0, min(y, HEIGHT-10))
                shield_ready = False
            else: break
 
        draw_bg()
        if settings.get("grid_overlay"): draw_grid()
 
        # стены — монолитный фиолетовый блок
        for (ox, oy) in obstacles:
            pygame.draw.rect(screen, NEON_PURPLE, (ox, oy, 10, 10))
 
        if now - food_spawn_time > 10000:
            food_x, food_y, food_weight, food_spawn_time = spawn_food()
 
        # еда — монолитный круг
        pygame.draw.circle(screen, food_colors[food_weight], (food_x, food_y), 7)
        # яд — монолитный круг
        pygame.draw.circle(screen, POISON_COL, (poison_x, poison_y), 7)
 
        if pu_active:
            pygame.draw.circle(screen, PU_COLORS[pu_type], (pu_x, pu_y), 8)
            if now - pu_spawn > 8000: pu_active = False
 
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake: del snake_list[0]
 
        for seg in snake_list[:-1]:
            if seg == snake_head:
                if shield_ready: shield_ready = False
                else: running = False
 
        # змея — одинаковый цвет везде
        for seg in snake_list:
            pygame.draw.circle(screen, snake_color, (seg[0], seg[1]), 6)
 
        # HUD
        draw_text(f"SCORE: {score}", font_sm, NEON_CYAN,  10, 8)
        draw_text(f"LVL: {level}",   font_sm, NEON_GREEN, 200, 8)
        if shield_ready:
            draw_text("[ SHIELD ACTIVE ]", font_sm, NEON_ORANGE, WIDTH//2, 8, center=True)
 
        pygame.display.update()
 
        if abs(x - food_x) < EAT_RADIUS and abs(y - food_y) < EAT_RADIUS:
            score += food_weight; length_of_snake += food_weight
            if score >= points_for_next_level:
                level += 1; points_for_next_level += 20
                current_speed = BASE_SPEED + (level - 1) * 3
                obstacles = generate_obstacles(level, (x, y))
            food_x, food_y, food_weight, food_spawn_time = spawn_food()
 
        if abs(x - poison_x) < EAT_RADIUS and abs(y - poison_y) < EAT_RADIUS:
            length_of_snake = max(1, length_of_snake - 2)
            px, py = random_pos(excluded())
            poison_x, poison_y = px, py
 
        if pu_active and abs(x - pu_x) < EAT_RADIUS and abs(y - pu_y) < EAT_RADIUS:
            if pu_type == PU_SPEED:    current_speed += 7; active_effect = PU_SPEED
            elif pu_type == PU_SLOW:   current_speed = max(5, current_speed - 7); active_effect = PU_SLOW
            elif pu_type == PU_SHIELD: shield_ready = True
            effect_start, pu_active = now, False
 
        clock.tick(current_speed)
    return score, level
 
# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    username  = username_screen()
    player_id = get_or_create_player(username) if db_available else None
    pb        = [get_personal_best(player_id) if player_id else 0]
 
    while True:
        action = main_menu()
        if action == "leaderboard": leaderboard_screen()
        elif action == "settings":  settings_screen()
        elif action == "play":
            while True:
                s, l = run_game(username, player_id, pb)
                if player_id:
                    save_game_session(player_id, s, l)
                    pb[0] = get_personal_best(player_id)
                if game_over_screen(s, l, pb[0]) == "menu": break
 
if __name__ == "__main__":
    main()