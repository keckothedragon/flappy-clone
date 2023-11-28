import pygame
import constants
from utils.base_object import BaseObject
from objects.bird import Bird
from objects.pipe import Pipe
from objects.floor import Floor
from objects.score import Score
from objects.menu import Menu
from objects.button import Button
from utils.animated import Animated
from utils.movement import Movement
from utils.file_helper import get_highscore, set_highscore


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
    primary_pipes = Pipe(constants.PIPE_WIDTH, constants.PIPE_GAP_HEIGHT, game_display, pipe_image)
    secondary_pipes = Pipe(constants.PIPE_WIDTH, constants.PIPE_GAP_HEIGHT, game_display, pipe_image)
    secondary_pipes.set_x(int((constants.DISPLAY_WIDTH * 1.5) + (constants.PIPE_WIDTH / 2)))

    floor = Floor(constants.DISPLAY_HEIGHT - constants.FLOOR_HEIGHT, constants.FLOOR_HEIGHT, game_display,
                  pygame.image.load(constants.FLOOR_IMAGE_PATH))

    player.set_bounds(((0, constants.DISPLAY_WIDTH), (0, constants.DISPLAY_HEIGHT - constants.FLOOR_HEIGHT)))

    controls = {pygame.K_SPACE: player.jump, pygame.K_UP: player.jump, pygame.K_w: player.jump}

    score = Score(constants.DISPLAY_WIDTH // 2, 20,
                  pygame.font.Font(*constants.SCORE_FONT), constants.SCORE_COLOR, game_display)

    menu = Menu(
        constants.DISPLAY_WIDTH // 2 - constants.MENU_WIDTH // 2,
        constants.DISPLAY_HEIGHT // 2 - constants.MENU_HEIGHT // 2,
        constants.MENU_WIDTH, constants.MENU_HEIGHT, game_display, pygame.image.load(constants.MENU_IMAGE_PATH),
        (get_highscore(), (constants.DISPLAY_WIDTH // 2 - 80, constants.DISPLAY_HEIGHT // 2 - 80),
         pygame.font.Font(*constants.MENU_FONT), pygame.font.Font(*constants.MENU_NUMBER_FONT))
    )
    menu.add_button(
        Button(constants.DISPLAY_WIDTH // 2 - 25, constants.DISPLAY_HEIGHT // 2 + 10, 50, 50, game_display,
               pygame.image.load("assets/img/menu/play-button.png"),
               lambda: menu.hide())
    )
    menu.add_button(
        Button(constants.DISPLAY_WIDTH // 2 + 65, constants.DISPLAY_HEIGHT // 2 - 138, 18, 18, game_display,
               pygame.image.load("assets/img/menu/quit-button.png"),
               lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
    )

    primary_pipes.link_score(score)
    secondary_pipes.link_score(score)

    while running:
        menu.hide()
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
        crash_type = "floor"  # default, don't move after crash
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

                if primary_pipes.check_collision(player) or secondary_pipes.check_collision(player):
                    crashed = True
                    player.crash()
                    player.set_movement(Movement(0, 0))
                    crash_type = "pipe"
            else:
                BaseObject.draw_all()

            pygame.display.update()
            clock.tick(60)

        if menu.update_highscore(score.get_score()):
            set_highscore(score.get_score())

        menu.show()
        button_pressed = False
        while not menu.hidden and running and not button_pressed:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    button_pressed = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if menu.check_collision_position(*event.pos):
                        for button in menu.buttons:
                            if button.check_collision_position(*event.pos):
                                button.on_click()

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
        secondary_pipes.set_x(int((constants.DISPLAY_WIDTH * 1.5) + (constants.PIPE_WIDTH / 2)))


if __name__ == "__main__":
    main()
