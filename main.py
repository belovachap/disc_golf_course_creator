from enum import Enum
import math
import pygame
import random


AIR_DRAG = 0.996


class ViewPort:
    def __init__(self, width, height, screen, x, y, zoom):
        self.width = width
        self.height = height
        self.screen = screen
        self.x = x
        self.y = y
        self.zoom = zoom


class Disc:
    def __init__(self, x, y, radius, color, speed, glide, turn, fade):
        self.velocity_angle = 0
        self.velocity = 0
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.glide = glide
        self.turn = turn
        self.fade = fade
        self.throw_distance = 0

    def display(self, view_port):
        view_x = (self.x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_y = -1 * ((self.y - view_port.y) / view_port.zoom) + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, self.color, (view_x, view_y), view_radius)

    def update(self, ticks):
        seconds = ticks / 1000

        self.y += math.sin(self.velocity_angle) * self.velocity * seconds        
        self.x += math.cos(self.velocity_angle) * self.velocity * seconds
        
        # Low velocity fade
        if self.velocity < 10 and self.velocity > 0.1:
            self.velocity_angle += (math.pi / 4) * .25 * ((self.fade + 1) / 6) * seconds

        # High velocity turn
        if self.velocity > 20:
            self.velocity_angle -= (math.pi / 4) * .25 * ((-1 * self.turn + 2) / 7) * seconds

        self.velocity *= AIR_DRAG

        # print('Throw distance:', self.throw_distance)


class ThrowStatus(Enum):
    PLANNING = 1
    FLYING = 2
    COMPLETE = 3


class Throw:
    def __init__(self, count, disc, facing_angle):
        self.count = count
        self.disc = disc
        self.status = ThrowStatus.PLANNING
        self.flight_path = []
        self.distance = 0
        self.facing_angle = facing_angle
        self.starting_x = disc.x
        self.starting_y = disc.y

    def update(self, ticks):
        if not self.status == ThrowStatus.FLYING:
            return

        seconds = ticks / 1000

        self.distance += self.disc.velocity * seconds

        if self.disc.velocity < 0.5:
            self.status = ThrowStatus.COMPLETE
            self.disc.velocity = 0

        if self.disc.velocity > 0:
            self.flight_path.append((self.disc.x, self.disc.y))
    
        self.disc.update(ticks)

    def display(self, view_port):
        for fp in self.flight_path:
            view_x = (fp[0] - view_port.x) / view_port.zoom + (view_port.width // 2)
            view_y = -1 * ((fp[1] - view_port.y) / view_port.zoom) + (view_port.height // 2)
            view_radius = self.disc.radius / view_port.zoom
            pygame.draw.circle(view_port.screen, (0, 0, 255), (view_x, view_y), view_radius)

        # Draw the "player"
        view_width = 1 / view_port.zoom
        view_height = 0.2 / view_port.zoom
        rect_surf = pygame.Surface((view_width, view_height), pygame.SRCALPHA)
        rect_surf.fill((128, 128, 128))
        rotated = pygame.transform.rotate(rect_surf, math.degrees(self.facing_angle - math.pi / 2))
        view_left = (self.starting_x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_top = -1 * ((self.starting_y - view_port.y) / view_port.zoom) + (view_port.height // 2)
        rotated_rect = rotated.get_rect()
        view_rect = pygame.Rect(view_left, view_top, view_width, view_height)
        view_port.screen.blit(rotated, view_rect)

        # Draw the disc
        self.disc.display(view_port) 


class Tree:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def display(self, view_port):
        view_x = (self.x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_y = -1 * ((self.y - view_port.y) / view_port.zoom) + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, (0, 255, 0), (view_x, view_y), view_radius)


class Basket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0.27051

    def display(self, view_port):
        view_x = (self.x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_y = -1 * ((self.y - view_port.y) / view_port.zoom) + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, (145, 145, 145), (view_x, view_y), view_radius)


class DirectionAngleHUD:
    def __init__(self):
        self.angle = 0

    def display(self, view_port):
        view_left = 10
        view_top = 650 
        view_width = 100
        view_height = 100
        view_rect = pygame.Rect(view_left, view_top, view_width, view_height)
        pygame.draw.rect(view_port.screen, (128, 128, 128), view_rect)

        pygame.draw.arc(view_port.screen, (0, 0, 0), view_rect, 0, -1 * math.pi, width=2)
        
        center = view_rect.center
        end_pos = (center[0] - math.sin(self.angle) * 50, center[1] - math.cos(self.angle) * 50) 

        pygame.draw.line(view_port.screen, (0, 0, 0), center, end_pos, width=2)


class PowerHUD:
    def __init__(self):
        self.power = 0
        self.space_bar_down = False

    def update(self):
        if not self.space_bar_down:
            return

        self.power += 1

        if self.power > 100:
            self.power = 0

    def display(self, view_port):
        view_left = 150
        view_top = 650 
        view_width = 600
        view_height = 100
        view_rect = pygame.Rect(view_left, view_top, view_width, view_height)
        pygame.draw.rect(view_port.screen, (128, 128, 128), view_rect)

        view_left = 150
        view_top = 650 
        view_width = 600 * (self.power / 100)
        view_height = 100
        view_rect = pygame.Rect(view_left, view_top, view_width, view_height)
        pygame.draw.rect(view_port.screen, (255, 0, 0), view_rect)
        

def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    distance = math.hypot(dx, dy)
    if distance < p1.radius + p2.radius:
        return True

    return False


basket = Basket(random.uniform(-50, 50), random.uniform(80, 110))

trees = []
for _ in range(0, random.randint(100, 1000)):
    x = random.uniform(-320 / 2, 320 / 2)
    y = random.uniform(-640 / 2, 640 / 2)
    radius = random.uniform(.25, 5)
    trees.append(Tree(x, y, radius))

throw_drive = Throw(1, Disc(0, 0, 0.12, (255, 0, 0), 7, 5, -2, 1), math.pi / 2)

direction_angle_hud = DirectionAngleHUD()
power_hud = PowerHUD()

background_colour = (255,255,255)
(width, height) = (1024, 768)
pygame.display.set_caption('Disc Golf Course Creator')
screen = pygame.display.set_mode((width, height))
view_port = ViewPort(width, height, screen, 0, 0, .1)

space_bar_down = False
view_port_follows_disc = False
recent_tree_hit = False
invincible_disc_time = 0
invincible_disc_time_limit = 0
running = True
clock = pygame.time.Clock()
while running:
    ticks = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            print('Mousewheel!', event)
            if event.y > 0:
                view_port.zoom *= 1.1
            else:
                view_port.zoom /= 1.1

            if view_port.zoom < .001:
                view_port.zoom = .001
            elif view_port.zoom > 1:
                view_port.zoom = 1

        elif event.type == pygame.MOUSEMOTION:
            if not event.buttons[0]:
                break 
            print('Mouse motion!', event)
            view_port_follows_disc = False
            view_port.x -= event.rel[0] * view_port.zoom
            view_port.y += event.rel[1] * view_port.zoom

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and throw_drive.status == ThrowStatus.PLANNING:
                print("throw the disc!")
                power_hud.space_bar_down = False
                throw_drive.status = ThrowStatus.FLYING
                view_port_follows_disc = True
                throw_drive.disc.velocity_angle = throw_drive.facing_angle + direction_angle_hud.angle
                throw_drive.disc.velocity = 27 * (power_hud.power / 100) # 27 meters / second is about 60 miles / hour 

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("reset!")
                view_port_follows_disc = False
                view_port.x = 0
                view_port.y = 0
                throw_drive = Throw(1, Disc(0, 0, 0.12, (255, 0, 0), 7, 5, -2, 1), math.pi / 2)

            if event.key == pygame.K_n:
                print("new map!")
                view_port_follows_disc = False
                view_port.x = 0
                view_port.y = 0
                throw_drive = Throw(1, Disc(0, 0, 0.12, (255, 0, 0), 7, 5, -2, 1), math.pi / 2)
                basket = Basket(random.uniform(-50, 50), random.uniform(-110, -80))
                trees = []
                for _ in range(0, random.randint(10, 100)):
                    x = random.uniform(-100, 100)
                    y = random.uniform(-200, 10)
                    radius = random.uniform(.25, 5)
                    trees.append(Tree(x, y, radius))

            elif event.key == pygame.K_SPACE:
                power_hud.space_bar_down = True

            elif event.key == pygame.K_LEFT:
                direction_angle_hud.angle += math.pi / 64
                if direction_angle_hud.angle > (math.pi / 2):
                    direction_angle_hud.angle = math.pi / 2

            elif event.key == pygame.K_RIGHT:
                direction_angle_hud.angle -= math.pi / 64
                if direction_angle_hud.angle < (-1 * math.pi / 2):
                    direction_angle_hud.angle = -1 * math.pi / 2
 
    if throw_drive.status == ThrowStatus.COMPLETE:
        view_port_follows_disc = False
        power_hud.power = 0
        direction_angle_hud.angle = 0
        facing_angle = math.atan2((basket.y - throw_drive.disc.y), (basket.x - throw_drive.disc.x))
        throw_drive = Throw(throw_drive.count + 1, throw_drive.disc, facing_angle)

    if view_port_follows_disc:
        view_port.x = throw_drive.disc.x
        view_port.y = throw_drive.disc.y
    
    screen.fill(background_colour)

    basket.display(view_port)
    if collide(throw_drive.disc, basket):
        print('You hit the basket!!')

    for tree in trees:
        tree.display(view_port)
        if not recent_tree_hit and collide(throw_drive.disc, tree):
            print('You hit a tree!')
            recent_tree_hit = True
            invincible_disc_time_limit = random.uniform(.1, 1)
            throw_drive.disc.velocity_angle += random.uniform(0, 2 * math.pi)
            throw_drive.disc.velocity *= random.uniform(0, 0.9)

    if recent_tree_hit:
        if invincible_disc_time < invincible_disc_time_limit:
            invincible_disc_time += ticks / 1000
        else:
            invincible_disc_time = 0
            recent_tree_hit = False

    throw_drive.update(ticks)
    throw_drive.display(view_port)

    direction_angle_hud.display(view_port)

    power_hud.update()
    power_hud.display(view_port)

    pygame.display.flip()
