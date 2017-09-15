import sys, pygame
from game_settings import *
import random

pygame.init()

size = (screen_width, screen_height)

game_screen = pygame.display.set_mode(size)

pygame.display.set_caption('Snake')

clock = pygame.time.Clock()

snakeImg = pygame.image.load('white_square.png')
pelletImg = pygame.image.load('yellow_circle.png')
pause = False
sound = True
score_sound = pygame.mixer.Sound(file="beep_short.wav")
button_click_sound = pygame.mixer.Sound(file="click.wav")
score_sound.set_volume(0.3)
button_click_sound.set_volume(0.7)


def snake(x, y):
    game_screen.blit(snakeImg, (x, y))


def update_snake_stats(snake_stats, x_dir, y_dir):
    """Updates snake movements by deleting last block, and pushing the rest of the x, y
       coordinates forward one"""
    new_stats = snake_stats[:]

    new_stats.insert(0, [snake_stats[0][0] + x_dir, snake_stats[0][1] + y_dir, x_dir, y_dir])
    del new_stats[-1]

    return new_stats


def add_snake(x, y, x_dir, y_dir):
    """Gives x, y, x_dir, y_dir of next snake block"""
    if x_dir > 0 and y_dir == 0:
        return [x - pellet_size, y, x_dir, y_dir]
    elif x_dir < 0 and y_dir == 0:
        return [x + pellet_size, y, x_dir, y_dir]
    elif y_dir > 0 and x_dir == 0:
        return [x, y + pellet_size, x_dir, y_dir]
    elif y_dir < 0 and x_dir == 0:
        return [x, y - pellet_size, x_dir, y_dir]


def snake_collision(snake_stats):
    """Check to see if snake contacts itself"""
    x_y_coords = []
    tested = []

    for block in snake_stats:
        x_y_coords += [block[0:2]]

    for test in x_y_coords:
        if test in tested:
            return True
        else:
            tested += [test]

    return False


def pellet(pellet_x, pellet_y):
    game_screen.blit(pelletImg, (pellet_x, pellet_y))


def pellet_snake_spawn(snake_stats, pellet_x, pellet_y):
    """Produce true if pellet spawns in snake path"""
    x_y_coords = []
    pellet_location = [pellet_x, pellet_y]

    for block in snake_stats:
        x_y_coords += [block[0:2]]

    for test in x_y_coords:
        if pellet_location == test:
            return True
    return False


def get_pellet_coordinate(snake_stats):
    """Produces random pellet coordinate that does not contact snake path"""
    while True:
        pellet_x = random.randrange(0, screen_width, pellet_size)
        pellet_y = random.randrange(0, screen_height, pellet_size)
        if not pellet_snake_spawn(snake_stats, pellet_x, pellet_y):
            break

    return pellet_x, pellet_y


def pellet_contact(x, y, pellet_x, pellet_y):
    """Returns true if snake x, y contacts with pellet x, y"""
    if x == pellet_x and y == pellet_y:
        return True
    else:
        return False


def direction_change(event, x_dir, y_dir, snake_stats):
    """Performs direction change if arrow keys are pressed"""
    snake_length = len(snake_stats)
    if event.key == pygame.K_LEFT:
        if snake_length == 1 or not snake_stats[0][0] > snake_stats[1][0]:
            x_dir, y_dir = -1 * snake_speed, 0
    elif event.key == pygame.K_RIGHT:
        if snake_length == 1 or not snake_stats[0][0] < snake_stats[1][0]:
            x_dir, y_dir = snake_speed, 0
    elif event.key == pygame.K_UP:
        if snake_length == 1 or not snake_stats[0][1] > snake_stats[1][1]:
            x_dir, y_dir = 0, -1 * snake_speed
    elif event.key == pygame.K_DOWN:
        if snake_length == 1 or not snake_stats[0][1] < snake_stats[1][1]:
            x_dir, y_dir = 0, snake_speed
    return x_dir, y_dir


def boundary_check(snake_stats):
    """Produce true if past edges of game"""
    if snake_stats[0][0] < 0 or snake_stats[0][0] > screen_width - snake_size or snake_stats[0][1] < 0 or snake_stats[0][1] > screen_height - snake_size:
        return True
    else:
        return False


def text_objects(text, font):
    text_surface = font.render(text, True, white)
    return text_surface, text_surface.get_rect()


def button(message, x, y, width, height, click_x, click_y, inactive_color, active_color, action=None, arg=None):
    """Produce button of certain dimensions that highlights when cursor is over
       and performs action if clicked"""

    mouse_pos = pygame.mouse.get_pos()

    if x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height :
        pygame.draw.rect(game_screen, active_color, (x, y, width, height))

        if x < click_x < x + width and y < click_y < y + height :
            if sound:
                pygame.mixer.Sound.play(button_click_sound)
            if arg is None:
                action()
            else:
                action(arg)
    else:
        pygame.draw.rect(game_screen, inactive_color, (x, y, width, height))

    small_text = pygame.font.Font("freesansbold.ttf", 20)
    text_surf, text_rect = text_objects(message, small_text)
    text_rect.center = ((x + (width / 2)), (y + (height / 2)))
    game_screen.blit(text_surf, text_rect)


def pellets_eaten(score):
    font = pygame.font.SysFont(None, 25)
    text = font.render("Score: " + str(score), True, bright_red)
    game_screen.blit(text, (0, 0))


def display_difficulty(speed_modifier):
    font = pygame.font.SysFont(None, 25)
    if speed_modifier == diff_mod_easy:
        difficulty, color = "Easy", bright_green
    elif speed_modifier == diff_mod_med:
        difficulty, color = "Medium", bright_yellow
    elif speed_modifier == diff_mod_hard:
        difficulty, color = "Hard", bright_red
    text = font.render("Difficulty: " + str(difficulty), True, color)
    font_dimensions = font.size("Difficulty: " + str(difficulty))
    game_screen.blit(text, (screen_width - font_dimensions[0], 0))


def display_sound_toggle(sound):
    if sound:
        on_off = "Mute"
    else:
        on_off = "Unmute"
    font = pygame.font.SysFont(None, 20)
    text = font.render("{} sound (s)".format(on_off), True, white)
    font_dimensions = font.size("{} sound (s)".format(on_off))
    game_screen.blit(text, (0, screen_height - font_dimensions[1]))


def game_over(score, speed_modifier):
    game_is_over = True
    global sound
    pygame.mouse.set_visible(True)
    click_x, click_y = 0, 0

    while game_is_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_s:
                    sound = not sound
            if (event.type == pygame.MOUSEBUTTONDOWN and
                event.__dict__['button'] == 1):
                click_x, click_y = event.__dict__['pos'][0], event.__dict__['pos'][1]

        game_screen.fill(black)
        display_sound_toggle(sound)
        large_text = pygame.font.Font('freesansbold.ttf', 50)
        text_surf, text_rect = text_objects("GAME OVER", large_text)
        text_rect.center = ((screen_width // 2), 140)
        game_screen.blit(text_surf, text_rect)

        small_text = pygame.font.Font('freesansbold.ttf', 25)
        text_surf, text_rect = text_objects("Your score was: {}".format(score), small_text)
        text_rect.center = ((screen_width // 2), 200)
        game_screen.blit(text_surf, text_rect)

        button("Play again", 250, 240, 120, 60, click_x, click_y, green, bright_green, game_loop, speed_modifier)
        button("Start menu", 70, 240, 120, 60, click_x, click_y, red, bright_red, game_intro)

        pygame.display.update()
        clock.tick(15)


def quit_game():
    pygame.quit()
    sys.exit()


def game_intro():
    intro = True
    global sound
    click_x, click_y = 0, 0

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    sound = not sound
            elif (event.type == pygame.MOUSEBUTTONDOWN and
                event.__dict__['button'] == 1):
                click_x, click_y = event.__dict__['pos'][0], event.__dict__['pos'][1]

        game_screen.fill(black)
        display_sound_toggle(sound)
        large_text = pygame.font.Font('freesansbold.ttf', 75)
        text_surf, text_rect = text_objects("SNAKE", large_text)
        text_rect.center = ((screen_width // 2), 140)
        game_screen.blit(text_surf, text_rect)

        button("Start!", 260, 240, 100, 60, click_x, click_y, green, bright_green, set_difficulty)
        button("Quit", 80, 240, 100, 60, click_x, click_y, red, bright_red, quit_game)

        pygame.display.update()
        clock.tick(15)


def set_difficulty():
    difficulty_screen = True
    global sound
    click_x, click_y = 0, 0

    while difficulty_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    sound = not sound
            elif (event.type == pygame.MOUSEBUTTONDOWN and
                event.__dict__['button'] == 1):
                click_x, click_y = event.__dict__['pos'][0], event.__dict__['pos'][1]

        game_screen.fill(black)
        display_sound_toggle(sound)
        large_text = pygame.font.Font('freesansbold.ttf', 38)
        text_surf, text_rect = text_objects("CHOOSE DIFFICULTY", large_text)
        text_rect.center = ((screen_width // 2), 140)
        game_screen.blit(text_surf, text_rect)

        button("Easy", 50, 240, 90, 60, click_x, click_y, green, bright_green, game_loop, diff_mod_easy)
        button("Medium", 175, 240, 90, 60, click_x, click_y, yellow, bright_yellow, game_loop, diff_mod_med)
        button("Hard", 300, 240, 90, 60, click_x, click_y, red, bright_red, game_loop, diff_mod_hard)

        pygame.display.update()
        clock.tick(15)


def unpause():
    global pause
    pause = False


def game_pause():
    global pause
    pause = True
    global sound
    pygame.mouse.set_visible(True)
    click_x, click_y = 0, 0

    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_s:
                    sound = not sound
            if (event.type == pygame.MOUSEBUTTONDOWN and
                event.__dict__['button'] == 1):
                click_x, click_y = event.__dict__['pos'][0], event.__dict__['pos'][1]

        game_screen.fill(black)
        large_text = pygame.font.Font('freesansbold.ttf', 50)
        text_surf, text_rect = text_objects("PAUSED", large_text)
        text_rect.center = ((screen_width // 2), 140)
        game_screen.blit(text_surf, text_rect)

        button("Continue", 260, 240, 100, 60, click_x, click_y, green, bright_green, unpause)
        button("Quit", 80, 240, 100, 60, click_x, click_y, red, bright_red, quit_game)

        pygame.display.update()
        clock.tick(15)


def game_loop(speed_modifier):
    global sound
    x, y = screen_width // 2, screen_height // 2
    x_dir, y_dir = 0, -1 * snake_speed
    snake_stats = [[x, y, x_dir, y_dir]]
    pellet_x, pellet_y = get_pellet_coordinate(snake_stats)
    snake_length = 1
    score = 0
    game_exit = False
    pygame.mouse.set_visible(False)

    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or
                    event.key == pygame.K_UP or event.key == pygame.K_DOWN):
                    x_dir, y_dir = direction_change(event, x_dir, y_dir, snake_stats)
                elif event.key == pygame.K_s:
                    sound = not sound
                elif event.key == pygame.K_p:
                    game_pause()

        snake_stats = update_snake_stats(snake_stats, x_dir, y_dir)
        x, y = snake_stats[0][0], snake_stats[0][1]

        game_screen.fill(black)
        pellet(pellet_x, pellet_y)

        for snakes in snake_stats:
            snake(snakes[0], snakes[1])

        pellets_eaten(score)
        display_difficulty(speed_modifier)
        display_sound_toggle(sound)

        if boundary_check(snake_stats) or snake_collision(snake_stats):
            game_over(score, speed_modifier)

        if pellet_contact(snake_stats[0][0], snake_stats[0][1], pellet_x, pellet_y):
            if sound:
                pygame.mixer.Sound.play(score_sound)
            snake_stats.append(add_snake(x, y, x_dir, y_dir))
            snake_length += 1
            score += 1
            pellet_x, pellet_y = get_pellet_coordinate(snake_stats)

        pygame.display.update()
        clock.tick(speed_modifier)

game_intro()
quit_game()
