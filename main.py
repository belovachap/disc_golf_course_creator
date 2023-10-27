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
        view_y = (self.y - view_port.y) / view_port.zoom + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, self.color, (view_x, view_y), view_radius)

    def update(self, ticks):
        seconds = ticks / 1000
        self.throw_distance += self.velocity * seconds
        
        self.x += math.sin(self.velocity_angle) * self.velocity * seconds
        self.y -= math.cos(self.velocity_angle) * self.velocity * seconds
        
        # Low velocity fade
        if self.velocity < 10 and self.velocity > 0.1:
            self.velocity_angle -= (math.pi / 4) * .25 * ((self.fade + 1) / 6) * seconds

        # High velocity turn
        if self.velocity > 20:
            self.velocity_angle += (math.pi / 4) * .25 * ((-1 * self.turn + 2) / 7) * seconds

        self.velocity *= AIR_DRAG

        # print('Throw distance:', self.throw_distance)


class HorizontalGridLine:
    def __init__(self, y):
        self.y = y

    def display(self, view_port):
        view_left = (-50 - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_top = (self.y - view_port.y) / view_port.zoom + (view_port.height // 2)    
        view_width = 100 / view_port.zoom
        view_height = .1 / view_port.zoom
        view_rect = pygame.Rect(view_left, view_top, view_width, view_height)
        pygame.draw.rect(view_port.screen, (0, 0, 255), view_rect)


class Tree:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def display(self, view_port):
        view_x = (self.x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_y = (self.y - view_port.y) / view_port.zoom + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, (0, 255, 0), (view_x, view_y), view_radius)


class Basket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0.27051

    def display(self, view_port):
        view_x = (self.x - view_port.x) / view_port.zoom + (view_port.width // 2)
        view_y = (self.y - view_port.y) / view_port.zoom + (view_port.height // 2)
        view_radius = self.radius / view_port.zoom
        pygame.draw.circle(view_port.screen, (145, 145, 145), (view_x, view_y), view_radius)


basket = Basket(random.uniform(-50, 50), random.uniform(-110, -80))

horizontal_grid = []
for y in range(-200, 0):
    horizontal_grid.append(HorizontalGridLine(y))

trees = []
for _ in range(0, random.randint(10, 100)):
    x = random.uniform(-100, 100)
    y = random.uniform(-200, 10)
    radius = random.uniform(.25, 5)
    trees.append(Tree(x, y, radius))

mockingbird = Disc(0, 0, 0.12, (255, 0, 0), 7, 5, -2, 1)

background_colour = (255,255,255)
(width, height) = (1024, 768)
pygame.display.set_caption('Disc Golf Course Creator')
screen = pygame.display.set_mode((width, height))
view_port = ViewPort(width, height, screen, 0, 0, .01)

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
            elif view_port.zoom > .1:
                view_port.zoom = .1

        elif event.type == pygame.MOUSEMOTION:
            if not event.buttons[0]:
                break 
            print('Mouse motion!', event)
            view_port.x -= event.rel[0] * view_port.zoom
            view_port.y -= event.rel[1] * view_port.zoom

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("throw the disc!")
                mockingbird.velocity = 27 # 27 meters / second is about 60 miles / hour 
            elif event.key == pygame.K_LEFT:
                mockingbird.velocity_angle -= math.pi / 32
                print(math.pi / 32)
                if mockingbird.velocity_angle < (-1 * math.pi / 4):
                    mockingbird.velocity_angle = -1 * math.pi / 4

                print('mockingbird.velocity_angle:', mockingbird.velocity_angle)

            elif event.key == pygame.K_RIGHT:
                mockingbird.velocity_angle += math.pi / 32
                if mockingbird.velocity_angle > (math.pi / 4):
                    mockingbird.velocity_angle = math.pi / 4

                print('mockingbird.velocity_angle:', mockingbird.velocity_angle)
 
    
    screen.fill(background_colour)

    for line in horizontal_grid:
        line.display(view_port)

    basket.display(view_port)

    for tree in trees:
        tree.display(view_port)

    mockingbird.update(ticks)
    mockingbird.display(view_port)
    pygame.display.flip()
