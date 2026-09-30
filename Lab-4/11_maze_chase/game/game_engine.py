import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)

        self.player = Player(0, 0)

        # Task 1: Multiple enemies
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),
            Enemy(ROWS - 1, 0),
            Enemy(0, COLS - 1),
        ]

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.caught = False
        self.won = False

        # Task 2: Difficulty ramp
        self.start_time = pygame.time.get_ticks()
        self.speed_tier = 1

        # Task 3: Power pellet
        # Place it at a different cell from the exit.
        pellet_col = 2
        pellet_row = 2

        self.pellet_rect = pygame.Rect(
            pellet_col * CELL + CELL // 2 - 8,
            pellet_row * CELL + CELL // 2 - 8,
            16,
            16
        )

        self.pellet_active = True

        # Task 4: Score by distance
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

        return True

    def update(self):
        if self.caught or self.won:
            return

        # Task 4: Increase score every frame while player is alive
        self.score += 1

        # Task 2: Calculate elapsed time
        elapsed = pygame.time.get_ticks() - self.start_time

        # Increase speed tier every 15 seconds
        new_tier = elapsed // 15000 + 1

        if new_tier != self.speed_tier:
            self.speed_tier = new_tier

            # Reduce enemy movement interval by 2 every tier.
            # Minimum interval is 5.
            new_interval = max(
                5,
                20 - (self.speed_tier - 1) * 2
            )

            # Apply the new speed to all enemies
            for enemy in self.enemies:
                enemy.move_interval = new_interval

        # Player movement
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # Task 3: Power pellet collision
        if self.pellet_active and self.player.rect.colliderect(self.pellet_rect):
            self.pellet_active = False

            # Freeze all enemies for 5 seconds
            for enemy in self.enemies:
                enemy.freeze()

        # Update all enemies independently
        for enemy in self.enemies:
            enemy.update(
                self.walls,
                self.player,
                ROWS,
                COLS
            )

            # Collision with any enemy
            if self.player.rect.colliderect(enemy.rect):
                self.caught = True

        # Check exit
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))

        wc = (50, 40, 60)

        # Draw maze
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]

                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x + CELL, y),
                        3
                    )

                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x, y + CELL),
                        3
                    )

        # Draw exit
        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4
        )

        lbl = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            lbl,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 6
            )
        )

        # Task 3: Draw power pellet
        if self.pellet_active:
            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                self.pellet_rect.center,
                8
            )

        # Draw player
        self.player.draw(self.screen)

        # Task 1: Draw all enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD
        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            50
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        # Task 2 + Task 4: Show speed tier and survived time
        info = self.font.render(
            f"Reach EXIT!  Speed Tier: {self.speed_tier}  "
            f"Survived: {self.score // 60}s  R=Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            info,
            (
                8,
                ROWS * CELL + 14
            )
        )

        # Game over overlays
        if self.caught:
            self._overlay(
                "CAUGHT!",
                (220, 60, 60)
            )

        if self.won:
            self._overlay(
                "ESCAPED!",
                (80, 220, 80)
            )

        pygame.display.flip()

    def _overlay(self, text, color):
        surf = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA
        )

        surf.fill(
            (0, 0, 0, 140)
        )

        self.screen.blit(
            surf,
            (0, 0)
        )

        msg = self.big_font.render(
            text,
            True,
            color
        )

        # Task 4: Show final score
        final_score = self.font.render(
            f"Final Score: {self.score}",
            True,
            (255, 255, 255)
        )

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            msg,
            (
                WIDTH // 2 - msg.get_width() // 2,
                ROWS * CELL // 2 - 60
            )
        )

        self.screen.blit(
            final_score,
            (
                WIDTH // 2 - final_score.get_width() // 2,
                ROWS * CELL // 2
            )
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2 - sub.get_width() // 2,
                ROWS * CELL // 2 + 40
            )
        )

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()