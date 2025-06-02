import pyxel
import math
import random

# --- Screen Size ---
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Define player movable area width and height
PLAY_AREA_WIDTH = 60
PLAY_AREA_HEIGHT = 62 

# Calculate top-left coordinates of the play area (centered on screen, extended 2px downwards)
PLAY_AREA_X = (SCREEN_WIDTH - PLAY_AREA_WIDTH) // 2
PLAY_AREA_Y = (SCREEN_HEIGHT - (60)) // 2 - 1 # Use original PLAY_AREA_HEIGHT (60) to calculate and fix Y coordinate

# --- Enemy Class ---
class Enemy:
    def __init__(self, player_x, player_y):
        spawn_edge = random.choice(["top", "bottom", "left", "right"])
        self.size = 8 # Enemy image size
        self.x = 0
        self.y = 0

        if spawn_edge == "top":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(-self.size * 2, -self.size)
        elif spawn_edge == "bottom":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(SCREEN_HEIGHT + self.size, SCREEN_HEIGHT + self.size * 2)
        elif spawn_edge == "left":
            self.x = random.randint(-self.size * 2, -self.size)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)
        elif spawn_edge == "right":
            self.x = random.randint(SCREEN_WIDTH + self.size, SCREEN_WIDTH + self.size * 2)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)

        self.speed = 0.5
        self.hp = 1 # HP for normal enemies
        self.last_hit_frame = -1 # Frame when last hit

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self):
        pyxel.blt(int(self.x), int(self.y), 0, 16, 8, self.size, self.size, 0)

    def is_outside_screen(self):
        margin = 20
        return (self.x < -margin or self.x > SCREEN_WIDTH + margin or
                self.y < -margin or self.y > SCREEN_HEIGHT + margin)

    def take_damage(self):
        if pyxel.frame_count == self.last_hit_frame:
            return False # Already processed damage this frame

        self.last_hit_frame = pyxel.frame_count
        self.hp -= 1
        return self.hp <= 0

# --- ShotGhost Class (New) ---
class ShotGhost:
    def __init__(self, player_x, player_y):
        spawn_edge = random.choice(["top", "bottom", "left", "right"])
        self.size = 16 # Image size 16x8
        self.x = 0
        self.y = 0

        if spawn_edge == "top":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(-self.size * 2, -self.size)
        elif spawn_edge == "bottom":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(SCREEN_HEIGHT + self.size, SCREEN_HEIGHT + self.size * 2)
        elif spawn_edge == "left":
            self.x = random.randint(-self.size * 2, -self.size)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)
        elif spawn_edge == "right":
            self.x = random.randint(SCREEN_WIDTH + self.size, SCREEN_WIDTH + self.size * 2)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)

        self.base_speed = 0.3 # Slower max speed than normal ghosts
        self.current_speed = 0.0
        self.hp = 1
        self.last_hit_frame = -1 # Frame when last hit

        self.state = "ACCEL" # ACCEL, DECEL, IDLE
        self.state_timer = 0
        self.state_duration_frames = 30 # 1 second (30 frames)

        self.bullet_fired = False # Flag to fire bullet only once while idle

    def update(self, player_x, player_y):
        self.state_timer += 1

        if self.state == "ACCEL":
            t = self.state_timer / self.state_duration_frames
            self.current_speed = self.base_speed * min(1.0, t)
            if self.state_timer >= self.state_duration_frames:
                self.state = "DECEL"
                self.state_timer = 0
                self.bullet_fired = False # Reset to allow firing bullet in new phase

        elif self.state == "DECEL":
            t = self.state_timer / self.state_duration_frames
            self.current_speed = self.base_speed * (1.0 - min(1.0, t))
            if self.state_timer >= self.state_duration_frames:
                self.state = "IDLE"
                self.state_timer = 0

        elif self.state == "IDLE":
            self.current_speed = 0.0
            if not self.bullet_fired:
                # Fire bullet (handled by App class via return value)
                self.bullet_fired = True
            
            if self.state_timer >= self.state_duration_frames: # Idle time also 1 second (30 frames)
                self.state = "ACCEL"
                self.state_timer = 0

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0 and self.current_speed > 0: # Don't move when idle
            self.x += dx / dist * self.current_speed
            self.y += dy / dist * self.current_speed
    
    def draw(self):
        # Flip image according to direction
        player_center_x = pyxel.width // 2
        flip_x = 1
        if self.x > player_center_x: # If to the right of player, face left
            flip_x = -1
        
        pyxel.blt(int(self.x), int(self.y), 0, 32, 0, self.size * flip_x, 8, 0)

    def is_outside_screen(self):
        margin = 20
        return (self.x < -margin or self.x > SCREEN_WIDTH + margin or
                self.y < -margin or self.y > SCREEN_HEIGHT + margin)

    def take_damage(self):
        if pyxel.frame_count == self.last_hit_frame:
            return False # Already processed damage this frame

        self.last_hit_frame = pyxel.frame_count
        self.hp -= 1
        return self.hp <= 0

# --- ShieldGhost Class (New) ---
class ShieldGhost:
    def __init__(self, player_x, player_y):
        spawn_edge = random.choice(["top", "bottom", "left", "right"])
        self.size = 8 # Image size 8x8
        self.x = 0
        self.y = 0

        if spawn_edge == "top":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(-self.size * 2, -self.size)
        elif spawn_edge == "bottom":
            self.x = random.randint(-self.size, SCREEN_WIDTH)
            self.y = random.randint(SCREEN_HEIGHT + self.size, SCREEN_HEIGHT + self.size * 2)
        elif spawn_edge == "left":
            self.x = random.randint(-self.size * 2, -self.size)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)
        elif spawn_edge == "right":
            self.x = random.randint(SCREEN_WIDTH + self.size, SCREEN_WIDTH + self.size * 2)
            self.y = random.randint(-self.size, SCREEN_HEIGHT)

        self.initial_speed = 0.4 # Slightly slower than normal ghosts
        self.rush_speed = 0.8 # Faster than normal ghosts
        self.current_speed = self.initial_speed
        
        self.hp = 2 # 1 to break shield, 1 to defeat body
        self.last_hit_frame = -1 # Frame when last hit

        self.state = "SHIELDED" # SHIELDED, DAMAGED_BLINK, RUSH
        self.state_timer = 0
        self.blink_duration_frames = 30 # 1 second (30 frames)
        self.blink_interval = 5 # Blink interval
        self.player_blink_timer = 0 # Timer for blink display

    def update(self, player_x, player_y):
        if self.state == "DAMAGED_BLINK":
            self.state_timer += 1
            self.player_blink_timer += 1 # Update blink timer
            if self.player_blink_timer >= self.blink_interval * 2:
                self.player_blink_timer = 0

            self.current_speed = 0.0 # Stop
            if self.state_timer >= self.blink_duration_frames:
                self.state = "RUSH"
                self.current_speed = self.rush_speed
                self.state_timer = 0
                self.player_blink_timer = 0 # Reset blink timer
        
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.x += dx / dist * self.current_speed
            self.y += dy / dist * self.current_speed

    def draw(self):
        u = 0
        v = 0
        # Flip image according to direction
        player_center_x = pyxel.width // 2
        flip_x = 1
        if self.x > player_center_x: # If to the right of player, face left
            flip_x = -1

        if self.state == "SHIELDED":
            u = 32
            v = 16
        elif self.state == "DAMAGED_BLINK" or self.state == "RUSH":
            u = 40
            v = 16

        # Skip drawing only while blinking
        if self.state == "DAMAGED_BLINK" and self.player_blink_timer % (self.blink_interval * 2) < self.blink_interval:
            return

        pyxel.blt(int(self.x), int(self.y), 0, u, v, self.size * flip_x, self.size, 0)

    def is_outside_screen(self):
        margin = 20
        return (self.x < -margin or self.x > SCREEN_WIDTH + margin or
                self.y < -margin or self.y > SCREEN_HEIGHT + margin)

    def take_damage(self):
        if self.state == "DAMAGED_BLINK": # Invincible while blinking
            return False

        if pyxel.frame_count == self.last_hit_frame:
            return False # Already processed damage this frame

        self.last_hit_frame = pyxel.frame_count
        self.hp -= 1
        if self.hp == 1 and self.state == "SHIELDED": # First damage taken
            self.state = "DAMAGED_BLINK"
            self.state_timer = 0
            self.player_blink_timer = 0
            return False # Not defeated yet
        
        return self.hp <= 0 # Finally defeated

# --- Attack Class ---
class Attack:
    # player_x, player_y are player position when attack is generated
    # initial_x_offset, initial_y_offset are relative spawn positions from player
    # initial_delay is delay in frames until attack appears
    def __init__(self, player_x, player_y, initial_x_offset, initial_y_offset, facing_right, initial_delay=0):
        self.width = 8
        self.height = 8
        self.facing_right = facing_right
        self.duration = 10 # Basic attack display duration
        self.life = self.duration # Remaining attack lifespan
        self.initial_delay = initial_delay # Initial delay in frames
        self.spawn_frame = pyxel.frame_count # Frame when attack was spawned

        # Remember relative offsets from player
        self.relative_offset_x = initial_x_offset
        self.relative_offset_y = initial_y_offset

        # Image offset depending on attack direction
        if self.facing_right:
            self.image_offset_x = 8
        else:
            self.image_offset_x = -self.width
        self.image_offset_y = 0

        # Calculate initial display position (position is calculated immediately even with delay)
        self.display_x = player_x + self.relative_offset_x + self.image_offset_x
        self.display_y = player_y + self.relative_offset_y + self.image_offset_y

    def update(self, player_x, player_y):
        # Don't decrease life during delay period
        if pyxel.frame_count < self.spawn_frame + self.initial_delay:
            # Follow player even during delay period
            self.display_x = player_x + self.relative_offset_x + self.image_offset_x
            self.display_y = player_y + self.relative_offset_y + self.image_offset_y
            return

        self.life -= 1
        # Update display position based on player's current position and relative offset
        self.display_x = player_x + self.relative_offset_x + self.image_offset_x
        self.display_y = player_y + self.relative_offset_y + self.image_offset_y

    def draw(self):
        # Don't draw during delay period or if life is exhausted
        if pyxel.frame_count < self.spawn_frame + self.initial_delay or self.life <= 0:
            return

        if self.facing_right:
            pyxel.blt(int(self.display_x), int(self.display_y) ,0, 24, 0, self.width, self.height, 0)
        else:
            pyxel.blt(int(self.display_x), int(self.display_y) ,0, 24, 0, -self.width, self.height, 0)

    def is_alive(self):
        # Consider "alive" even during delay period, "dead" when life is exhausted
        return self.life > 0 or pyxel.frame_count < self.spawn_frame + self.initial_delay

    def check_collision(self, enemy):
        # Don't perform collision detection during delay period
        if pyxel.frame_count < self.spawn_frame + self.initial_delay:
            return False

        attack_left = self.display_x
        attack_right = self.display_x + self.width
        attack_top = self.display_y
        attack_bottom = self.display_y + self.height

        enemy_left = enemy.x
        enemy_right = enemy.x + enemy.size
        enemy_top = enemy.y
        enemy_bottom = enemy.y + enemy.size

        return (attack_left < enemy_right and
                attack_right > enemy_left and
                attack_top < enemy_bottom and
                attack_bottom > enemy_top)

# --- ExperienceOrb Class ---
class ExperienceOrb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1 # Visual radius of yellow dot remains 1
        self.collision_radius = 4 # Set larger radius for collision detection
        self.color = pyxel.COLOR_YELLOW # Set color to yellow
        self.value = 1 # Amount of experience (placeholder)
        self.attraction_speed = 0.5 # Attraction speed (orb's inherent speed)

    def update(self, player_x, player_y, player_attraction_range): # Add player coordinates and attraction range as arguments
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # If player is within attraction range, move orb towards player
        if dist < player_attraction_range and dist != 0:
            self.x += dx / dist * self.attraction_speed
            self.y += dy / dist * self.attraction_speed

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, self.color) # Use visual radius

    def get_rect(self):
        # Return rectangle for collision detection (generate rectangle based on collision_radius)
        return (self.x - self.collision_radius, self.y - self.collision_radius, self.collision_radius * 2, self.collision_radius * 2)

# --- Satellite Class (New) ---
class Satellite:
    def __init__(self, player_x, player_y, radius, rotation_speed):
        self.radius = radius # Rotation radius from player
        self.rotation_speed = rotation_speed # Rotation speed (degrees/frame)
        self.angle = random.uniform(0, 360) # Set initial angle randomly
        self.size = 8 # Satellite drawing size and collision size to 8x8 to match image

        # Drawing position (updated every frame in update)
        self.display_x = 0
        self.display_y = 0

    def update(self, player_x, player_y):
        self.angle = (self.angle + self.rotation_speed) % 360
        # Calculate orbit from player's center + specified offset (center is 4px because image size is 8x8)
        self.display_x = player_x + self.radius * math.cos(math.radians(self.angle)) + 4
        self.display_y = player_y + self.radius * math.sin(math.radians(self.angle)) + 4

    def draw(self):
        # Draw satellite with specified image (adjust blt XY so center is display_x, display_y)
        pyxel.blt(int(self.display_x - self.size / 2), int(self.display_y - self.size / 2), 0, 24, 48, self.size, self.size, 0)

    def get_rect(self):
        # Return rectangle for collision detection (adjusted to image size 8x8)
        return (self.display_x - self.size / 2, self.display_y - self.size / 2, self.size, self.size)

# --- Bullet Class (New) ---
class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=2, size=8, initial_delay=0, is_enemy_bullet=False): # Add is_enemy_bullet flag
        self.x = x
        self.y = y
        self.size = size # Set to 8 to match image size
        self.speed = speed
        self.life = 120 # Max lifespan (frames)
        self.initial_delay = initial_delay # Initial delay in frames
        self.spawn_frame = pyxel.frame_count # Frame when bullet was spawned
        self.is_enemy_bullet = is_enemy_bullet # Whether it's an enemy bullet

        # Calculate direction vector to target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist != 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else: # If target is at the same position, don't move
            self.vx = 0
            self.vy = 0

    def update(self):
        # Don't move during delay period
        if pyxel.frame_count < self.spawn_frame + self.initial_delay:
            return

        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        # Don't draw during delay period or if life is exhausted
        if pyxel.frame_count < self.spawn_frame + self.initial_delay or self.life <= 0:
            return
        
        u_img = 16 # U coordinate for player bullet
        v_img = 48 # V coordinate for player bullet
        if self.is_enemy_bullet:
            u_img = 32 # U coordinate for enemy bullet
            v_img = 8  # V coordinate for enemy bullet
            # Enemy bullet is 4x4, so adjust blt size (but draw central 4x4 of 8x8 image)
            pyxel.blt(int(self.x - 2), int(self.y - 2), 0, u_img, v_img, 4, 4, 0)
        else:
            # Draw bullet with specified image (adjust blt XY so center is x, y)
            pyxel.blt(int(self.x - self.size / 2), int(self.y - self.size / 2), 0, u_img, v_img, self.size, self.size, 0)


    def get_rect(self):
        # Return rectangle for collision detection (adjusted to image size)
        if self.is_enemy_bullet:
            return (self.x - 2, self.y - 2, 4, 4) # Enemy bullet is 4x4
        else:
            return (self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)

    def is_alive(self):
        # Whether it's off screen or life is exhausted
        is_off_screen = (self.x < -self.size or self.x > SCREEN_WIDTH + self.size or
                         self.y < -self.size or self.y > SCREEN_HEIGHT + self.size)
        return self.life > 0 and not is_off_screen

# --- Meteor Class (New) ---
class Meteor:
    def __init__(self, start_x, start_y, target_x, target_y, fly_duration, explode_duration, initial_delay=0):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.fly_duration = fly_duration # Frames for flight
        self.explode_duration = explode_duration # Frames for explosion display
        self.spawn_frame = pyxel.frame_count # Frame when spawned
        self.initial_delay = initial_delay # Initial delay in frames

        self.state = "FLYING" # "FLYING", "EXPLODING", "DONE"
        self.current_frame_in_state = 0 # Elapsed frames in each state

        self.current_x = start_x
        self.current_y = start_y
        self.current_size = 0 # Expand during flight

        self.image_meteor_u = 16
        self.image_meteor_v = 16
        self.image_explosion_u = 16
        self.image_explosion_v = 32
        self.image_width = 16
        self.image_height = 16

        self.impact_x = 0 # X coordinate at impact
        self.impact_y = 0 # Y coordinate at impact

    def update(self):
        # Don't update during delay period
        if pyxel.frame_count < self.spawn_frame + self.initial_delay:
            return

        self.current_frame_in_state += 1

        if self.state == "FLYING":
            t = self.current_frame_in_state / self.fly_duration
            if t >= 1.0:
                self.state = "EXPLODING"
                self.current_frame_in_state = 0
                self.impact_x = self.target_x
                self.impact_y = self.target_y
                pyxel.play(0, 4) # Play meteor impact sound
            else:
                # Calculate position with linear interpolation
                self.current_x = self.start_x + (self.target_x - self.start_x) * t
                self.current_y = self.start_y + (self.target_y - self.start_y) * t
                # Expand size (e.g., from 0 to image_width)
                self.current_size = int(self.image_width * t)
                if self.current_size < 1: self.current_size = 1 # Ensure minimum size

        elif self.state == "EXPLODING":
            if self.current_frame_in_state >= self.explode_duration:
                self.state = "DONE"

    def draw(self):
        # Don't draw during delay period or if life is exhausted
        if pyxel.frame_count < self.spawn_frame + self.initial_delay or self.state == "DONE":
            return

        if self.state == "FLYING":
            # Draw meteor (expand based on center)
            draw_x = int(self.current_x - self.current_size / 2)
            draw_y = int(self.current_y - self.current_size / 2)
            pyxel.blt(draw_x, draw_y, 0,
                      self.image_meteor_u, self.image_meteor_v,
                      self.image_width, self.image_height, 0)
        elif self.state == "EXPLODING":
            # Draw explosion
            draw_x = int(self.impact_x - self.image_width / 2)
            draw_y = int(self.impact_y - self.image_height / 2)
            pyxel.blt(draw_x, draw_y, 0,
                      self.image_explosion_u, self.image_explosion_v,
                      self.image_width, self.image_height, 0)

    def is_alive(self):
        # Consider "alive" even during delay period
        return self.state != "DONE" or pyxel.frame_count < self.spawn_frame + self.initial_delay

    def get_explosion_rect(self):
        if self.state == "EXPLODING":
            # Collision detection range for explosion (use explosion image size)
            return (self.impact_x - self.image_width / 2,
                    self.impact_y - self.image_height / 2,
                    self.image_width,
                    self.image_height)
        return None


# --- App Class ---
class App:
    def __init__(self):
        # Initialize Pyxel with FPS set to 30
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Ghost Survivor", fps=30)

        try:
            pyxel.load("my_resource.pyxres")
        except Exception as e:
            print(f"Failed to load resource file 'my_resource.pyxres': {e}")
            print("Creating dummy resources.")
            pyxel.image(0).rect(16, 0, 8, 8, 7) # Player (dummy)
            pyxel.image(0).rect(16, 8, 8, 8, 8) # Enemy (dummy)
            pyxel.image(0).rect(24, 0, 8, 8, 10) # Attack (dummy)
            # Dummy images for meteor and explosion
            pyxel.image(0).rect(16, 16, 16, 16, pyxel.COLOR_BROWN) # Meteor (dummy)
            pyxel.image(0).circb(24, 40, 7, pyxel.COLOR_ORANGE) # Explosion (dummy)
            pyxel.image(0).circ(24, 40, 5, pyxel.COLOR_YELLOW) # Explosion center (dummy)
            # Add dummy images for bullet and satellite
            pyxel.image(0).rect(16, 48, 8, 8, pyxel.COLOR_WHITE) # Player bullet (dummy)
            pyxel.image(0).rect(24, 48, 8, 8, pyxel.COLOR_CYAN)  # Satellite (dummy)
            # Dummy images for new enemies
            pyxel.image(0).rect(32, 0, 16, 8, pyxel.COLOR_PURPLE) # Shot Ghost (dummy)
            pyxel.image(0).rect(32, 8, 4, 4, pyxel.COLOR_DARKBLUE) # Shot Ghost bullet (dummy)
            pyxel.image(0).rect(32, 16, 8, 8, pyxel.COLOR_GRAY) # Shield Ghost (dummy)
            pyxel.image(0).rect(40, 16, 8, 8, pyxel.COLOR_RED) # Shield Ghost after damage (dummy)


            pyxel.sound(0).set("c2", "t", "7", "s", 10) # Walking sound
            pyxel.sound(1).set("e2", "p", "7", "s", 10) # Damage sound
            pyxel.sound(2).set("g2", "n", "7", "s", 10) # Enemy defeated sound / Explosion sound
            pyxel.sound(3).set("a3", "t", "7", "s", 5)  # EXP Orb acquisition sound (new)
            pyxel.sound(4).set("c1", "s", "7", "v", 10) # Meteor impact sound (new)

        # No PyxelUniversalFont
        self.font_writer = None

        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x = PLAY_AREA_X + PLAY_AREA_WIDTH // 2 - 4
        self.player_y = PLAY_AREA_Y + PLAY_AREA_HEIGHT // 2 - 4
        self.facing_right = True
        self.step_interval = 4
        self.step_timer = 0
        self.enemies = [] # Normal enemies
        self.shot_ghosts = [] # List of Shot Ghosts
        self.shield_ghosts = [] # List of Shield Ghosts
        self.enemy_spawn_timer = 0
        self.base_enemy_spawn_interval = 30 # Base enemy spawn interval
        self.attacks = []
        self.attack_timer = 0
        self.base_attack_interval = 30 # Base attack interval
        self.attack_interval = self.base_attack_interval # Current attack interval
        self.experience_orbs = [] # List of experience orbs
        self.bullets = [] # List of player bullet objects
        self.enemy_bullets = [] # List of enemy bullet objects
        self.meteors = [] # List of meteor objects

        self.hp = 20 # Set initial HP to 20
        self.max_hp = 20 # Set max HP to 20
        self.is_game_over = False
        self.is_game_clear = False # Add game clear flag
        self.invincible_timer = 0
        self.invincible_duration = 60
        self.player_blink_timer = 0
        self.player_blink_interval = 5

        self.kill_count = 0
        self.exp = 0 # Add experience variable
        self.current_level = 1 # Current level
        self.exp_to_next_level = 3 # Set experience needed for next level up to 3

        # Game state management
        self.game_state = "PLAYING" # "PLAYING", "LEVEL_UP_MENU", "GAME_CLEAR"

        # Player stats
        self.player_base_speed = 1.0 # Base movement speed
        self.player_speed = self.player_base_speed # Current movement speed
        self.player_attack_power = 1 # Player attack power (affects kill count here)
        self.exp_attraction_range = 5 # Experience attraction range

        # New skill related variables
        self.attacks_per_interval = 1 # For N-Sword Style: Number of attack objects generated per attack
        self.can_spawn_bullet = False # For Bullet: Can fire bullets
        self.bullet_spawn_timer = 0
        self.bullet_spawn_interval = 45 # Shorten bullet firing interval (90 -> 45)
        self.bullets_per_shot = 0 # Number of bullets fired at once
        self.satellites = [] # List of satellite objects
        self.satellite_base_radius = 15 # Satellite rotation radius
        self.can_spawn_meteor = False # For Meteor: Can activate meteor
        self.meteor_spawn_timer = 0
        self.meteor_spawn_interval = 300 # Halve meteor activation interval (10 seconds = 600 frames -> 5 seconds = 300 frames)
        self.meteors_per_strike = 0 # Number of meteors falling per strike

        # Game time management
        self.game_duration_frames = 5 * 60 * 30 # 5 minutes (frames at 30FPS)
        self.game_elapsed_frames = 0

        # For time announcements
        self.alert_timings = {240, 180, 120, 60, 30, 15, 5, 3, 2, 1} # Remaining seconds
        self.triggered_alerts = set() # Record already announced times
        self.alert_message = None
        self.alert_display_timer = 0
        self.alert_display_duration = 30 # Announcement display duration (1 second = 30 frames)

        # Enemy difficulty increase
        self.enemies_per_spawn = 1 # Number of enemies spawned per spawn
        self.next_difficulty_increase_time_for_spawn_amount = 60 * 30 # First spawn amount increase after 1 minute (30FPS)

        # For skill selection menu (list of all skills)
        self.all_skill_options = [
            "Dash",
            "Rapid Attack",
            "Magnet",
            "Heal",
            "Multi-Sword",
            "Bullet",
            "Satellite",
            "Meteor"
        ]
        self.current_skill_options = [] # Currently displayed skill options
        self.selected_skill_index = 0

        # Rainbow colors for game clear
        self.rainbow_colors = [
            pyxel.COLOR_RED, pyxel.COLOR_ORANGE, pyxel.COLOR_YELLOW,
            pyxel.COLOR_GREEN, pyxel.COLOR_CYAN, pyxel.COLOR_PURPLE, pyxel.COLOR_PINK
        ]

    def update(self):
        # Allow resetting at any time with R key or X key (mapped to virtual gamepad's Y button)
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y): # Use KEY_X for X button
            self.reset_game()
            return

        # Stop further updates if game over or game clear
        if self.is_game_over or self.is_game_clear:
            return

        # Update game timer (only progresses in PLAYING state)
        if self.game_state == "PLAYING":
            self.game_elapsed_frames += 1

        # Game clear check
        if self.game_elapsed_frames >= self.game_duration_frames and not self.is_game_clear:
            self.is_game_clear = True
            self.game_state = "GAME_CLEAR"
            # Clear all enemies and bullets when game is cleared
            self.enemies = []
            self.shot_ghosts = []
            self.shield_ghosts = []
            self.enemy_bullets = []
            self.bullets = []
            self.attacks = []
            self.satellites = []
            self.meteors = []
            return # Stop updating after game clear

        # Calculate remaining time (seconds)
        # pyxel.frame_count progresses at 30FPS, so divide by 30 to convert to seconds
        remaining_seconds = max(0, (self.game_duration_frames - self.game_elapsed_frames) // 30)

        # Time announcement
        if remaining_seconds in self.alert_timings and remaining_seconds not in self.triggered_alerts:
            if remaining_seconds >= 60:
                self.alert_message = f"{remaining_seconds // 60} min left!"
            else:
                self.alert_message = f"{remaining_seconds} sec left!"
            self.alert_display_timer = self.alert_display_duration
            self.triggered_alerts.add(remaining_seconds)

        if self.alert_display_timer > 0:
            self.alert_display_timer -= 1
        else:
            self.alert_message = None # Clear message when timer expires


        # Update processing according to game state
        if self.game_state == "PLAYING":
            moving = False
            # Player movement using keyboard and virtual gamepad D-Pad
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                self.player_x -= self.player_speed
                self.facing_right = False
                moving = True
            elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                self.player_x += self.player_speed
                self.facing_right = True
                moving = True
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                self.player_y -= self.player_speed
                moving = True
            elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                self.player_y += self.player_speed
                moving = True

            if moving:
                self.step_timer -= 1
                if self.step_timer <= 0:
                    pyxel.play(0, 0)
                    self.step_timer = self.step_interval
            else:
                self.step_timer = 0

            player_display_width = 8
            player_display_height = 8

            self.player_x = max(PLAY_AREA_X, min(self.player_x, PLAY_AREA_X + PLAY_AREA_WIDTH - player_display_width))
            self.player_y = max(PLAY_AREA_Y, min(self.player_y, PLAY_AREA_Y + PLAY_AREA_HEIGHT - player_display_height))

            player_hitbox_width = 4
            player_hitbox_height = 4
            # Player hitbox offset returns to original calculation
            player_hitbox_offset_x = (player_display_width - player_hitbox_width) // 2
            player_hitbox_offset_y = (player_display_height - player_hitbox_height) // 2
            player_hitbox_x = self.player_x + player_hitbox_offset_x
            player_hitbox_y = self.player_y + player_hitbox_offset_y
            player_rect_for_collision = (player_hitbox_x, player_hitbox_y, player_hitbox_width, player_hitbox_height)


            if self.invincible_timer > 0:
                self.invincible_timer -= 1
                self.player_blink_timer += 1
                if self.player_blink_timer >= self.player_blink_interval * 2:
                    self.player_blink_timer = 0
            else:
                self.player_blink_timer = 0

            # --- Enemy Spawning (according to difficulty) ---
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.base_enemy_spawn_interval:
                spawn_types = []
                # Calculate in seconds * 30 frames for 30FPS
                if self.game_elapsed_frames < 30 * 30: # First 30 seconds
                    spawn_types = ["normal"]
                elif self.game_elapsed_frames < 60 * 30: # 30 seconds to 60 seconds (up to 1 minute total)
                    spawn_types = ["normal", "shot"]
                elif self.game_elapsed_frames < 90 * 30: # 60 seconds to 90 seconds (up to 1 minute 30 seconds total) - Delay Shield Ghost appearance by 30 seconds
                    spawn_types = ["normal", "shot", "shield"]
                else: # After 90 seconds
                    spawn_types = ["normal", "shot", "shield"]


                # Increase enemy spawn amount (after 60 seconds, every minute)
                if self.game_elapsed_frames >= self.next_difficulty_increase_time_for_spawn_amount and self.game_elapsed_frames >= 60 * 30:
                    self.enemies_per_spawn *= 1.5 # Enemy spawn increase rate from 2x to 1.5x
                    self.next_difficulty_increase_time_for_spawn_amount += 60 * 30 # Every minute (30FPS)

                for _ in range(int(self.enemies_per_spawn)): # Fix here
                    if spawn_types:
                        chosen_type = random.choice(spawn_types)
                        if chosen_type == "normal":
                            self.enemies.append(Enemy(self.player_x, self.player_y))
                        elif chosen_type == "shot":
                            self.shot_ghosts.append(ShotGhost(self.player_x, self.player_y))
                        elif chosen_type == "shield":
                            self.shield_ghosts.append(ShieldGhost(self.player_x, self.player_y))
                self.enemy_spawn_timer = 0

            # --- Enemy Update and Collision Detection ---
            self.enemies = [enemy for enemy in self.enemies if not enemy.is_outside_screen()]
            self.shot_ghosts = [ghost for ghost in self.shot_ghosts if not ghost.is_outside_screen()]
            self.shield_ghosts = [ghost for ghost in self.shield_ghosts if not ghost.is_outside_screen()]

            # Normal enemies
            for enemy in self.enemies:
                enemy.update(self.player_x, self.player_y)
                enemy_rect = (enemy.x, enemy.y, enemy.size, enemy.size)
                if self.check_collision_rect(player_rect_for_collision, enemy_rect):
                    if self.invincible_timer == 0:
                        self.hp -= 1
                        pyxel.play(0, 1)
                        self.invincible_timer = self.invincible_duration
                        if self.hp <= 0:
                            self.hp = 0
                            self.is_game_over = True
            
            # Shot Ghosts
            for ghost in self.shot_ghosts:
                ghost.update(self.player_x, self.player_y)
                # If in idle state and hasn't fired a bullet yet, spawn a bullet
                if ghost.state == "IDLE" and not ghost.bullet_fired:
                    # Shot Ghost's bullet targets the player
                    ghost_center_x = ghost.x + ghost.size // 2
                    ghost_center_y = ghost.y + 8 // 2 # Shot Ghost height is 8
                    self.enemy_bullets.append(Bullet(
                        ghost_center_x, ghost_center_y,
                        self.player_x + player_display_width // 2,
                        self.player_y + player_display_height // 2,
                        speed=0.5, # Slow down bullet flight speed (0.8 -> 0.5)
                        size=4, # 4x4 size
                        is_enemy_bullet=True # Mark as enemy bullet
                    ))
                    ghost.bullet_fired = True # Record that bullet was fired

                ghost_rect = (ghost.x, ghost.y, ghost.size, 8) # Shot Ghost height is 8
                if self.check_collision_rect(player_rect_for_collision, ghost_rect):
                    if self.invincible_timer == 0:
                        self.hp -= 1
                        pyxel.play(0, 1)
                        self.invincible_timer = self.invincible_duration
                        if self.hp <= 0:
                            self.hp = 0
                            self.is_game_over = True

            # Shield Ghosts
            for ghost in self.shield_ghosts:
                ghost.update(self.player_x, self.player_y)
                ghost_rect = (ghost.x, ghost.y, ghost.size, ghost.size)
                # Only deal damage if Shield Ghost is not invincible (blinking)
                if self.check_collision_rect(player_rect_for_collision, ghost_rect) and ghost.state != "DAMAGED_BLINK": # Fix here
                    if self.invincible_timer == 0:
                        self.hp -= 1
                        pyxel.play(0, 1)
                        self.invincible_timer = self.invincible_duration
                        if self.hp <= 0:
                            self.hp = 0
                            self.is_game_over = True


            self.attack_timer += 1
            if self.attack_timer >= self.attack_interval:
                for i in range(self.attacks_per_interval): # Effect of Multi-Sword Style
                    # Y-axis shift of attack (increases upwards)
                    attack_y_offset = -i * 2 # Shift up by 2px each time

                    # Slightly stagger timing of each attack
                    attack_delay = i * 2 # Delay each attack by 2 frames

                    # Reverse direction for odd-numbered attacks to attack behind self
                    current_facing_right = self.facing_right
                    if i % 2 != 0: # Odd-numbered (0-indexed, i.e., 2nd, 4th attack)
                        current_facing_right = not self.facing_right

                    # Pass initial offset and delay to Attack constructor
                    self.attacks.append(Attack(
                        self.player_x,
                        self.player_y,
                        0, # x_offset remains 0
                        attack_y_offset,
                        current_facing_right,
                        attack_delay # New initial_delay argument
                    ))
                self.attack_timer = 0

            for attack in self.attacks:
                # Pass player's current position so attack follows player
                attack.update(self.player_x, self.player_y)
            self.attacks = [attack for attack in self.attacks if attack.is_alive()]

            hit_enemies_this_frame = [] # To prevent hitting the same enemy multiple times in one frame
            # Attack detection for normal enemies
            for attack in self.attacks:
                for enemy in self.enemies:
                    if enemy not in hit_enemies_this_frame:
                        if attack.check_collision(enemy):
                            is_dead = enemy.take_damage()
                            if is_dead:
                                hit_enemies_this_frame.append(enemy)
                                self.kill_count += self.player_attack_power # Increase kill count according to attack power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))

            # Attack detection for Shot Ghosts
            for attack in self.attacks:
                for ghost in self.shot_ghosts:
                    if ghost not in hit_enemies_this_frame:
                        # Shot Ghost hitbox is 16x8
                        ghost_rect = (ghost.x, ghost.y, ghost.size, 8) 
                        if attack.check_collision(type("obj", (object,), {"x": ghost.x, "y": ghost.y, "size": ghost.size})()): # Collision detection with pseudo Enemy object
                            is_dead = ghost.take_damage()
                            if is_dead:
                                hit_enemies_this_frame.append(ghost)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + 8 // 2))

            # Attack detection for Shield Ghosts
            for attack in self.attacks:
                for ghost in self.shield_ghosts:
                    if ghost not in hit_enemies_this_frame:
                        ghost_rect = (ghost.x, ghost.y, ghost.size, ghost.size)
                        # Collision detection with pseudo Enemy object
                        if attack.check_collision(type("obj", (object,), {"x": ghost.x, "y": ghost.y, "size": ghost.size})()): 
                            is_dead = ghost.take_damage()
                            if is_dead: # When shield breaks or defeated
                                hit_enemies_this_frame.append(ghost) # Temporarily add to remove from list
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + ghost.size // 2))

            self.enemies = [enemy for enemy in self.enemies if enemy not in hit_enemies_this_frame]
            self.shot_ghosts = [ghost for ghost in self.shot_ghosts if ghost not in hit_enemies_this_frame]
            self.shield_ghosts = [ghost for ghost in self.shield_ghosts if ghost not in hit_enemies_this_frame]


            # --- Experience Orb Processing ---
            collected_orbs = []
            for orb in self.experience_orbs:
                # Pass player's attraction range to experience orb's update
                orb.update(self.player_x, self.player_y, self.exp_attraction_range) 
                orb_rect = orb.get_rect() # Get orb's collision rectangle
                if self.check_collision_rect(player_rect_for_collision, orb_rect):
                    collected_orbs.append(orb)
                    self.exp += orb.value # Add experience
                    pyxel.play(0, 3) # Orb acquisition sound (sound 3 on sound channel 0)

            # Remove collected orbs from list
            self.experience_orbs = [orb for orb in self.experience_orbs if orb not in collected_orbs]

            # --- Player Bullet Skill Processing ---
            if self.can_spawn_bullet:
                self.bullet_spawn_timer += 1
                if self.bullet_spawn_timer >= self.bullet_spawn_interval:
                    all_enemies = self.enemies + self.shot_ghosts + self.shield_ghosts # Target all enemies
                    if all_enemies: # Only fire bullets if there are enemies
                        # Player's center coordinates
                        player_center_x = self.player_x + player_display_width // 2
                        player_center_y = self.player_y + player_display_height // 2

                        # Sort enemies by distance from player
                        sorted_enemies = sorted(all_enemies, key=lambda e: math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))

                        # Target closest enemies according to bullet count
                        for i in range(min(self.bullets_per_shot, len(sorted_enemies))):
                            target_enemy = sorted_enemies[i]
                            # Add a slight delay to each bullet
                            bullet_delay = i * 3 # e.g., delay by 3 frames each
                            self.bullets.append(Bullet(
                                player_center_x,
                                player_center_y,
                                target_enemy.x + target_enemy.size // 2, # Target enemy's center
                                target_enemy.y + target_enemy.size // 2,
                                initial_delay=bullet_delay # Pass delay
                            ))
                        pyxel.play(0, 0) # Placeholder sound
                    self.bullet_spawn_timer = 0

            # Player bullet update and collision detection
            bullets_to_remove = []
            enemies_to_remove_by_bullet = []
            for bullet in self.bullets:
                bullet.update()
                if not bullet.is_alive():
                    bullets_to_remove.append(bullet)
                    continue # No need for collision detection if bullet is gone

                # Collision detection for normal enemies
                for enemy in self.enemies:
                    if enemy not in enemies_to_remove_by_bullet:
                        bullet_rect = bullet.get_rect()
                        enemy_rect = (enemy.x, enemy.y, enemy.size, enemy.size)
                        if self.check_collision_rect(bullet_rect, enemy_rect):
                            is_dead = enemy.take_damage()
                            if is_dead:
                                bullets_to_remove.append(bullet)
                                enemies_to_remove_by_bullet.append(enemy)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))
                                break # This bullet already hit, move to next bullet

                # Collision detection for Shot Ghosts
                for ghost in self.shot_ghosts:
                    if ghost not in enemies_to_remove_by_bullet:
                        bullet_rect = bullet.get_rect()
                        ghost_rect = (ghost.x, ghost.y, ghost.size, 8) # 16x8
                        if self.check_collision_rect(bullet_rect, ghost_rect):
                            is_dead = ghost.take_damage()
                            if is_dead:
                                bullets_to_remove.append(bullet)
                                enemies_to_remove_by_bullet.append(ghost)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + 8 // 2))
                                break

                # Collision detection for Shield Ghosts
                for ghost in self.shield_ghosts:
                    if ghost not in enemies_to_remove_by_bullet:
                        bullet_rect = bullet.get_rect()
                        ghost_rect = (ghost.x, ghost.y, ghost.size, ghost.size) # 8x8
                        if self.check_collision_rect(bullet_rect, ghost_rect):
                            is_dead = ghost.take_damage()
                            if is_dead:
                                bullets_to_remove.append(bullet)
                                enemies_to_remove_by_bullet.append(ghost)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + ghost.size // 2))
                            break

            self.bullets = [b for b in self.bullets if b not in bullets_to_remove]
            # Reapply bullets_to_remove here to remove player bullets that disappeared due to collision with enemy bullets
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove_by_bullet]
            self.shot_ghosts = [g for g in self.shot_ghosts if g not in enemies_to_remove_by_bullet]
            self.shield_ghosts = [g for g in self.shield_ghosts if g not in enemies_to_remove_by_bullet]


            # --- Enemy Bullet Update and Collision Detection with Player ---
            enemy_bullets_to_remove = []
            for e_bullet in self.enemy_bullets:
                e_bullet.update()
                if not e_bullet.is_alive():
                    enemy_bullets_to_remove.append(e_bullet)
                    continue
                
                e_bullet_rect = e_bullet.get_rect()
                # If hits player
                if self.invincible_timer == 0 and self.check_collision_rect(player_rect_for_collision, e_bullet_rect):
                    self.hp -= 1 # Change enemy bullet damage to 1
                    pyxel.play(0, 1)
                    self.invincible_timer = self.invincible_duration
                    if self.hp <= 0:
                        self.hp = 0
                        self.is_game_over = True
                    enemy_bullets_to_remove.append(e_bullet)
                    continue # No need for collision detection with other attacks if hit player

                # If hit by player's attack (sword attack)
                hit_by_player_attack = False
                for attack in self.attacks:
                    if attack.check_collision(type("obj", (object,), {"x": e_bullet_rect[0], "y": e_bullet_rect[1], "size": e_bullet_rect[2]})()):
                        enemy_bullets_to_remove.append(e_bullet)
                        pyxel.play(0, 2) # Disappearance sound
                        self.experience_orbs.append(ExperienceOrb(e_bullet_rect[0] + e_bullet_rect[2]//2, e_bullet_rect[1] + e_bullet_rect[3]//2)) # Experience orb
                        hit_by_player_attack = True
                        break # One bullet only hits one attack
                if hit_by_player_attack:
                    continue # Already gone, no need for collision detection with other attacks

                # Collision between player bullet and enemy bullet
                hit_by_player_bullet = False
                for p_bullet in self.bullets:
                     p_bullet_rect = p_bullet.get_rect()
                     if self.check_collision_rect(e_bullet_rect, p_bullet_rect):
                         enemy_bullets_to_remove.append(e_bullet)
                         bullets_to_remove.append(p_bullet) # Player bullet also disappears
                         pyxel.play(0, 2) # Disappearance sound
                         self.experience_orbs.append(ExperienceOrb(e_bullet_rect[0] + e_bullet_rect[2]//2, e_bullet_rect[1] + e_bullet_rect[3]//2)) # Experience orb
                         hit_by_player_bullet = True
                         break
                if hit_by_player_bullet:
                    continue # Already gone, no need for collision detection with other attacks

                # Collision with satellite
                hit_by_satellite = False
                for satellite in self.satellites:
                    sat_rect = satellite.get_rect()
                    if self.check_collision_rect(sat_rect, e_bullet_rect):
                        enemy_bullets_to_remove.append(e_bullet)
                        pyxel.play(0, 2) # Disappearance sound
                        self.experience_orbs.append(ExperienceOrb(e_bullet_rect[0] + e_bullet_rect[2]//2, e_bullet_rect[1] + e_bullet_rect[3]//2))
                        hit_by_satellite = True
                        break
                if hit_by_satellite:
                    continue # Already gone, no need for collision detection with other attacks

                # Collision with meteor
                hit_by_meteor = False
                for meteor in self.meteors:
                    if meteor.state == "EXPLODING":
                        explosion_rect = meteor.get_explosion_rect()
                        if explosion_rect and self.check_collision_rect(explosion_rect, e_bullet_rect):
                            enemy_bullets_to_remove.append(e_bullet)
                            pyxel.play(0, 2) # Disappearance sound
                            self.experience_orbs.append(ExperienceOrb(e_bullet_rect[0] + e_bullet_rect[2]//2, e_bullet_rect[1] + e_bullet_rect[3]//2))
                            hit_by_meteor = True
                            # Meteor can destroy multiple bullets, so don't break
                if hit_by_meteor:
                    continue # Already gone, no need for collision detection with other attacks


            self.enemy_bullets = [b for b in self.enemy_bullets if b not in enemy_bullets_to_remove]
            # Here, reapply bullets_to_remove to remove player bullets that disappeared due to collision with enemy bullets
            self.bullets = [b for b in self.bullets if b not in bullets_to_remove]


            # --- Satellite Skill Processing ---
            satellites_to_remove_enemies = [] # Record enemies defeated by satellites
            for satellite in self.satellites:
                satellite.update(self.player_x, self.player_y)
                sat_rect = satellite.get_rect()

                # Normal enemies
                for enemy in self.enemies:
                    if enemy not in satellites_to_remove_enemies:
                        enemy_rect = (enemy.x, enemy.y, enemy.size, enemy.size)
                        if self.check_collision_rect(sat_rect, enemy_rect):
                            is_dead = enemy.take_damage()
                            if is_dead:
                                satellites_to_remove_enemies.append(enemy)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))

                # Shot Ghosts
                for ghost in self.shot_ghosts:
                    if ghost not in satellites_to_remove_enemies:
                        ghost_rect = (ghost.x, ghost.y, ghost.size, 8)
                        if self.check_collision_rect(sat_rect, ghost_rect):
                            is_dead = ghost.take_damage()
                            if is_dead:
                                satellites_to_remove_enemies.append(ghost)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + 8 // 2))

                # Shield Ghosts
                for ghost in self.shield_ghosts:
                    if ghost not in satellites_to_remove_enemies:
                        ghost_rect = (ghost.x, ghost.y, ghost.size, ghost.size)
                        if self.check_collision_rect(sat_rect, ghost_rect):
                            is_dead = ghost.take_damage()
                            if is_dead:
                                satellites_to_remove_enemies.append(ghost)
                                self.kill_count += self.player_attack_power
                                pyxel.play(0, 2)
                                self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + ghost.size // 2))
            
            self.enemies = [e for e in self.enemies if e not in satellites_to_remove_enemies]
            self.shot_ghosts = [g for g in self.shot_ghosts if g not in satellites_to_remove_enemies]
            self.shield_ghosts = [g for g in self.shield_ghosts if g not in satellites_to_remove_enemies]


            # --- Meteor Skill Processing ---
            if self.can_spawn_meteor:
                self.meteor_spawn_timer += 1
                if self.meteor_spawn_timer >= self.meteor_spawn_interval:
                    for i in range(self.meteors_per_strike): # Fall multiple times
                        # Random point from top-right of screen
                        start_x = random.uniform(SCREEN_WIDTH, SCREEN_WIDTH + 30)
                        start_y = random.uniform(-30, 0)
                        # Random point within play area
                        target_x = random.uniform(PLAY_AREA_X, PLAY_AREA_X + PLAY_AREA_WIDTH - 16) # Consider meteor image width
                        target_y = random.uniform(PLAY_AREA_Y, PLAY_AREA_Y + PLAY_AREA_HEIGHT - 16) # Consider meteor image height

                        # Stagger arrival timing of each meteor
                        meteor_delay = i * 10 # Delay by 10 frames each

                        self.meteors.append(Meteor(
                            start_x, start_y,
                            target_x, target_y,
                            fly_duration=60, # 1 second flight (60 frames)
                            explode_duration=120, # 2 second explosion (120 frames)
                            initial_delay=meteor_delay # Pass delay
                        ))
                    self.meteor_spawn_timer = 0
            
            # Meteor update and collision detection
            meteors_to_remove = []
            enemies_to_remove_by_meteor = []
            for meteor in self.meteors:
                meteor.update()
                if not meteor.is_alive():
                    meteors_to_remove.append(meteor)
                    continue # No need to process if meteor is gone

                if meteor.state == "EXPLODING":
                    explosion_rect = meteor.get_explosion_rect()
                    if explosion_rect:
                        # Normal enemies
                        for enemy in self.enemies:
                            if enemy not in enemies_to_remove_by_meteor:
                                enemy_rect = (enemy.x, enemy.y, enemy.size, enemy.size)
                                if self.check_collision_rect(explosion_rect, enemy_rect):
                                    is_dead = enemy.take_damage()
                                    if is_dead:
                                        enemies_to_remove_by_meteor.append(enemy)
                                        self.kill_count += self.player_attack_power
                                        self.experience_orbs.append(ExperienceOrb(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))

                        # Shot Ghosts
                        for ghost in self.shot_ghosts:
                            if ghost not in enemies_to_remove_by_meteor:
                                ghost_rect = (ghost.x, ghost.y, ghost.size, 8)
                                if self.check_collision_rect(explosion_rect, ghost_rect):
                                    is_dead = ghost.take_damage()
                                    if is_dead:
                                        enemies_to_remove_by_meteor.append(ghost)
                                        self.kill_count += self.player_attack_power
                                        self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + 8 // 2))

                        # Shield Ghosts
                        for ghost in self.shield_ghosts:
                            if ghost not in enemies_to_remove_by_meteor:
                                ghost_rect = (ghost.x, ghost.y, ghost.size, ghost.size)
                                if self.check_collision_rect(explosion_rect, ghost_rect):
                                    is_dead = ghost.take_damage()
                                    if is_dead:
                                        enemies_to_remove_by_meteor.append(ghost)
                                        self.kill_count += self.player_attack_power
                                        self.experience_orbs.append(ExperienceOrb(ghost.x + ghost.size // 2, ghost.y + ghost.size // 2))


            self.meteors = [m for m in self.meteors if m not in meteors_to_remove]
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove_by_meteor]
            self.shot_ghosts = [g for g in self.shot_ghosts if g not in enemies_to_remove_by_meteor]
            self.shield_ghosts = [g for g in self.shield_ghosts if g not in enemies_to_remove_by_meteor]


            # --- Level Up Processing ---
            if self.exp >= self.exp_to_next_level:
                self.current_level += 1
                self.exp = 0 # Reset experience to 0
                # Set experience needed for next level up (e.g., increases by 1 each time)
                self.exp_to_next_level = self.current_level * 3 # Experience needed for level up transitions to 3, 6, 9...
                # Select 3 random skill options
                self.current_skill_options = random.sample(self.all_skill_options, 3)
                self.selected_skill_index = 0 # Reset selection index
                self.game_state = "LEVEL_UP_MENU" # Transition to level up menu

        elif self.game_state == "LEVEL_UP_MENU":
            # Skill selection menu operations
            # Use keyboard UP/DOWN for selection, Z/SPACE for confirmation (mapped to virtual gamepad D-Pad and A button)
            if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                self.selected_skill_index = (self.selected_skill_index - 1) % len(self.current_skill_options)
            elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                self.selected_skill_index = (self.selected_skill_index + 1) % len(self.current_skill_options)
            elif pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B): # Select with Z or Space key
                # Apply selected skill
                selected_skill = self.current_skill_options[self.selected_skill_index]

                if selected_skill == "Dash":
                    self.player_speed *= 1.4 # Movement speed increases by 1.4x
                elif selected_skill == "Rapid Attack":
                    # Shorten attack interval (smaller value means faster)
                    self.attack_interval = max(5, self.attack_interval / 1.3) 
                    # Shorten bullet firing interval
                    self.bullet_spawn_interval = max(30, self.bullet_spawn_interval / 1.2) # Minimum 30 frames
                elif selected_skill == "Magnet":
                    self.exp_attraction_range *= 2.0 # Experience absorption range increases by 2x
                elif selected_skill == "Heal":
                    self.hp += 5 # Recover +5 HP (can exceed max HP)
                elif selected_skill == "Multi-Sword": # New skill effect
                    self.attacks_per_interval += 1
                elif selected_skill == "Bullet": # New skill effect
                    self.can_spawn_bullet = True
                    self.bullets_per_shot += 1 # Increase bullet count
                elif selected_skill == "Satellite": # New skill effect
                    # Increase number of satellites
                    # Change Satellite constructor argument from color to rotation_speed
                    self.satellites.append(Satellite(
                        self.player_x, self.player_y,
                        self.satellite_base_radius,
                        random.uniform(3, 7) # New satellites generated with random speed
                    ))
                    # Update rotation speed of all existing satellites randomly
                    for sat in self.satellites:
                        sat.rotation_speed = random.uniform(3, 7)
                elif selected_skill == "Meteor": # New skill effect
                    self.can_spawn_meteor = True
                    self.meteors_per_strike += 1 # Increase number of meteor strikes
                self.game_state = "PLAYING" # Resume game


    def check_collision_rect(self, rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return (x1 < x2 + w2 and
                x1 + w1 > x2 and
                y1 < y2 + h2 and
                y1 + h1 > y2)

    def draw_text(self, x, y, text, color, size=8):
        # Using pyxel.text directly as PyxelUniversalFont is not used
        pyxel.text(x, y, text, color)


    def draw(self):
        pyxel.cls(4)
        pyxel.bltm(32, 0, 0, 0, 0, 64, 64)
        pyxel.bltm(0, 0, 0, 64, 0, 32, 64)
        pyxel.bltm(32+64, 0, 0, 64+32, 0, 32, 64)

        # Draw experience orbs (draw before player and enemies)
        for orb in self.experience_orbs:
            orb.draw()

        if not self.is_game_over and not self.is_game_clear and not (self.invincible_timer > 0 and self.player_blink_timer % (self.player_blink_interval * 2) < self.player_blink_interval):
            if self.facing_right:
                pyxel.blt(int(self.player_x), int(self.player_y), 0, 16, 0, 8, 8, 0)
            else:
                pyxel.blt(int(self.player_x), int(self.player_y), 0, 16, 0, -8, 8, 0)

        for enemy in self.enemies:
            enemy.draw()
        for ghost in self.shot_ghosts:
            ghost.draw()
        for ghost in self.shield_ghosts:
            ghost.draw()

        for attack in self.attacks:
            attack.draw()

        # Draw player bullets
        for bullet in self.bullets:
            bullet.draw()
        # Draw enemy bullets
        for e_bullet in self.enemy_bullets:
            e_bullet.draw()


        # Draw satellites
        for satellite in self.satellites:
            satellite.draw()

        # Draw meteors
        for meteor in self.meteors:
            meteor.draw()

        # Draw UI text on top
        self.draw_text(5 - 2, 5, f"HP:{self.hp}", pyxel.COLOR_GREEN, size=8)
        self.draw_text(5 - 2, 15, f"Kills:{self.kill_count}", pyxel.COLOR_RED, size=8)
        self.draw_text(5 - 2, 25, f"EXP:{self.exp}/{self.exp_to_next_level}", pyxel.COLOR_BLACK, size=8)
        self.draw_text(5 - 2, 35, f"LV:{self.current_level}", pyxel.COLOR_LIME, size=8)

        # Display remaining time
        remaining_frames = max(0, self.game_duration_frames - self.game_elapsed_frames)
        minutes = remaining_frames // (30 * 60) # Frames per minute at 30FPS
        seconds = (remaining_frames // 30) % 60 # Frames per second at 30FPS
        time_text = f"{minutes:02}:{seconds:02}"
        time_text_x = SCREEN_WIDTH - 5 - (len(time_text) * 4) # Calculate based on 4px per character (pyxel.text default size)
        time_text_y = SCREEN_HEIGHT - 10
        self.draw_text(time_text_x, time_text_y, time_text, pyxel.COLOR_BLACK, size=8) # Remaining time timer in black


        if self.is_game_over:
            game_over_text = "GAME OVER!"
            restart_text = "Press 'KEY-R' or 'X/Y' to Reset!" # Updated instruction
            font_size_game_over = 8
            font_size_restart = 8
            # Center text using pyxel.text's default character width of 4px
            game_over_text_width = len(game_over_text) * 4
            game_over_x = (SCREEN_WIDTH - game_over_text_width) // 2
            game_over_y = SCREEN_HEIGHT // 2 - 10
            self.draw_text(game_over_x, game_over_y, game_over_text, pyxel.COLOR_RED, size=font_size_game_over)

            restart_text_width = len(restart_text) * 4
            restart_x = (SCREEN_WIDTH - restart_text_width) // 2
            restart_y = SCREEN_HEIGHT // 2 + 5
            self.draw_text(restart_x+1, restart_y, restart_text, pyxel.COLOR_RED, size=font_size_restart)
        
        # Game Clear display
        if self.is_game_clear:
            clear_text = "GAME CLEAR!"
            restart_text = "Press 'R' or 'X' (Y-button) to Reset!" # Updated instruction
            
            # Center text using pyxel.text's default character width of 4px
            clear_text_width = len(clear_text) * 4
            clear_x = (SCREEN_WIDTH - clear_text_width) // 2
            clear_y = SCREEN_HEIGHT // 2 - 10
            
            # Apply rainbow colors
            rainbow_color_index = (pyxel.frame_count // 5) % len(self.rainbow_colors) # Change color every 5 frames
            rainbow_color = self.rainbow_colors[rainbow_color_index]

            self.draw_text(clear_x, clear_y, clear_text, rainbow_color, size=8)

            restart_text_width = len(restart_text) * 4
            restart_x = (SCREEN_WIDTH - restart_text_width) // 2
            restart_y = SCREEN_HEIGHT // 2 + 5
            self.draw_text(restart_x, restart_y, restart_text, pyxel.COLOR_WHITE, size=8)

        # Draw level up menu
        if self.game_state == "LEVEL_UP_MENU":
            # Semi-transparent background
            pyxel.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, pyxel.COLOR_BLACK)
            pyxel.rectb(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, pyxel.COLOR_WHITE) # Border

            menu_x = SCREEN_WIDTH // 2 - 30
            menu_y = SCREEN_HEIGHT // 2 - 20
            self.draw_text(menu_x, menu_y - 10, "SELECT SKILL!", pyxel.COLOR_WHITE, size=8)

            for i, skill in enumerate(self.current_skill_options): # Display randomly selected skills
                color = pyxel.COLOR_WHITE
                if i == self.selected_skill_index:
                    color = pyxel.COLOR_YELLOW # Highlight selected skill
                self.draw_text(menu_x, menu_y + i * 10, skill, color, size=8)

            self.draw_text(menu_x-18, menu_y + len(self.current_skill_options) * 10 + 5, "Move, Z/Space (A/B-button)", pyxel.COLOR_LIGHT_BLUE, size=8) # Updated instruction

        # Draw announcement message
        if self.alert_message and self.alert_display_timer > 0:
            # Center text
            alert_text_width = len(self.alert_message) * 4 # pyxel.text default character width is 4px
            alert_x = (SCREEN_WIDTH - alert_text_width) // 2 - 3 # Move -3px on x-axis
            alert_y = SCREEN_HEIGHT // 2 - 4 # Slightly above screen center
            self.draw_text(alert_x, alert_y, self.alert_message, pyxel.COLOR_YELLOW, size=8)

            
App()
