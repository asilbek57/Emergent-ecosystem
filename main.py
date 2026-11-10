import random
import pygame
import sys
import math

#constants
GRID_WIDTH = 120
GRID_HEIGHT = 67
CELL_SIZE = 16
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10

class Genome:
    def __init__(self, speed=1, vision=6):
        self.speed = speed
        self.vision = vision

    def inheritance(self):
        child_speed = self.speed
        child_speed = child_speed + random.choice([-1, 0, 1])
        child_speed = max(1, child_speed)
        child_vision = self.vision
        child_vision = child_vision + random.choice([-1, 0, 1])
        child_vision = max(1, child_vision)
        return Genome(speed=child_speed, vision=child_vision)


class Cell:
    def __init__(self, x, y, energy, age=0, is_alive=True):
        if not isinstance(energy, int) or not isinstance(age, int) or not isinstance(is_alive, bool) or not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Invalid inputs for the Cell attributes")
        self.x = x
        self.y = y
        self.energy = energy
        self.age = age
        self.is_alive = is_alive
        self.genome = Genome()

    def move(self, dx, dy):
        if not isinstance(dx, int) or not isinstance(dy, int):
            raise ValueError("Coordinates must be integers")
        self.x = max(0, min(GRID_WIDTH - 1, self.x + dx))
        self.y = max(0, min(GRID_HEIGHT - 1, self.y + dy))

    def random_movement(self):
        if self.is_alive:
            dx = random.choice([-1, 0, 1]) * self.genome.speed
            dy = random.choice([-1, 0, 1]) * self.genome.speed
            self.move(dx, dy)

    def update(self):
        if self.is_alive:
            self.age += 1
            self.energy -= 1
            if self.energy <= 0:
                self.is_alive = False
            elif self.age > 1000000:
                self.is_alive = False

    def food_seeking(self, food_list):
        if self.is_alive:
            closest_food = None
            min_distance = float('inf')
            for fx, fy in food_list:
                distance = math.hypot(fx - self.x, fy - self.y)
                if distance < min_distance and distance <= self.genome.vision:
                    min_distance = distance
                    closest_food = (fx, fy)
            
            if closest_food:
                fx, fy = closest_food
                dx = 0
                dy = 0
                if fx > self.x:
                    dx = 1
                elif fx < self.x:
                    dx = -1
                
                if fy > self.y:
                    dy = 1
                elif fy < self.y:
                    dy = -1
                self.move(dx, dy)
            else:
                self.random_movement()

    def change_color(self):
        max_energy = 150
        ratio = max(0, min(1, self.energy / max_energy))
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
        if self.is_alive and self.energy >= 150:
            self.energy //= 2
            
            kid = Cell(
                max(0, min(GRID_WIDTH - 1, self.x + random.choice([-1, 0, 1]))),
                max(0, min(GRID_HEIGHT - 1, self.y + random.choice([-1, 0, 1]))),
                self.energy
            )
            kid.genome = self.genome.inheritance()
            return kid
        return None

    def __str__(self):
        return f"Cell({self.x}, {self.y}, energy={self.energy}, age={self.age}, alive={self.is_alive})"


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = []
        self.food = []

    def add_cell(self, cell):
        self.cells.append(cell)

    def random_population(self, num_cells):
        for _ in range(num_cells):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = Cell(x, y, 100)
            self.cells.append(cell)

    def update_all(self):
        newborns = []
        for cell in self.cells:
            cell.update()
            cell.food_seeking(self.food)
            kid = cell.reproduce()
            if kid:
                newborns.append(kid)
        self.cells = [c for c in self.cells if c.is_alive] + newborns
        for cell in self.cells:
            cell.update()
            cell.food_seeking(self.food)
            cell.reproduce()
        self.cells = [cell for cell in self.cells if cell.is_alive]

    def spawn_food(self):
        fx = random.randint(0, self.width - 1)
        fy = random.randint(0, self.height - 1)
        self.food.append((fx, fy))

    def handle_eating(self):
        for i in range(len(self.food) - 1, -1, -1):
            fx, fy = self.food[i]
            eaten = False
            for cell in self.cells:
                if cell.x == fx and cell.y == fy:
                    cell.energy += 50
                    eaten = True
                    break
            if eaten:
                self.food.pop(i)


def food_drawing(screen, food, cell_size):
    food_size = 8 
    offset = (cell_size - food_size) // 2
    for fx, fy in food:
        pixel_x = fx * cell_size + offset
        pixel_y = fy * cell_size + offset
        pygame.draw.rect(screen, (188, 191, 138), (pixel_x, pixel_y, food_size, food_size))


def run_game():
    pygame.init()
    
    world = World(GRID_WIDTH, GRID_HEIGHT)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Emergent Ecosystem")

    tick_count = 0
    clock = pygame.time.Clock()

    world.random_population(300)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        tick_count += 1
        world.update_all()
        world.handle_eating()

        if tick_count % 2 == 0:
            world.spawn_food()

        screen.fill((0, 0, 0)) # dark background
        food_drawing(screen, world.food, CELL_SIZE)
        
        for cell in world.cells:
            cell.draw(screen, CELL_SIZE)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()