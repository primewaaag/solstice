import pygame
import pygame_gui
import os
import random
import time

def clear_terminal():
    os.system("cls")
clear_terminal()

pygame.init()
pygame.mixer.init()

WIDTH = 600
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
manager = pygame_gui.UIManager((WIDTH, HEIGHT), "assets/style/theme.json")
pygame.display.set_caption("Solstice")

FPS = 60
clock = pygame.time.Clock()
dt = 0

WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
FUCHSIA = (255, 0, 255)
GRAY = (128, 128, 128)
LIME = (0, 128, 0)
MAROON = (128, 0, 0)
NAVYBLUE = (0, 0, 128)
OLIVE = (128, 128, 0)
PURPLE = (128, 0, 128)
TEAL = (0,128,128)
PINK = (255, 20, 147)


is_running = True # For the Game Loop
main_menu_done = True # For the Main Menu Loop
health_ship = 100 # Per Hit -10 Health
laser_shooting = False # If you can use the Laser Shooter
laser_cooldown = 0.5 # We need a Cooldown to prevent Spamming and lagging
current_shot_time = 0 # Time since last shot
amount_of_enemies = 0 # How many Enemies are on the Screen
enemy_size = 125 # Size of the Enemies
power_orb_active = False # If the Power Orb is active
power_orb_timer = 0 # Timer for the Power Orb
orb_effect_time = 0 # Timer for the Power Orb Effect
POWER_ORB_DURATION = 10 # Duration of the Power Orb Effect
POWER_ORB_RESPAWN = 30 # Time until the Power Orb respawns
health_active = False # If the Health is active
health_timer = 0 # Timer for the Health
HEALTH_RESPAWN = random.randint(30, 45) # Time until the Health respawns
hitboxes = False # Toggle for viewing Hitboxes
killed = 0 # Amount of killed Enemies
bossfight = False # If the Boss Fight is active
boss_speed = 150 # Change for different Boss Speeds
boss_direction = random.choice([-1, 1]) # If moving left or right.
boss_change_timer = 0 # Timer for changing direction
boss_change_space = 1000 # Time until changing direction
boss_health = 1000 # Boss Health
delay_nought_laser = 1 # Delay of the bosses lasers
delay_nought_laser_timer = 0 # Timer for the Delay of the Bosses Lasers
amount_killed = 150 # How many Enemies needed for Boss Fight
how_many_enemies = 5 # How many Enemies can be on the Screen at once
HEALTH_NEEDED_FOR_ACTIVE = 50 # Health needed until Health can spawn
speed_increase_lasers = 0
# Highscore tracking
boss_start_time = 0
current_boss_time = 0
highscore_file = "highscore.txt"

# Load highscore from file
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as f:
        try:
            highscore = float(f.read().strip())
        except:
            highscore = 0
else:
    highscore = 0
# Highscore tracking end

ships = [
    pygame.image.load("assets/main_ship_base/ship_full_health.png").convert_alpha(),
    pygame.image.load("assets/main_ship_base/ship_slight_damaged.png").convert_alpha(),
    pygame.image.load("assets/main_ship_base/ship_damaged.png").convert_alpha(),
    pygame.image.load("assets/main_ship_base/ship_very_damaged.png").convert_alpha(),
]
space_background = pygame.image.load("assets/pictures/space-background.png").convert_alpha()
space_background = pygame.transform.scale(space_background, (WIDTH, HEIGHT))
ships = [pygame.transform.scale(ship, (125, 125)) for ship in ships]
laser_01 = pygame.image.load("assets/lasers/01.png").convert_alpha()
main_menu_picture = pygame.image.load("assets/pictures/MainMenu.png").convert_alpha()
dreadnought_enemy = pygame.image.load("assets/enemies/dreadnought_enemy.png")
dreadnought_enemy = pygame.transform.scale(dreadnought_enemy, (enemy_size, enemy_size))
dreadnought_enemy = pygame.transform.flip(dreadnought_enemy, False, True)
power_orb = pygame.image.load("assets/pictures/PowerOrb.png").convert_alpha()
power_orb = pygame.transform.scale(power_orb, (50, 50))
heart = pygame.image.load("assets/pictures/heart.png").convert_alpha()
heart = pygame.transform.scale(heart, (50, 50))
laser_02 = pygame.image.load("assets/lasers/12.png").convert_alpha()
dreadnought_enemy = pygame.transform.scale(dreadnought_enemy, (200, 200))

ships_position = pygame.Vector2(450, 750)
dreadnought_enemy_position = pygame.Vector2(200, -150)
laser_01_position = pygame.Vector2(ships_position.x + 50, ships_position.y - 20)
laser_02_position = pygame.Vector2(dreadnought_enemy_position.x + 50, dreadnought_enemy_position.y + 20)

alien_talk_1 = pygame.mixer.Sound("assets/sounds/alien-talk-1.wav")
alien_talk_2 = pygame.mixer.Sound("assets/sounds/alien-talk-2.wav")
alien_talk_3 = pygame.mixer.Sound("assets/sounds/alien-talk-3.wav")
scream_sound = pygame.mixer.Sound("assets/sounds/scream.wav")
laser_sound = pygame.mixer.Sound("assets/sounds/shot_fired.wav")

start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((375, 250), (150, 75)),
    text='Play!',
    manager=manager
)
help_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((375, 325), (150, 75)),
    text='Help!',
    manager=manager
)
quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((375, 400), (150, 75)),
                                             text='Quit!',
                                             manager=manager)


def format_image(path):
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    image = pygame.transform.scale(image, (enemy_size, enemy_size))
    return image
def healthbar(surface, x, y, segment_width, height, current_health, max_health, segments):
    segments = segments
    health_per_segment = max_health / segments

    for i in range(segments):
        segment_x = x + i * segment_width
        if current_health > i * health_per_segment:
            pygame.draw.rect(surface, RED, (segment_x, y, segment_width, height))
        pygame.draw.rect(surface, WHITE, (segment_x, y, segment_width, height), 2)


shots = []
enemies_types = [
    format_image("assets/enemies/battlecruiser_enemy.png"), 
    format_image("assets/enemies/bomber_enemy.png"),
    format_image("assets/enemies/fighter_enemy.png"),
    format_image("assets/enemies/frigate_enemy.png"),
    format_image("assets/enemies/scout_enemy.png"),
    format_image("assets/enemies/support_enemy.png"),
    format_image("assets/enemies/torpedo_enemy.png")
]
enemies = []
laser_noughts = []

keys = pygame.key.get_pressed()
pygame.mixer.music.load("assets/sounds/GameSound.mp3")
pygame.mixer.music.play(-1)

# Main Menu Loop
while main_menu_done:
    for event in pygame.event.get():
        manager.process_events(event)  

        if event.type == pygame.QUIT:
            is_running = False
            main_menu_done = False
            pygame.quit()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == start_button:
                main_menu_done = False
            if event.ui_element == quit_button:
                is_running = False
                main_menu_done = False
                clear_terminal()
            if event.ui_element == help_button:
                text = "Controls:\nWASD to Move\nSpace to Shoot\nM to Mute/Unmute\nH to toggle Hitboxes\nEsc to Quit\n\nInfos:\nPick up the Heart to heal +20 Health\nPick up the Power Orb to shoot faster for 10 Seconds\nKill 150 Enemies to trigger the Boss Fight"
                font = pygame.font.Font(None, 33)
                text_surface = font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
                screen.fill(BLACK)
                screen.blit(text_surface, text_rect)
                pygame.display.flip()
                time.sleep(5)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_volume() == 0:
                    pygame.mixer.music.set_volume(1)
                else:
                    pygame.mixer.music.set_volume(0)
            if event.key == pygame.K_h:
                if hitboxes == False:
                    hitboxes = True
                else:
                    hitboxes = False
            if event.key == pygame.K_ESCAPE:
                is_running = False
                main_menu_done = False
                clear_terminal()
            
    manager.update(dt)
    screen.blit(main_menu_picture, (0, 0))
    manager.draw_ui(screen)
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
# End of Main Menu Loop


while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_volume() == 0:
                    pygame.mixer.music.set_volume(1)
                else:
                    pygame.mixer.music.set_volume(0)
            if event.key == pygame.K_h:
                    if hitboxes == False:
                        hitboxes = True
                    else:
                        hitboxes = False
            if not bossfight:
                if event.key == pygame.K_PERIOD:
                    killed += 149
    keys = pygame.key.get_pressed()

    # Movement
    if keys[pygame.K_a]:
        ships_position.x -= 300 * dt
    if keys[pygame.K_d]:
        ships_position.x += 300 * dt
    if keys[pygame.K_w]:
        ships_position.y -= 300 * dt
    if keys[pygame.K_s]:
        ships_position.y += 300 * dt
    if keys[pygame.K_ESCAPE]:
        is_running = False
    # Finished Movement
    # Shooting
    if keys[pygame.K_SPACE] and not laser_shooting:
        laser_sound.play()
        laser_shooting = True
        laser_01_position.x = ships_position.x + 6
        laser_01_position.y = ships_position.y - 20
        shots.append(laser_01_position.copy())
    if laser_shooting:
        current_shot_time += dt
        if current_shot_time >= laser_cooldown:
            laser_shooting = False
            current_shot_time = 0
    # Finished Shooting
    
    # Killing Enemies
    # Finished Killing Enemies

    # Keep Player in Screen
    if ships_position.x < -25:
        ships_position.x = -25
    if ships_position.x > WIDTH - 100:
        ships_position.x = WIDTH - 100
    if ships_position.y < -30:
        ships_position.y = -30
    if ships_position.y > HEIGHT - 95:
        ships_position.y = HEIGHT - 95
    # Finished Keeping Player in Screen

    # Drawing the Stuff
    screen.fill(BLACK)
    player_bar_height = 25
    player_bar_segments = 10
    player_bar_x = 20
    player_bar_y = HEIGHT - player_bar_height - 20
    healthbar(screen, 20, HEIGHT - player_bar_height - 20, 20, player_bar_height, health_ship, 100, player_bar_segments)
    font = pygame.font.Font(None, 30)
    player_text_surface = font.render("Player Health:", True, WHITE)
    player_text_rect = player_text_surface.get_rect(midbottom=(player_bar_x + (player_bar_segments * 20)/2, player_bar_y - 5))
    screen.blit(player_text_surface, player_text_rect)
    if bossfight:
        boss_bar_height = 25
        boss_bar_segments = 10
        boss_bar_x = WIDTH - (boss_bar_segments * 20) - 20
        boss_bar_y = HEIGHT - boss_bar_height - 20

        # Draw Boss Health
        healthbar(
            screen,
            boss_bar_x,
            boss_bar_y,
            20,  # segment width
            boss_bar_height,
            boss_health,
            1000,  # max boss health
            boss_bar_segments
        )

        # Draw text above Boss Health
        boss_text_surface = font.render("Boss Health:", True, WHITE)
        boss_text_rect = boss_text_surface.get_rect(midbottom=(boss_bar_x + (boss_bar_segments * 20)/2, boss_bar_y - 5))
        screen.blit(boss_text_surface, boss_text_rect)
    # Shots
    for shot in shots:
        shot.y -= 500 * dt
        screen.blit(laser_01, shot)
    # Shots End
    # Main Ship
    if health_ship >= 75:
        screen.blit(ships[0], ships_position)
    elif health_ship >= 50:
        screen.blit(ships[1], ships_position)
    elif health_ship >= 25:
        screen.blit(ships[2], ships_position)
    elif health_ship > 0:
        screen.blit(ships[3], ships_position)
    else:
        pygame.mixer.music.stop()
        scream_sound.play()
        text = "You Died!"
        font = pygame.font.Font(None, 74)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.fill(BLACK)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(3)
        is_running = False
        continue
    # Main Ship End
    # Power Orbs
    if not bossfight:
        if health_ship < 80:
            if not power_orb_active:
                power_orb_timer += dt
                if power_orb_timer >= POWER_ORB_RESPAWN:
                    where_to_spawn = random.randint(50, WIDTH - 50)
                    power_orb_rect = pygame.Rect(where_to_spawn, -75, 50, 50)
                    power_orb_active = True
                    power_orb_timer = 0
            if power_orb_active:
                power_orb_rect.y += 100 * dt
                screen.blit(power_orb, (power_orb_rect.x, power_orb_rect.y))
                ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125)
                if power_orb_rect.colliderect(ship_rect):
                    laser_cooldown = 0.25
                    orb_effect_time = 0
                    power_orb_active = False
    if laser_cooldown == 0.25:
                orb_effect_time += dt
                if orb_effect_time >= POWER_ORB_DURATION:
                    laser_cooldown = 0.5
    # End Power Orbs
    if not bossfight:
        if health_ship <= HEALTH_NEEDED_FOR_ACTIVE:
            if not health_active:
                health_timer += dt
                if health_timer >= HEALTH_RESPAWN:
                    where_to_spawn = random.randint(50, WIDTH - 50)
                    health_rect = pygame.Rect(where_to_spawn, -75, 50, 50)
                    health_active = True
                    health_timer = 0
            if health_active:
                health_rect.y += 100 * dt
                screen.blit(heart, (health_rect.x, health_rect.y))
                ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125)
                if health_rect.colliderect(ship_rect):
                    health_ship += 20
                    if health_ship > 100:
                        health_ship = 100
                    health_active = False
    # Drawing Enemies and controlling Enemies
    if not bossfight:
        if amount_of_enemies < how_many_enemies:
            enemy_type = random.choice(enemies_types)
            where_to_spawn = random.randint(0, WIDTH - 75)
            enemy_position = pygame.Vector2(where_to_spawn, -75)
            enemies.append((enemy_type, enemy_position))
            amount_of_enemies += 1
        for enemy in enemies:
            if enemy[1].y > HEIGHT:
                enemies.remove(enemy)
                amount_of_enemies -= 1
                health_ship -= 10
            enemy[1].y += 100 * dt
            screen.blit(enemy[0], enemy[1]) # Takes from Enemy List the inner Enemy List the Type of Enemy (Picture) and the Position
        # Drawing Enemies and controlling Enemies End

    # Collision
    if not bossfight:
        for enemy in enemies:
            for shot in shots:
                enemy_rect = pygame.Rect(enemy[1].x, enemy[1].y, enemy_size, enemy_size).scale_by(0.63)
                shot_rect = pygame.Rect(shot.x, shot.y, 121, 126).scale_by(0.25)
                collides = enemy_rect.colliderect(shot_rect)
                if collides:
                    enemies.remove(enemy)
                    amount_of_enemies -= 1
                    killed += 1
                    shots.remove(shot)
    if not bossfight:
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[1].x, enemy[1].y, enemy_size, enemy_size).scale_by(0.63)
            ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125).scale_by(0.63)
            collides = enemy_rect.colliderect(ship_rect)
            if collides:
                enemies.remove(enemy)
                amount_of_enemies -= 1
                killed += 1
                health_ship -= 10
    # Boss Fight
    if killed >= amount_killed:
        screen.fill(BLACK)
        text = "Boss Fight!"
        font = pygame.font.Font(None, 74)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(3)
        killed = 0
        bossfight = True
        amount_of_enemies = 0
        dreadnought_enemy_position = pygame.Vector2(WIDTH/2 - enemy_size/2, 0)

        boss_start_time = time.time()

    # Boss Fight End
    # Collision
    if bossfight:
        boss_change_timer += dt
        if boss_change_timer >= boss_change_space:
            boss_direction = random.choice([-1, 1])
            boss_change_timer = 0
        
        dreadnought_enemy_position.x += boss_direction * boss_speed * dt

        if dreadnought_enemy_position.x < -50:
            dreadnought_enemy_position.x = -50
            boss_direction = 1
        if dreadnought_enemy_position.x > WIDTH - 150:
            dreadnought_enemy_position.x = WIDTH - 150
            boss_direction = -1

        screen.blit(dreadnought_enemy, dreadnought_enemy_position)

        if hitboxes:
            boss_rect = pygame.Rect(dreadnought_enemy_position.x, dreadnought_enemy_position.y, 200, 200).scale_by(0.63)
            pygame.draw.rect(screen, PURPLE, boss_rect, 1, border_radius=2) #- Remove # if you want to see Hitbox
    if hitboxes:
        ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125).scale_by(0.63)
        pygame.draw.rect(screen, BLUE, ship_rect, 1, border_radius=2) #- Remove # if you want to see Hitbox
        for shot in shots:
            shot_rect = pygame.Rect(shot.x, shot.y, 121, 126).scale_by(0.25)
            pygame.draw.rect(screen, GREEN, shot_rect, 1, border_radius=2) #- Remove # if you want to see Hitbox
    if hitboxes:
        if not bossfight:
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy[1].x, enemy[1].y, enemy_size, enemy_size).scale_by(0.63)
                pygame.draw.rect(screen, RED, enemy_rect, 1, border_radius=2) #- Remove # if you want to see Hitbox
    if bossfight:
        for shot in shots:
            boss_rect = pygame.Rect(dreadnought_enemy_position.x, dreadnought_enemy_position.y, 200, 200).scale_by(0.63)
            shot_rect = pygame.Rect(shot.x, shot.y, 121, 126).scale_by(0.25)
            if boss_rect.colliderect(shot_rect):
                boss_health -= 10
                shots.remove(shot)
        if bossfight:
            laser_02_position.x = dreadnought_enemy_position.x
            laser_02_position.y = dreadnought_enemy_position.y 
            delay_nought_laser_timer += dt
            if delay_nought_laser_timer >= delay_nought_laser:
                delay_nought_laser_timer = 0
                laser_noughts.append(laser_02_position.copy())
        for laser in laser_noughts:
            laser.y += 400 * dt
            screen.blit(laser_02, laser)
            laser_rect = pygame.Rect(laser.x, laser.y, 121, 126).inflate(-48, 33) # ⬇️
            laser_rect.centerx += 12 # Change these 3 Value to move the Hitbox
            laser_rect.centery += 66 # ⬆️
            ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125).scale_by(0.63)
            if laser_rect.colliderect(ship_rect):
                health_ship -= 10
                laser_noughts.remove(laser)
            speed_increase_lasers += dt
            if hitboxes:
                pygame.draw.rect(screen, PINK, laser_rect, 1, border_radius=2) #- Remove # if you want to see Hitbox
    if bossfight:
        current_boss_time = time.time() - boss_start_time
    
        # Draw current boss fight time
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"Time: {int(current_boss_time)}s", True, WHITE)
        screen.blit(text_surface, (10, 10))
        
        # Draw current highscore
        text_surface2 = font.render(f"Highscore: {int(highscore)}s", True, WHITE)
        screen.blit(text_surface2, (10, 40))
    # When boss dies
    if boss_health <= 0:
        bossfight = False

        # Update highscore if current boss time is faster (smaller) than previous highscore
        if highscore == 0 or current_boss_time < highscore:
            highscore = current_boss_time
            with open(highscore_file, "w") as f:
                f.write(str(highscore))

        screen.fill(BLACK)
        text = "You Win!"
        font = pygame.font.Font(None, 74)
        text_surface = font.render(text, True, GREEN)
        text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(3)
        is_running = False
        continue



    boss_rect = pygame.Rect(dreadnought_enemy_position.x, dreadnought_enemy_position.y, 200, 200).scale_by(0.63)
    ship_rect = pygame.Rect(ships_position.x, ships_position.y, 125, 125).scale_by(0.63)
    if boss_rect.colliderect(ship_rect):
        health_ship -= 10
        dreadnought_enemy_position.y = 0
        dreadnought_enemy_position.x = random.randint(0, WIDTH - 200)
    if delay_nought_laser > 0.5:
        if speed_increase_lasers >= 37.5:
            delay_nought_laser -= 0.1
            speed_increase_lasers = 0
    
    pygame.display.flip()

    # Hit Boxes
    # Finished Drawing the Stuff
    
    # Makes the Game not get cooked by to many things in shots list
    for shot in shots:
            if shot.y < -100:
                shots.remove(shot)
    for laser in laser_noughts:
            if laser.y > HEIGHT + 100:
                laser_noughts.remove(laser)
    # Or else it would crash or laggggg.
    # Cap the Frame Rate
    dt = clock.tick(FPS) / 1000
    # No Cap btw ;)
pygame.quit()