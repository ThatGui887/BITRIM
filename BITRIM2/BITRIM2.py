import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)


pygame.init()


clock = pygame.time.Clock()

class Bullet:
    """Class to create bullets shot by the player."""
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 5, 5)  
        self.color = (255, 0, 0)  
        self.speed = 10 if direction == 'right' else -10  

    def update(self):
        self.rect.x += self.speed  
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Gun:
    """Class to create the player's gun."""
    def __init__(self, player):
        self.player = player
        self.color = BLACK  
        self.visible = False  

    def update_position(self):
        
        if self.player.last_direction: 
            self.visible = True

    def draw(self, screen):
        if self.visible:  
            gun_length = 20
            gun_width = 5
            gun_y = self.player.rect.centery

            if self.player.last_direction == 'right': 
                gun_x = self.player.rect.right
                
                pygame.draw.line(screen, self.color, (gun_x, gun_y), (gun_x + gun_length, gun_y), gun_width)
            else:  
                gun_x = self.player.rect.left
                
                pygame.draw.line(screen, self.color, (gun_x, gun_y), (gun_x - gun_length, gun_y), gun_width)

class Sword:
    """Class to create the player's sword."""
    def __init__(self, player):
        self.player = player
        self.color = BLACK 
        self.visible = False  
        self.sword_timer = 0  

    def update_position(self):
        
        if self.player.last_direction: 
            self.visible = True

    def draw(self, screen):
        if self.visible:  
            sword_length = 60  
            sword_width = 10  
            sword_y = self.player.rect.centery

            if self.player.last_direction == 'right': 
                sword_x = self.player.rect.right
                
                pygame.draw.line(screen, self.color, (sword_x, sword_y), (sword_x + sword_length, sword_y), sword_width)
            else:  
                sword_x = self.player.rect.left
                
                pygame.draw.line(screen, self.color, (sword_x, sword_y), (sword_x - sword_length, sword_y), sword_width)

    def update(self):
        if self.visible:
            self.sword_timer += clock.get_time() / 1000  
            if self.sword_timer > 0.1:  
                self.visible = False
                self.sword_timer = 0  

class Player:
    """Class to create the playable sprite."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.x_velocity = 0
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -13  
        self.on_ground = False
        self.health = 100  
        self.ammo = 10  
        self.bullets = []  
        self.shoot_cooldown = False  
        self.gun = Gun(self)  
        self.sword = Sword(self)  
        self.last_direction = None  

    def move(self, keys):
        
        self.x_velocity = 0
        if keys[pygame.K_LEFT]:
            self.x_velocity = -5
            self.last_direction = 'left'  
        elif keys[pygame.K_RIGHT]:
            self.x_velocity = 5
            self.last_direction = 'right'  

        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.y_velocity = self.jump_strength
            self.on_ground = False

    def shoot(self):
        if self.ammo > 0 and not self.shoot_cooldown:  
            direction = self.last_direction if self.last_direction else 'right'  
            gun_x = self.rect.x + (self.rect.width if direction == 'right' else 0)  
            gun_y = self.rect.centery  
            bullet = Bullet(gun_x, gun_y, direction)  
            self.bullets.append(bullet)  
            self.ammo -= 1  
            self.shoot_cooldown = True  

            
            self.gun.visible = True

    def release_shoot(self):
        self.shoot_cooldown = False  

    def use_sword(self):
        self.sword.visible = True
        self.sword.sword_timer = 0  

    def release_sword(self):
        self.sword.visible = False  

    def update(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity
        self.apply_gravity()

       
        self.gun.update_position()
        self.sword.update()

    def apply_gravity(self):
        self.y_velocity += self.gravity 
        if self.rect.y >= 650:  
            self.rect.y = 650
            self.on_ground = True

    def check_collision(self, platforms):
        self.on_ground = False

        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                
                if self.y_velocity > 0 and self.rect.bottom <= platform.rect.top + self.y_velocity:
                    self.rect.bottom = platform.rect.top
                    self.y_velocity = 0
                    self.on_ground = True

      
        if self.on_ground:
            self.y_velocity = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        
        health_bar_width = 40
        health_bar_height = 5
        health_bar = pygame.Rect(self.rect.x + (self.rect.width - health_bar_width) // 2,
                                  self.rect.y - health_bar_height - 5,
                                  health_bar_width, health_bar_height)
        pygame.draw.rect(screen, BLACK, health_bar) 
        health_fill = health_bar_width * (self.health / 100)
        pygame.draw.rect(screen, (255, 0, 0), health_bar.inflate(-2, -2))  

        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f'Ammo: {self.ammo}', True, BLACK)
        screen.blit(text_surface, (10, 10)) 

      
        self.gun.draw(screen)
        self.sword.draw(screen)
        
class Enemy:
    """Class to create an enemy sprite."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 0, 0)  # Red color for the enemy
        self.x_velocity = 2  # Move right initially
        self.y_velocity = 0
        self.gravity = 0.5
        self.on_ground = False

    def move(self):
        """Move the enemy left and right."""
        self.rect.x += self.x_velocity

        # Reverse direction if the enemy hits the screen boundaries
        if self.rect.right >= 1280 or self.rect.left <= 0:
            self.x_velocity *= -1

    def apply_gravity(self):
        """Apply gravity to the enemy."""
        if not self.on_ground:
            self.y_velocity += self.gravity
        self.rect.y += self.y_velocity

    def check_collision(self, platforms):
        """Check for collision with platforms."""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # If the enemy is falling and lands on top of the platform
                if self.y_velocity > 0 and self.rect.bottom <= platform.rect.top + self.y_velocity:
                    self.rect.bottom = platform.rect.top
                    self.y_velocity = 0
                    self.on_ground = True

    def update(self, platforms):
        """Update the enemy position and handle collisions."""
        self.move()
        self.apply_gravity()
        self.check_collision(platforms)

    def draw(self, screen):
        """Draw the enemy sprite on the screen."""
        pygame.draw.rect(screen, self.color, self.rect)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(100, 400, 50, 100)
        self.platforms = [
            Platform(0, 650, 1280, 50),  # Ground platform
            Platform(400, 500, 200, 20),  # Mid-level platform
            Platform(800, 400, 200, 20)   # Upper-level platform
        ]
        self.enemy = Enemy(500, 300, 50, 50)  # Add an enemy sprite

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.player.shoot()
                    if event.key == pygame.K_w:
                        self.player.use_sword()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        self.player.release_shoot()
                    if event.key == pygame.K_w:
                        self.player.release_sword()

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.update()

            # Update enemy and check for collisions
            self.enemy.update(self.platforms)

            # Player collision with platforms
            self.player.check_collision(self.platforms)

            # Screen drawing
            self.screen.fill(LIGHT_BLUE)
            for platform in self.platforms:
                platform.draw(self.screen)
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)  # Draw the enemy

            for bullet in self.player.bullets:
                bullet.update()
                bullet.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


class Platform:
    """Class to create a static platform."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BROWN

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(100, 400, 50, 100)
        self.platforms = [
            Platform(0, 650, 1280, 50),  
            Platform(400, 500, 200, 20),  
            Platform(800, 400, 200, 20)   
        ]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.player.shoot()  
                    if event.key == pygame.K_w:
                        self.player.use_sword()  
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        self.player.release_shoot()  
                    if event.key == pygame.K_w:
                        self.player.release_sword()  

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.update()

           
            self.player.check_collision(self.platforms)

           
            self.screen.fill(LIGHT_BLUE)
            for platform in self.platforms:
                platform.draw(self.screen)
            self.player.draw(self.screen)

            
            for bullet in self.player.bullets:
                bullet.update() 
                bullet.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((1280, 720))
    game = Game(screen)
    game.run()