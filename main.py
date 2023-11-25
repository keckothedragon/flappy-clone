import pygame
import constants
from utils.base_object import BaseObject
from objects.bird import Bird
from objects.pipe import Pipe
from objects.floor import Floor
from objects.score import Score
from utils.animated import Animated
from utils.movement import Movement


def main():
    pygame.init()
    game_display = pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    running = True

    player_images = [pygame.image.load(image) for image in constants.PLAYER_IMAGES_PATH]
    player = Bird(constants.PLAYER_START_X, constants.PLAYER_START_Y, constants.PLAYER_WIDTH, constants.PLAYER_HEIGHT,
                  constants.PLAYER_JUMP_HEIGHT, game_display, Animated(player_images, 60, 4))

    pipe_image = pygame.image.load(constants.PIPE_IMAGE_PATH)
    pipe = Pipe(constants.PIPE_WIDTH, constants.PIPE_GAP_HEIGHT, game_display, pipe_image)
    pipe2 = Pipe(constants.PIPE_WIDTH, constants.PIPE_GAP_HEIGHT, game_display, pipe_image)
    pipe2.set_x(int((constants.DISPLAY_WIDTH * 1.5) + (constants.PIPE_WIDTH / 2)))

    floor = Floor(constants.DISPLAY_HEIGHT - constants.FLOOR_HEIGHT, constants.FLOOR_HEIGHT, game_display,
                  pygame.image.load(constants.FLOOR_IMAGE_PATH))

    player.set_bounds(((0, constants.DISPLAY_WIDTH), (0, constants.DISPLAY_HEIGHT - constants.FLOOR_HEIGHT)))

    controls = {pygame.K_SPACE: player.jump, pygame.K_UP: player.jump, pygame.K_w: player.jump}

    score = Score(constants.DISPLAY_WIDTH // 2, 20,
                  pygame.font.Font(*constants.SCORE_FONT), constants.SCORE_COLOR, game_display)

    pipe.link_score(score)
    pipe2.link_score(score)

    while running:
        frame_advance = False
        while player.get_movement().get_delta_y() == 0 and running:
            # before player initially jumps
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    controls.get(event.key, lambda: None)()
                    if event.key == pygame.K_BACKSPACE:
                        frame_advance = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    player.jump()

                if event.type == pygame.QUIT:
                    running = False

            game_display.fill(constants.BG_COLOR)

            player.draw()
            floor.update()
            score.draw()

            pygame.display.update()
            clock.tick(60)

        crashed = False
        crash_type = "floor" # default
        while not crashed and running:
            advance = not frame_advance
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    controls.get(event.key, lambda: None)()
                    if event.key == pygame.K_BACKSPACE:
                        frame_advance = True
                        advance = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    player.jump()

                if event.type == pygame.QUIT:
                    running = False

            game_display.fill(constants.BG_COLOR)

            if advance:
                BaseObject.update_all()

                if floor.check_collision(player):
                    crashed = True
                    player.crash()
                    crash_type = "floor"

                if pipe.check_collision(player) or pipe2.check_collision(player):
                    crashed = True
                    player.crash()
                    player.set_movement(Movement(0, 0))
                    crash_type = "pipe"
            else:
                BaseObject.draw_all()

            pygame.display.update()
            clock.tick(60)

        button_pressed = False
        while not button_pressed and running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    button_pressed = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    button_pressed = True

                if event.type == pygame.QUIT:
                    running = False

            game_display.fill(constants.BG_COLOR)

            if crash_type == "pipe":
                # if crashed into pipe, fall to ground, if crashed into ground, do nothing
                player.update()
            BaseObject.draw_all()

            pygame.display.update()
            clock.tick(60)

        BaseObject.reset_all()
        pipe2.set_x(int((constants.DISPLAY_WIDTH * 1.5) + (constants.PIPE_WIDTH / 2)))


if __name__ == "__main__":
    main()
