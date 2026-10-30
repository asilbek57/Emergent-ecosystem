import random
import pygame
import sys

class Cell:
    def __init__(self, x, y, energy, age=0, is_alive = True):
        if not isinstance(energy, int) or not isinstance(age, int) or not isinstance(is_alive, bool) or not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Invalid inputs for the Cell attributes")
        self.x = x
        self.y = y
        self.energy = energy
        self.age = age
        self.is_alive = is_alive
        self.genome = Genome()
    def move(self, dx, dy):
        if not isinstance (dx, int) or not isinstance(dy, int):
            raise ValueError("Coordinates must be integers")
        self.x = max(0, min(49, self.x + dx))
        self.y = max(0, min(49, self.y + dy))

    def random_movement(self):
        if self.is_alive:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.move(dx, dy)   
    def update(self):
        if self.is_alive:
            self.random_movement()
            self.age += 1
            self.energy -= 1
            if self.energy <= 0:
                self.is_alive = False
            elif self.age > 100:
                self.is_alive = False
            

    def change_color(self):
        max_energy = 100
        ratio = max(0, min(1, self.energy / max_energy)) #this ensures that the ratio does not exceed 1 (which could cause errors with rgb colouring)
        r = 0
        g = int(ratio * 255)
        b = 0
        return (r, g, b)

    def draw(self, screen, cell_size):
        if self.is_alive:
            pixel_x = self.x * cell_size
            pixel_y = self.y * cell_size
            color = self.change_color()
            pygame.draw.rect(screen, color, (pixel_x, pixel_y, cell_size, cell_size))

    def reproduce(self):
        if self.is_alive and self.energy >=150:
            self.energy //= 2
            self.genome = self.genome.inheritance()
            kid = Cell(max(0, min(49, self.x +random.choice([-1, 0, 1]))), max(0, min(49, self.y + random.choice([-1, 0, 1]))), self.energy)
            return kid
    def __str__(self):
        return f"Cell({self.x},{self.y}, {self.energy}, {self.age}, {self.is_alive})"

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = []
        self.food = []
    def add_cell(self, cell):
        self.cells.append(cell)

    def random_population(self, num_cells):
        for cell in range(num_cells):
            x = random.randint(0,49)
            y = random.randint(0,49)
            cell = Cell(x, y, 100)
            self.cells.append(cell)

    def update_all(self):
        for cell in self.cells:
            cell.update()

        self.cells = [cell for cell in self.cells if cell.is_alive]

    def spawn_food(self):
        fx = random.randint(0, 49)
        fy = random.randint(0, 49)
        self.food.append((fx, fy))

class Genome:
    def __init__(self, speed=1):
        self.speed = speed

    def inheritance(self):
        child_speed = self.speed
        child_speed = child_speed + random.choice([-1, 0, 1])
        child_speed = max(1, child_speed)
        return Genome(speed=child_speed) #meaning a brand new object of genome for the child

def food_drawing(screen, food, cell_size):
        food_size = 8
        offset = (cell_size - food_size) // 2
        for fx, fy in food:
            pixel_x = fx * cell_size + offset
            pixel_y = fy * cell_size + offset
            pygame.draw.rect(screen, (188, 191, 138), (pixel_x, pixel_y, food_size, food_size))
        



def run_game():
    world = World(50,50)
    pygame.init()
    CELL_SIZE = 16
    WINDOW_WIDTH = world.width * CELL_SIZE
    WINDOW_HEIGHT = world.height * CELL_SIZE

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Emergent Ecosystem")

    
    tick_count = 0
    clock = pygame.time.Clock()
    FPS = 10

    world.random_population(50)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        tick_count += 1
        world.update_all()
        if tick_count % 10 == 0:
            world.spawn_food()
        screen.fill((30, 30, 30)) #dark background 
        food_drawing(screen, world.food, CELL_SIZE)
        for cell in world.cells:
            cell.draw(screen, CELL_SIZE)
        

        pygame.display.flip() #always updating the display
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


run_game()