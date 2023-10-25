import math
import pygame

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
        self.velocity *= AIR_DRAG
        print('Throw distance:', self.throw_distance)

mockingbird = Disc(0, 0, 0.12, (255, 0, 0), 7, 5, -2, 1)

background_colour = (255,255,255)
(width, height) = (1024, 768)
pygame.display.set_caption('Disc Golf Course Creator')
screen = pygame.display.set_mode((width, height))
view_port = ViewPort(800, 600, screen, 0, 0, .01)

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
                print('move left!', view_port.x)
                view_port.x -= 1
            elif event.key == pygame.K_RIGHT:
                view_port.x += 1
            elif event.key == pygame.K_UP:
                view_port.y -= 1
            elif event.key == pygame.K_DOWN:
                view_port.y += 1

    
    screen.fill(background_colour)
    mockingbird.update(ticks)
    mockingbird.display(view_port)
    pygame.display.flip()
