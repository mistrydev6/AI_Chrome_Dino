import pygame
import os
import sys
import random
import neat
import math


# Initialize pygame
pygame.init()

#Global Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUN = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
       pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]  

JUMP = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]

LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]


FONT = pygame.font.SysFont("comicsansms", 20)

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self, img=RUN[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.step_index = 0

    def update(self):
        if self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = JUMP
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 6                     
            self.jump_vel -= 0.80
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUN[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y)) 

class Obstable:
    def __init__(self, image, num_cactus):
        self.image = image
        self.type = num_cactus
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed

        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstable):
    def __init__(self, image, num_cactus):
        super().__init__(image, num_cactus)
        self.rect.y = 325

class LargeCactus(Obstable):
    def __init__(self, image, num_cactus):
        super().__init__(image, num_cactus)
        self.rect.y = 300

def remove(index):
    dinosaurs.pop(index)
    genom.pop(index)
    nets.pop(index)

def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx**2 + dy**2)

#Main Method
def eval_genomes(genomes, config):

    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, dinosaurs, genom, nets

    points = 0
    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 10

    obstacles = []
    dinosaurs = []
    genom = []
    nets = []

    clock = pygame.time.Clock()
    
    for genome_id, genome in genomes:
        dinosaurs.append(Dinosaur())
        genom.append(genome)

        #NEURAL NET
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0


    def Score():
        global points, game_speed

        points += 1

        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points: {str(points)}', True, (255, 255, 255))
        SCREEN.blit(text, (950, 50))

    def stats():
        global dinosaurs, game_speed, genom 
        t1 = FONT.render(f'Dinosuars Alive : {str(len(dinosaurs))}', True, (255, 255, 255))
        t2 = FONT.render(f'Population Generation: {pop.generation+1}', True, (255, 255, 255))
        t3 = FONT.render(f'Game Speed: {str(game_speed)}', True, (255, 255, 255))

        SCREEN.blit(t1, (50, 450))
        SCREEN.blit(t2, (50, 480))
        SCREEN.blit(t3, (50, 510))

    def background():
        global x_pos_bg, y_pos_bg

        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))

        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        SCREEN.fill((0, 0, 0))

        for x in dinosaurs:
            x.update()
            x.draw(SCREEN)

        if len(dinosaurs) == 0:
            break 

        #Randomly Generating Obstacles
        if len(obstacles) == 0:
            a = random.randint(0, 1)

            if a == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif a == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))


        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()

            for i, x in enumerate(dinosaurs):
                if obstacle.rect.colliderect(x.rect):
                    genom[i].fitness -= 1
                    remove(i)


#        user_input = pygame.key.get_pressed()

        for i, x in enumerate(dinosaurs):
            output = nets[i].activate(
                (
                    x.rect.y, 
                    distance(
                        (
                            x.rect.x,
                            x.rect.y
                        ),
                        obstacle.rect.midtop
                    )
                )
            )

            if output[0] > 0.5 and x.rect.y == x.Y_POS:
                x.dino_jump = True
                x.dino_run = False

#            if user_input[pygame.K_SPACE]:
#                x.dino_jump = True
#                x.dino_run = False

        Score()
        background()  
        stats()
        clock.tick(60)
        pygame.display.update()

#NEAT Algorithm setup
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)

#Run Method
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
