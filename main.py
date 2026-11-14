import random
import pygame
import sys
import math
import numpy as np

GRID_WIDTH = 120
GRID_HEIGHT = 67
CELL_SIZE = 16
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10
STEP = 0.4        # distance moved per tick, per speed point
WANDER = 0.25     # random wobble of the heading per tick (radians)
MAX_TURN = 0.35   # fastest a cell can turn toward a target
DEPOSIT = 1.0     # trail left behind each tick

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
        self.x = float(x)                                   
        self.y = float(y)
        self.heading = random.uniform(0, 2 * math.pi)

    @property
    def gx(self):
        return int(self.x)

    @property
    def gy(self):
        return int(self.y)

    def steer_toward(self, angle):
    # shortest signed angle difference, limited to MAX_TURN
        diff = (angle - self.heading + math.pi) % (2 * math.pi) - math.pi
        self.heading += max(-MAX_TURN, min(MAX_TURN, diff))

    def nearest_food(self, food_list):
        best, best_d = None, self.genome.vision
        for fx, fy in food_list:
            d = math.hypot(fx - self.x, fy - self.y)
            if d <= best_d:
                best, best_d = (fx, fy), d
        return best

    def move_forward(self):
        step = STEP * self.genome.speed
        self.x += math.cos(self.heading) * step
        self.y += math.sin(self.heading) * step
        if self.x < 0 or self.x > GRID_WIDTH - 1: # bounce off walls
            self.heading = math.pi - self.heading
            self.x = max(0.0, min(GRID_WIDTH - 1.0, self.x))
        if self.y < 0 or self.y > GRID_HEIGHT - 1:
            self.heading = -self.heading
            self.y = max(0.0, min(GRID_HEIGHT - 1.0, self.y))

    def act(self, food_list, trail):
        if not self.is_alive:
            return
        self.heading += random.uniform(-WANDER, WANDER)
        target = self.nearest_food(food_list)
        if target:
            self.steer_toward(math.atan2(target[1] + 0.5 - self.y, target[0] + 0.5 - self.x))
        self.move_forward()
        trail[self.gx, self.gy] += DEPOSIT

    def update(self):
        if self.is_alive:
            self.age += 1
            self.energy -= 1
            if self.energy <= 0:
                self.is_alive = False
            elif self.age > 1000:
                self.is_alive = False

    def change_color(self):
        max_energy = 150
        ratio = max(0, min(1, self.energy / max_energy))
        r = int(ratio * 56)
        g = int(ratio * 207)
        b = int(ratio * 194)
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
                max(0, min(GRID_WIDTH - 1, self.gx + random.choice([-1, 0, 1]))),
                max(0, min(GRID_HEIGHT - 1, self.gy + random.choice([-1, 0, 1]))),
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
        self.trail = np.zeros((width, height), dtype=np.float32)

    def update_trail(self, decay=0.98, spread=0.2):
        neighbors = (np.roll(self.trail, 1, 0) + np.roll(self.trail, -1, 0) +
                    np.roll(self.trail, 1, 1) + np.roll(self.trail, -1, 1)) / 4
        self.trail = (self.trail * (1 - spread) + neighbors * spread) * decay

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
            cell.act(self.food, self.trail)
            kid = cell.reproduce()
            if kid:
                newborns.append(kid)
        self.cells = [c for c in self.cells if c.is_alive] + newborns


    def spawn_food(self):
        fx = random.randint(0, self.width - 1)
        fy = random.randint(0, self.height - 1)
        self.food.append((fx, fy))

    def handle_eating(self):
        for i in range(len(self.food) - 1, -1, -1):
            fx, fy = self.food[i]
            eaten = False
            for cell in self.cells:
                if cell.gx == fx and cell.gy == fy:
                    self.trail[cell.gx, cell.gy] += 10
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
        pygame.draw.rect(screen, (242, 172, 232), (pixel_x, pixel_y, food_size, food_size))

def trail_drawing(screen, trail):
        #brightness clipped to 0-1 range
        v = np.clip(trail / 5, 0, 1)
        #square root to enhance contrast
        v = np.sqrt(v)        
        rgb = np.zeros((trail.shape[0], trail.shape[1], 3), dtype=np.uint8)
        #cyan - [120, 180, 255]
        #bright green - [53, 222, 98]
        red = 53
        green = 222
        blue = 98
        #[...] is short for [:,:,:], all dimensions
        rgb[..., 0] = (v * red).astype(np.uint8)
        rgb[..., 1] = (v * green).astype(np.uint8)
        rgb[..., 2] = (v * blue).astype(np.uint8)
        surf = pygame.surfarray.make_surface(rgb)
        surf = pygame.transform.smoothscale(surf, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(surf, (0, 0))

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

        screen.fill((0, 0, 0)) #background
    
        trail_drawing(screen, world.trail)
        world.update_trail()

        food_drawing(screen, world.food, CELL_SIZE)
        
        for cell in world.cells:
            cell.draw(screen, CELL_SIZE)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()