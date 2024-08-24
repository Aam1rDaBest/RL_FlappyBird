import pygame
import random
import time
import os
from CustomEnvironment import CustomEnvironment
from database import GameDatabase
import csv
import sys
import inspect

# Global variable to determine main function loop break (separate to FlappyBirdGame)
end_decision = False


class FlappyBirdGame:
    def __init__(self, difficulty, mode):
        # Initialize Pygame
        pygame.init()

        # Set up paths for images
        current_dir = os.path.dirname(__file__)
        image_dir = os.path.join(current_dir, "images")
        sound_dir = os.path.join(current_dir, "sounds")

        # Load sounds
        sound_go_path = os.path.join(sound_dir, "game_over.mp3")
        self.game_over_sound = pygame.mixer.Sound(sound_go_path)

        sound_fl_path = os.path.join(sound_dir, "flap.mp3")
        self.flap_sound = pygame.mixer.Sound(sound_fl_path)

        sound_count_path = os.path.join(sound_dir, "countdown.mp3")
        self.countdown_sound = pygame.mixer.Sound(sound_count_path)
        self.countdown_sound.set_volume(0.5)

        sound_start_path = os.path.join(sound_dir, "start.mp3")
        self.start_sound = pygame.mixer.Sound(sound_start_path)

        # Load images
        self.background_image = pygame.image.load(
            os.path.join(image_dir, "background.png")
        )
        self.pipe_image = pygame.image.load(os.path.join(image_dir, "pipe.png"))
        self.bird_image = pygame.image.load(os.path.join(image_dir, "bird.png"))
        self.retry_image = pygame.image.load(os.path.join(image_dir, "reload_2.png"))
        self.end_image = pygame.image.load(os.path.join(image_dir, "exit.png"))

        # Rescale images
        self.background_image = pygame.transform.scale(
            self.background_image, (650, 500)
        )
        self.bird_image = pygame.transform.scale(self.bird_image, (60, 60))
        self.pipe_image = pygame.transform.scale(self.pipe_image, (50, 300))

        self.top_pipe_image = pygame.transform.flip(self.pipe_image, False, True)
        self.retry_image = pygame.transform.scale(self.retry_image, (70, 60))
        self.end_image = pygame.transform.scale(self.end_image, (40, 40))

        # Set event handling attributes
        self.retry_hover_start_time = 0
        self.dead_fall_time = 0
        self.dead_turn = False
        self.mode = mode

        # Set and load in pipe variables based on difficulty
        if self.mode == "vis":
            self.death = False
            self.death_mode = difficulty.replace(" vis", "")
            difficulty = "normal"
        self.difficulty = difficulty
        self.should_continue_running = True

        self.read_attributes_from_csv()

        # Bird variables
        self.bird_x = 60
        self.bird_y = 200
        self.bird_velocity = 0
        self.gravity = 0.22
        self.flap_force = -5.4  # This will be the force applied when the bird flaps

        # Pipes variables (that weren't set yet)
        self.pipe_width = 50
        self.pipes = []

        # Game state variables
        self.game_active = True
        self.paused = False
        self.dead = False
        self.submitted_name = False

        # Score/Result variables
        self.score = 0
        self.ai_score = None
        self.reward = 0
        self.current_actions = []

        # Pygame window setup
        self.win_width, self.win_height = 650, 500
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.font_color = (255, 255, 255)

        # Initialise database and set high score
        self.db = GameDatabase()
        self.high_score = self.db.get_highest_score(self.mode, self.difficulty)
        if self.high_score is None:
            self.high_score = 0

    def read_attributes_from_csv(self):
        # Define the CSV file path based on difficulty
        csv_filename = f"{self.difficulty}_attributes.csv"

        # Read attribute values from CSV
        with open(csv_filename, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.pipe_gap = int(row["pipe_gap"])
                self.pipe_distance = int(row["pipe_distance"])
                self.min_pipe_height = int(row["min_pipe_height"])
                self.pipe_speed = float(row.get("pipe_speed"))
                self.pipe_render = int(row.get("pipe_render"))

    def show_popup(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (0, 0, 255)
        RED = (255, 0, 0)

        # Define font
        font = pygame.font.Font(None, 36)

        # Create the popup rectangle
        popup_width, popup_height = 400, 200
        popup_rect = pygame.Rect(
            (self.win_width - popup_width) // 2,
            (self.win_height - popup_height) // 2,
            popup_width,
            popup_height,
        )

        # Create buttons
        button_width, button_height = 150, 50
        replay_button = pygame.Rect(
            (popup_rect.left + popup_width // 4) - button_width // 2,
            popup_rect.top + popup_height // 2 - button_height // 2,
            button_width,
            button_height,
        )
        end_button = pygame.Rect(
            (popup_rect.left + 3 * popup_width // 4) - button_width // 2,
            popup_rect.top + popup_height // 2 - button_height // 2,
            button_width,
            button_height,
        )

        # Main loop for the popup
        popup_running = True
        while popup_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Replay pressed
                    if replay_button.collidepoint(mouse_pos):
                        global end_decision
                        end_decision = False
                        popup_running = False
                        return
                    # End pressed
                    elif end_button.collidepoint(mouse_pos):
                        end_decision = True
                        popup_running = False
                        return

            # Draw the popup background
            pygame.draw.rect(self.win, WHITE, popup_rect)
            pygame.draw.rect(self.win, BLACK, popup_rect, 2)

            # Draw buttons
            pygame.draw.rect(self.win, BLUE, replay_button)
            pygame.draw.rect(self.win, BLACK, replay_button, 2)
            pygame.draw.rect(self.win, RED, end_button)
            pygame.draw.rect(self.win, BLACK, end_button, 2)

            # Render and draw text
            if self.mode == "vis":
                question_text = font.render("Objective Achieved", True, BLACK)
                self.win.blit(
                    question_text, (popup_rect.left + 90, popup_rect.top + 25)
                )
            else:
                question_text = font.render(
                    "Do you want to Replay or Exit?", True, BLACK
                )
                self.win.blit(
                    question_text, (popup_rect.left + 20, popup_rect.top + 25)
                )
            replay_text = font.render("Replay", True, BLACK)
            self.win.blit(replay_text, (replay_button.x + 30, replay_button.y + 15))

            end_text = font.render("Exit", True, BLACK)
            self.win.blit(end_text, (end_button.x + 50, end_button.y + 15))

            # Update the display
            pygame.display.flip()

    def get_state_space(self):
        # Return dictionary of state space
        return {
            "bird_x": self.bird_x,
            "bird_y": self.bird_y,
            "bird_velocity": self.bird_velocity,
            "pipes": self.pipes,
            "game_active": self.game_active,
            "paused": self.paused,
            "score": self.score,
        }

    def get_action(self):
        # Return dictionary containing values of action
        return {
            "flap": 1,
            "do_nothing": 0,
        }

    def get_action_space(self):
        # Return the action space
        return self.current_actions

    def generate_pipe(self):
        # Generates lists for the pipes on screen
        top_pipe_height = random.randint(
            self.min_pipe_height, self.win_height - self.min_pipe_height - self.pipe_gap
        )
        top_pipe_pos = (self.win_width, top_pipe_height)
        bottom_pipe_pos = (self.win_width, top_pipe_height + self.pipe_gap)
        self.pipes.append((top_pipe_pos, bottom_pipe_pos))

        # Remove first item pipe if it's no longer on screen
        if len(self.pipes) > 4:
            self.pipes.pop(0)

    def death_animation(self):
        # Plays an animation on collision
        if self.dead_turn == False:
            pygame.time.delay(200)
            self.game_over_sound.play()
            self.bird_image = pygame.transform.rotate(self.bird_image, -90)
            self.dead_turn = True
        if self.bird_y < 450:
            self.bird_y += 5
        return

    def username(self):
        # Define the alphabet characters
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

        # Define font
        font = pygame.font.Font(None, 40)

        # Define arrow parameters
        arrow_width = 20
        arrow_height = 10
        arrow_padding = 5

        # Define arrow rectangles
        arrow_up_rects = []
        arrow_down_rects = []
        for i in range(6):
            cell_rect = pygame.Rect(160 + i * (320 // 6), 125, 320 // 6, 245)
            arrow_up_rect = pygame.Rect(
                cell_rect.centerx - arrow_width // 2,
                cell_rect.centery - arrow_height - arrow_padding - 30,
                arrow_width,
                arrow_height,
            )
            arrow_down_rect = pygame.Rect(
                cell_rect.centerx - arrow_width // 2,
                cell_rect.centery + arrow_padding + arrow_height + 20,
                arrow_width,
                arrow_height,
            )
            arrow_up_rects.append(arrow_up_rect)
            arrow_down_rects.append(arrow_down_rect)

        # Define submit button parameters
        submit_button_width = 130
        submit_button_height = 45
        submit_button_rect = pygame.Rect(
            (self.win_width - submit_button_width) // 2,
            370,
            submit_button_width,
            submit_button_height,
        )
        button_radius = 10

        # Define colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (0, 128, 255)
        SILVER = (192, 192, 192)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)
        DARK_GREEN = (0, 120, 0)

        # Store current character index for each cell
        current_char_indices = [0, 0, 0, 0, 0, 0]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the mouse is clicked on the arrows
                    mouse_pos = pygame.mouse.get_pos()
                    for i in range(6):
                        if arrow_up_rects[i].collidepoint(mouse_pos):
                            current_char_indices[i] = (
                                current_char_indices[i] + 1
                            ) % len(alphabet)
                        elif arrow_down_rects[i].collidepoint(mouse_pos):
                            current_char_indices[i] = (
                                current_char_indices[i] - 1
                            ) % len(alphabet)
                    # Check if the mouse is clicked on the submit button
                    if submit_button_rect.collidepoint(mouse_pos):
                        selected_characters = [
                            alphabet[idx] for idx in current_char_indices
                        ]
                        selected_characters = "".join(
                            alphabet[idx] for idx in current_char_indices
                        )
                        return selected_characters

            # Draw the username screen
            pygame.draw.rect(
                self.win, BLUE, (100, 50, 440, 380)
            )  # Main background rectangle

            pygame.draw.rect(self.win, SILVER, (110, 60, 420, 360))  # Inner rectangle

            # Draw border around the screen
            pygame.draw.rect(self.win, BLACK, (100, 50, 440, 380), width=6)

            # Draw decorative elements
            # Add diagonal lines based on the inner rectangle
            pygame.draw.line(self.win, BLACK, (110, 60), (530, 420), width=2)
            pygame.draw.line(self.win, BLACK, (530, 60), (110, 420), width=2)

            # Add circles based on the inner rectangle
            pygame.draw.circle(self.win, BLACK, (110, 60), 10)
            pygame.draw.circle(self.win, BLACK, (530, 60), 10)
            pygame.draw.circle(self.win, BLACK, (110, 420), 10)
            pygame.draw.circle(self.win, BLACK, (530, 420), 10)

            # Draw diamond-shaped content area
            diamond_width = 420
            diamond_height = 360
            diamond_center_x = 100 + 440 // 2
            diamond_center_y = 50 + 380 // 2
            diamond_points = [
                (diamond_center_x, diamond_center_y - diamond_height // 2),  # Top point
                (
                    diamond_center_x + diamond_width // 2,
                    diamond_center_y,
                ),  # Right point
                (
                    diamond_center_x,
                    diamond_center_y + diamond_height // 2,
                ),  # Bottom point
                (diamond_center_x - diamond_width // 2, diamond_center_y),  # Left point
            ]
            pygame.draw.polygon(self.win, BLUE, diamond_points)

            # Draw alphabet cells with scrolling logic
            cell_width = 320 // 6
            cell_height = 360 // 6
            for i in range(6):
                cell_rect = pygame.Rect(
                    160 + i * cell_width,
                    125 + (245 - cell_height) // 2,
                    cell_width,
                    cell_height,
                )
                pygame.draw.rect(self.win, SILVER, cell_rect, 2)

                # Draw arrow above cell
                arrow_up_rect = arrow_up_rects[i]
                arrow_up_points = [
                    (arrow_up_rect.left, arrow_up_rect.bottom),
                    (arrow_up_rect.centerx, arrow_up_rect.top),
                    (arrow_up_rect.right, arrow_up_rect.bottom),
                ]
                arrow_up_color = (
                    GREEN
                    if arrow_up_rects[i].collidepoint(pygame.mouse.get_pos())
                    else BLACK
                )
                pygame.draw.polygon(self.win, arrow_up_color, arrow_up_points)

                # Draw arrow below cell
                arrow_down_rect = arrow_down_rects[i]
                arrow_down_points = [
                    (arrow_down_rect.left, arrow_down_rect.top),
                    (arrow_down_rect.centerx, arrow_down_rect.bottom),
                    (arrow_down_rect.right, arrow_down_rect.top),
                ]
                arrow_down_color = (
                    RED
                    if arrow_down_rects[i].collidepoint(pygame.mouse.get_pos())
                    else BLACK
                )
                pygame.draw.polygon(self.win, arrow_down_color, arrow_down_points)

                # Draw the alphabet character based on current index
                char_surface = font.render(
                    alphabet[current_char_indices[i]], True, BLACK
                )
                char_rect = char_surface.get_rect(
                    center=(cell_rect.centerx, cell_rect.centery)
                )
                self.win.blit(char_surface, char_rect)

            # Draw the submit button
            pygame.draw.rect(
                self.win,
                SILVER,
                (
                    ((self.win_width - submit_button_width) // 2) - 5,
                    365,
                    submit_button_width + 10,
                    submit_button_height + 10,
                ),
            )
            if submit_button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(
                    self.win,
                    BLACK,
                    submit_button_rect.move(5, 5),
                    border_radius=button_radius,
                )  # Shadow

                pygame.draw.rect(
                    self.win,
                    DARK_GREEN,
                    submit_button_rect,
                    border_radius=button_radius,
                )
            else:
                pygame.draw.rect(
                    self.win, GREEN, submit_button_rect, border_radius=button_radius
                )
            submit_text = font.render("Submit", True, WHITE)
            submit_text_rect = submit_text.get_rect(center=submit_button_rect.center)
            self.win.blit(submit_text, submit_text_rect)

            # Draw the "Enter Name:" text
            enter_name_text = font.render("Enter Name:", None, BLACK)
            enter_name_text_rect = enter_name_text.get_rect(
                center=(self.win_width // 2, 175)
            )
            self.win.blit(enter_name_text, enter_name_text_rect)

            font_two = pygame.font.Font(None, 25)
            top_score_text = font_two.render("Leaderboard Entry", None, BLACK)
            top_score_rect = top_score_text.get_rect(center=(self.win_width // 2, 140))
            self.win.blit(top_score_text, top_score_rect)

            # Update the display
            pygame.display.flip()

    def handle_buttons(self, buttons):

        # Define colors
        BLACK = (0, 0, 0)
        GOLD = (255, 215, 0)
        GREEN = (0, 128, 0)
        DARK_GREEN = (0, 100, 0)

        # Draw the pause screen
        pygame.draw.rect(
            self.win, GOLD, (100, 80, 440, 350)
        )  # Main background rectangle
        pygame.draw.rect(self.win, DARK_GREEN, (110, 90, 420, 330))  # Inner rectangle

        # Draw border around the screen
        pygame.draw.rect(self.win, BLACK, (100, 80, 440, 350), width=6)

        # Draw decorative elements
        # Add diagonal lines based on the inner rectangle
        pygame.draw.line(self.win, BLACK, (110, 90), (530, 420), width=2)
        pygame.draw.line(self.win, BLACK, (530, 90), (110, 420), width=2)

        # Add circles based on the inner rectangle
        pygame.draw.circle(self.win, BLACK, (110, 90), 10)
        pygame.draw.circle(self.win, BLACK, (530, 90), 10)
        pygame.draw.circle(self.win, BLACK, (110, 420), 10)
        pygame.draw.circle(self.win, BLACK, (530, 420), 10)

        outer_rect = pygame.Rect(190, 150, 260, 220)
        pygame.draw.rect(self.win, BLACK, outer_rect, border_radius=5)
        inner_rect = outer_rect.inflate(-5, -5)
        pygame.draw.rect(self.win, GREEN, inner_rect)

        # Handle text displayed
        font = pygame.font.Font(None, 65)
        if self.paused == True:
            text_surface = font.render("PAUSED", True, (215, 190, 0))
        elif self.paused != True:
            if self.mode == "pvc":
                if self.ai_score is not None:
                    font = pygame.font.Font(None, 55)
                    if self.ai_score < self.score:
                        text_surface = font.render("YOU WON", True, (215, 190, 0))
                    elif self.ai_score == self.score:
                        text_surface = font.render("YOU DREW", True, (215, 190, 0))
                    else:
                        text_surface = font.render("YOU LOST", True, (215, 190, 0))
                else:
                    text_surface = font.render("FINISH", True, (215, 190, 0))
            else:
                text_surface = font.render("FINISH", True, (215, 190, 0))
        self.win.blit(
            text_surface, (170 + 310 // 2 - text_surface.get_width() // 2, 100)
        )

        # Loop to create buttons
        for button in buttons:
            pygame.draw.rect(
                self.win, button["color"], button["rect"], border_radius=20
            )

            # Calculate the position for the text
            text_rect = button["text"].get_rect()
            text_rect.centery = button["rect"].centery
            text_rect.left = button["rect"].left + 20

            # Blit the text
            self.win.blit(button["text"], text_rect)

            # Check if the current button is the retry button
            if button["action"] == "retry":
                # Calculate the position for the image
                retry_image_rect = self.retry_image.get_rect()
                retry_image_rect.centery = button["rect"].centery
                retry_image_rect.right = button["rect"].right - 10

                # Blit the image
                self.win.blit(self.retry_image, retry_image_rect)

            # Check if the current button is the end button
            if button["action"] == "end":
                # Calculate the position for the image
                exit_image_rect = self.end_image.get_rect()
                exit_image_rect.centery = button["rect"].centery
                exit_image_rect.right = button["rect"].right - 10

                # Blit the image
                self.win.blit(self.end_image, exit_image_rect)

            # Check for button hover
            mouse_pos = pygame.mouse.get_pos()
            if button["rect"].collidepoint(mouse_pos):

                # Set button hover effects
                button["color"] = (180, 150, 100)
                shadow_rect = pygame.Rect(
                    button["rect"].left + 5,
                    button["rect"].top + 5,
                    button["rect"].width,
                    button["rect"].height,
                )
                pygame.draw.rect(
                    self.win, (0, 0, 0, 100), shadow_rect, border_radius=20
                )

                # Apply hover animation to retry image
                if button["action"] == "retry":
                    current_time = pygame.time.get_ticks()
                    if current_time - self.retry_hover_start_time >= 240:
                        self.retry_image = pygame.transform.rotate(
                            self.retry_image, -90
                        )
                        self.retry_hover_start_time = current_time

                # Apply hover effect to end image
                if button["action"] == "end":
                    self.end_image = pygame.transform.scale(self.end_image, (50, 50))

                # Handle button press
                if pygame.mouse.get_pressed()[0]:
                    self.button_function(button["action"])
                    return

                # Draws button hover effects
                for button in buttons:
                    pygame.draw.rect(
                        self.win, button["color"], button["rect"], border_radius=20
                    )
                    text_rect = button["text"].get_rect()
                    text_rect.centery = button["rect"].centery
                    text_rect.left = button["rect"].left + 20

                    self.win.blit(button["text"], text_rect)

                    if button["action"] == "retry":
                        retry_image_rect = self.retry_image.get_rect()
                        retry_image_rect.centery = button["rect"].centery
                        retry_image_rect.right = button["rect"].right - 10

                        self.win.blit(self.retry_image, retry_image_rect)

                    if button["action"] == "end":
                        exit_image_rect = self.end_image.get_rect()
                        exit_image_rect.centery = button["rect"].centery
                        exit_image_rect.right = button["rect"].right - 10

                        # Blit the image
                        self.win.blit(self.end_image, exit_image_rect)

            # Hover effects are stopped
            else:

                # Access image from file as pygame alters image properties on animation
                button["color"] = (215, 170, 0)
                current_dir = os.path.dirname(__file__)
                image_dir = os.path.join(current_dir, "images")
                if button["action"] == "retry":
                    self.retry_image = pygame.image.load(
                        os.path.join(image_dir, "reload_2.png")
                    )
                    self.retry_image = pygame.transform.scale(
                        self.retry_image, (70, 60)
                    )
                if button["action"] == "end":
                    self.end_image = pygame.image.load(
                        os.path.join(image_dir, "exit.png")
                    )
                    self.end_image = pygame.transform.scale(self.end_image, (40, 40))

    def display_score(self):
        # Display current score
        score_text = self.font.render(f"Score: {self.score}", True, self.font_color)
        score_rect = score_text.get_rect(center=(self.win_width // 2, 20))
        self.win.blit(score_text, score_rect)

        # Display high score for mode: game
        if self.mode == "game":
            high_score_text = self.font.render(
                f"High Score: {self.high_score}", True, self.font_color
            )
            high_score_rect = high_score_text.get_rect(center=(self.win_width // 2, 50))
            self.win.blit(high_score_text, high_score_rect)

        # Display high score for mode: pvc
        if self.mode == "pvc":
            # Display AI score on the player's turn
            handle_ai = False
            stack = inspect.stack()
            for frame_info in stack:
                frame = frame_info.frame
                function_name = frame.f_code.co_name
                if function_name == "run":
                    handle_ai = True
            if handle_ai:
                ai_score_text = self.font.render(
                    f"COM Score: {self.ai_score}", True, self.font_color
                )
                ai_score_rect = ai_score_text.get_rect(center=(self.win_width // 2, 70))
                self.win.blit(ai_score_text, ai_score_rect)

                if self.high_score == 0:
                    high_score_text = self.font.render(
                        f"High Score: {self.ai_score}", True, self.font_color
                    )
                else:
                    high_score_text = self.font.render(
                        f"High Score: {self.high_score}", True, self.font_color
                    )
            else:
                high_score_text = self.font.render(
                    f"High Score: {self.high_score}", True, self.font_color
                )

            high_score_rect = high_score_text.get_rect(center=(self.win_width // 2, 45))
            self.win.blit(high_score_text, high_score_rect)

    def darken_background(self):
        # Darkens the background for pause/stop effect
        darkened = pygame.Surface(self.win.get_size())
        darkened.set_alpha(128)
        darkened.fill((0, 0, 0))
        self.win.blit(darkened, (0, 0))

    def button_function(self, action):
        # Resets properties outside the game's running environment
        self.dead_fall_time = 0
        self.retry_hover_start_time = 0
        self.dead_turn = False
        self.dead = False
        self.submitted_name = False
        self.high_score = self.db.get_highest_score(self.mode, self.difficulty)

        if self.high_score is None:
            self.high_score = 0

        # Resets bird position to beginning
        if not self.paused:
            self.bird_image = pygame.transform.rotate(self.bird_image, 90)

        # Handles on exiting the the mode
        if action == "end":

            # Handles saving training of agent
            # self.env.save_file()

            # Handles exiting mode: vis
            if self.mode == "vis" and not self.paused:
                self.show_popup()

            if self.mode == "vis" and self.paused:
                global end_decision
                end_decision = True

            # Handles exiting mode: pvc
            if self.mode == "pvc":
                handle_pop = False
                stack = inspect.stack()
                for frame_info in stack:
                    frame = frame_info.frame
                    function_name = frame.f_code.co_name
                    if function_name == "run":
                        handle_pop = True
                    if function_name == "run_agent":
                        self.ai_score = self.score
                if handle_pop:
                    self.show_popup()

            # Resets game properties on end
            self.reward = 0
            self.current_actions = []
            self.pipes = []
            self.bird_y = 200
            self.bird_velocity = 0
            self.game_active = True
            self.paused = False
            self.score = 0
            self.should_continue_running = False

            return

        # Resets game properties on retry
        elif action == "retry":
            self.reward = 0
            self.current_actions = []
            self.pipes = []
            self.bird_y = 200
            self.bird_velocity = 0
            self.game_active = True
            self.paused = False
            self.score = 0
            self.generate_pipe()
            if self.mode != "vis":
                self.countdown()

    def append_action_space(self, flap_this_frame):
        # Pop redundant/repeated value to efficiently represent the last action
        # as run time occurs in a matter of frames which is updated every 1/60 seconds
        if flap_this_frame:
            if (
                len(self.current_actions) > 2
                and self.current_actions[-3] in [0, 1]
                and self.current_actions[-1] == 0
            ):
                self.current_actions.pop()

            # Append "do_nothing" action only for after the frame when flap occurs
            self.current_actions.append(self.get_action()["do_nothing"])

    def countdown(self):
        # Creates a countdown screen
        for number in range(3, 0, -1):
            self.win.blit(self.background_image, (0, 0))
            self.darken_background()

            countdown_text = self.font.render(str(number), True, self.font_color)
            countdown_rect = countdown_text.get_rect(
                center=(self.win_width // 2, self.win_height // 2)
            )

            # Display the text for the turn
            if self.run_turn == "run":
                turn_text = "Player Turn"
            else:
                turn_text = "COM Turn"

            text_surface = self.font.render(turn_text, True, (215, 170, 0))
            text_rect = text_surface.get_rect(
                center=(self.win_width // 2, self.win_height // 6)
            )
            self.win.blit(text_surface, text_rect)

            # Display countdown and sound effects
            self.win.blit(countdown_text, countdown_rect)
            if number == 1:
                self.start_sound.play()
            else:
                self.countdown_sound.play()

            pygame.display.update()
            pygame.time.wait(1250)

    def calculate_reward(self):
        # Reward for staying alive
        self.reward += 0.05

        # Reward for passing a pipe
        try:
            top_pipe, bottom_pipe = self.pipes[0]
            if top_pipe[0] < 30:
                top_pipe, bottom_pipe = self.pipes[1]

            if 70 > top_pipe[0] > 60:
                self.reward += 5

            # Potential penalty for being too high or too low
            """
            if self.bird_y < 75 or self.bird_y > self.win_height - 75:
                self.reward -= 0.05

            if 75 < self.bird_y > 11:
                self.reward -= 0.5"""
        except:
            pass

        # Game over penalty
        if self.game_active == False:
            self.reward -= 1000

    def get_reward(self):
        # Return reward to be used for Q value
        return self.reward

    def run(self):
        # Create game environment properties for player's run
        self.run_turn = "run"
        running = True
        self.generate_pipe()
        self.paused = False
        self.countdown()
        pygame.event.clear(pygame.MOUSEBUTTONDOWN)
        pygame.event.clear(pygame.KEYDOWN)

        # Buttons for pause/end screens
        buttons = [
            {
                "rect": pygame.Rect(225, 275, 200, 50),
                "color": (215, 170, 0),
                "text": self.font.render("End", True, (0, 0, 0)),
                "text_rect": pygame.Rect(300, 310, 200, 50),
                "action": "end",
            },
            {
                "rect": pygame.Rect(225, 175, 200, 50),
                "color": (200, 200, 200),
                "text": self.font.render("Retry", True, (0, 0, 0)),
                "text_rect": pygame.Rect(295, 210, 200, 50),
                "action": "retry",
            },
        ]

        # Game loop
        while running:

            # Handles game termination
            if self.should_continue_running == False:
                self.should_continue_running = True
                running = False
                return

            # Loop to provide event handling for game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.mode == "pvc":
                        global end_decision
                        end_decision = True
                    running = False

                # Handles key presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        # Handles flap presses
                        if self.game_active and not self.paused:
                            self.flap_sound.play()
                            self.current_actions.append(self.get_action()["flap"])
                            self.bird_velocity = self.flap_force
                        elif self.paused:
                            self.paused = False

                    # Handles pause presses
                    elif event.key == pygame.K_p:
                        if self.game_active:
                            self.paused = not self.paused

            # Handles an active game
            if self.game_active and not self.paused:

                # Adds nothing action to action space
                if self.bird_velocity > 0:
                    self.append_action_space(True)

                # Apply gravity to bird's velocity
                self.bird_velocity += self.gravity
                if self.bird_velocity > 10:
                    self.bird_velocity = 10
                elif self.bird_velocity < -10:
                    self.bird_velocity = -10

                # Update bird's position based on velocity
                self.bird_y += self.bird_velocity

                # Keep bird within screen bounds
                self.bird_y = max(min(self.bird_y, self.win_height - 50), 0)

                # Scroll pipes to the left
                for i, (top_pipe, bottom_pipe) in enumerate(self.pipes):
                    top_pipe_list = list(top_pipe)
                    bottom_pipe_list = list(bottom_pipe)
                    top_pipe_list[0] -= self.pipe_speed
                    bottom_pipe_list[0] -= self.pipe_speed
                    self.pipes[i] = (tuple(top_pipe_list), tuple(bottom_pipe_list))

                # Generate new pipes when the distance is reached
                if (
                    self.pipes
                    and self.pipes[-1][0][0] < self.win_width - self.pipe_distance
                ):
                    self.generate_pipe()

                if self.pipes and 60 < self.pipes[0][0][0] < (67 - self.pipe_speed):
                    self.score += 1
                elif len(self.pipes) > 1 and 60 < self.pipes[1][0][0] < (
                    67 - self.pipe_speed
                ):
                    self.score += 1

                # Collision detection
                bird_rect = pygame.Rect(60, self.bird_y, 45, 45)
                for top_pipe, bottom_pipe in self.pipes:
                    top_pipe_rect_one = pygame.Rect(
                        top_pipe[0],
                        top_pipe[1] - 80,
                        self.pipe_width / 2,
                        63,
                    )

                    top_pipe_rect_two = pygame.Rect(
                        top_pipe[0] + 6.2,
                        top_pipe[1] - 300,
                        (self.pipe_width / 2) - 6.2,
                        self.pipe_render - 63,
                    )
                    bottom_pipe_rect_one = pygame.Rect(
                        bottom_pipe[0],
                        bottom_pipe[1] + 3,
                        self.pipe_width / 2,
                        63,
                    )
                    bottom_pipe_rect_two = pygame.Rect(
                        bottom_pipe[0] + 6.2,
                        bottom_pipe[1] + 63,
                        (self.pipe_width / 2) - 6.2,
                        self.pipe_render - 63,
                    )
                    if (
                        bird_rect.colliderect(top_pipe_rect_one)
                        or bird_rect.colliderect(top_pipe_rect_two)
                        or bird_rect.colliderect(bottom_pipe_rect_one)
                        or bird_rect.colliderect(bottom_pipe_rect_two)
                    ):
                        self.game_active = False
                if (
                    bird_rect.colliderect(top_pipe_rect_one)
                    or bird_rect.colliderect(top_pipe_rect_two)
                    or bird_rect.colliderect(bottom_pipe_rect_one)
                    or bird_rect.colliderect(bottom_pipe_rect_two)
                    or bird_rect.collidepoint(60, 490)
                ):
                    self.game_active = False

            # Render and display game environment
            # Draw the background
            self.win.blit(self.background_image, (0, 0))

            for top_pipe, bottom_pipe in self.pipes:
                # Draw the top pipe
                self.win.blit(self.top_pipe_image, (top_pipe[0], top_pipe[1] - 300))

                # Draw the bottom pipe only if it's within the screen bounds
                if top_pipe[1] + self.pipe_gap < self.win_height:
                    # Check if the top pipe is flipped vertically
                    if self.top_pipe_image.get_flags() & pygame.SRCALPHA:
                        # If flipped, draw the bottom pipe without flipping
                        self.win.blit(self.pipe_image, (bottom_pipe[0], bottom_pipe[1]))
                    else:
                        # If not flipped, draw the bottom pipe with flipping
                        self.win.blit(
                            pygame.transform.flip(self.pipe_image, False, True),
                            (bottom_pipe[0], bottom_pipe[1]),
                        )

            # Draw the bird
            self.win.blit(self.bird_image, (60, self.bird_y))

            # Handles when the game is not active
            if self.paused or (not self.game_active and self.dead):
                self.darken_background()

                # Handles for when the bird dies
                if not self.game_active and self.dead:
                    # Handles database entry for an existing entry in the database for the
                    # particular mode and difficulty
                    top_scores = self.db.get_top_scores(self.mode, self.difficulty)
                    if top_scores:
                        min_score = min(score[0] for score in top_scores)
                        if self.score > min_score or len(top_scores) < 5:
                            if not self.submitted_name:
                                username = self.username()
                                self.submitted_name = True
                                if not self.db.check_username_existence(username):
                                    self.db.insert_new_user(username)
                                user_id = self.db.get_user_id(username)
                                self.db.insert_new_game_score(
                                    user_id, self.score, self.mode, self.difficulty
                                )
                                # Handles AI entry for database
                                if self.mode == "pvc":
                                    ai_id = self.db.insert_new_ai(username)
                                    self.db.insert_new_game_score(
                                        ai_id, self.ai_score, self.mode, self.difficulty
                                    )
                        # Continues to end screen
                        self.handle_buttons(buttons)
                    # Handles for first entry in database for particular mode and difficulty
                    else:
                        if not self.submitted_name:
                            username = self.username()
                            self.submitted_name = True
                            if not self.db.check_username_existence(username):
                                self.db.insert_new_user(username)
                            user_id = self.db.get_user_id(username)
                            self.db.insert_new_game_score(
                                user_id, self.ai_score, self.mode, self.difficulty
                            )
                            # Handle AI entry for database
                            if self.mode == "pvc":
                                ai_id = self.db.insert_new_ai(username)
                                self.db.insert_new_game_score(
                                    ai_id, self.score, self.mode, self.difficulty
                                )
                        # Continues to end screen
                        self.handle_buttons(buttons)
                # If not achieved a top score then continue to end screen
                else:
                    self.handle_buttons(buttons)

            # Display score unless paused
            if not self.paused:
                self.display_score()

            # Handle screen death
            if not self.game_active and not self.dead:
                self.death_animation()
                if self.bird_y > 445:
                    self.dead = True

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def run_agent(self):
        # Create an instance of CustomEnvironment to run Q Learning model
        self.env = CustomEnvironment(self)

        # Create game properties for agent's run
        self.run_turn = "run_a"
        running = True
        self.generate_pipe()
        self.paused = False
        self.ai_score = None
        if self.mode == "vis":
            if self.death_mode == "easy":
                count = 10
            elif self.death_mode == "normal":
                count = 10
            elif self.death_mode == "hard":
                count = 10
        else:
            count = 0
        self.countdown()

        # Buttons for pause/end screens
        if self.mode == "pvc":
            buttons = [
                {
                    "rect": pygame.Rect(225, 300, 200, 40),
                    "color": (200, 200, 200),
                    "text": self.font.render("Continue", True, (0, 0, 0)),
                    "text_rect": None,  # No need to set initially
                    "action": "end",
                },
                {
                    "rect": pygame.Rect(225, 200, 200, 40),
                    "color": (200, 200, 200),
                    "text": self.font.render("Retry AI", True, (0, 0, 0)),
                    "text_rect": None,  # No need to set initially
                    "action": "retry",
                },
            ]
        else:
            buttons = [
                {
                    "rect": pygame.Rect(225, 300, 200, 40),
                    "color": (200, 200, 200),
                    "text": self.font.render("End AI", True, (0, 0, 0)),
                    "text_rect": None,  # No need to set initially
                    "action": "end",
                },
                {
                    "rect": pygame.Rect(225, 200, 200, 40),
                    "color": (200, 200, 200),
                    "text": self.font.render("Retry AI", True, (0, 0, 0)),
                    "text_rect": None,  # No need to set initially
                    "action": "retry",
                },
            ]

        for button in buttons:
            button_width, button_height = button["rect"].width, button["rect"].height
            text_width, text_height = (
                button["text"].get_width(),
                button["text"].get_height(),
            )
            text_x = button["rect"].x + (button_width - text_width) // 2
            text_y = button["rect"].y + (button_height - text_height) // 2
            button["text_rect"] = pygame.Rect(text_x, text_y, text_width, text_height)

        # Game loop
        while running:
            if self.should_continue_running == False:
                self.should_continue_running = True
                running = False
                return

            # Loop to provide event handling for game events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.mode == "pvc":
                        global end_decision
                        end_decision = True
                    # Resets game properties (as mode: vis runs the fucntion: run afterwards)
                    self.reward = 0
                    self.current_actions = []
                    self.pipes = []
                    self.bird_y = 200
                    self.bird_velocity = 0
                    self.game_active = True
                    self.paused = False
                    self.score = 0
                    running = False
                    quit()

                # Handles user's pause presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        if self.game_active:
                            self.paused = not self.paused

            # Handles active game
            if self.game_active and not self.paused:

                # Handles nothing action
                if self.bird_velocity >= 0:
                    self.append_action_space(True)

                # Get agent's action from Q Learning model
                action = self.env.step()
                flap_this_frame = action == 1

                # Apply the action if flap
                if flap_this_frame:
                    self.flap_sound.play()
                    self.current_actions.append(self.get_action()["flap"])
                    self.bird_velocity = self.flap_force

                # Applies gravity to velocity
                self.bird_velocity += self.gravity
                if self.bird_velocity > 10:
                    self.bird_velocity = 10
                elif self.bird_velocity < -10:
                    self.bird_velocity = -10

                # Applies velocity to bird
                self.bird_y += self.bird_velocity

                # Keep bird within screen bounds
                self.bird_y = max(min(self.bird_y, self.win_height - 50), 0)

                # Scroll pipes to the left
                for i, (top_pipe, bottom_pipe) in enumerate(self.pipes):
                    top_pipe_list = list(top_pipe)
                    bottom_pipe_list = list(bottom_pipe)
                    top_pipe_list[0] -= self.pipe_speed
                    bottom_pipe_list[0] -= self.pipe_speed
                    self.pipes[i] = (tuple(top_pipe_list), tuple(bottom_pipe_list))

                    # As action has rendered, make reward and make agent learn
                    self.calculate_reward()
                    self.env.update()

                # Generate new pipes when the distance is reached
                if (
                    self.pipes
                    and self.pipes[-1][0][0] < self.win_width - self.pipe_distance
                ):
                    self.generate_pipe()

                if self.pipes and 60 < self.pipes[0][0][0] < (67 - self.pipe_speed):
                    self.score += 1
                elif len(self.pipes) > 1 and 60 < self.pipes[1][0][0] < (
                    67 - self.pipe_speed
                ):
                    self.score += 1

                # Collision detection
                bird_rect = pygame.Rect(60, self.bird_y, 45, 45)
                for top_pipe, bottom_pipe in self.pipes:
                    top_pipe_rect_one = pygame.Rect(
                        top_pipe[0],
                        top_pipe[1] - 80,
                        self.pipe_width / 2,
                        63,
                    )

                    top_pipe_rect_two = pygame.Rect(
                        top_pipe[0] + 6.2,
                        top_pipe[1] - 300,
                        (self.pipe_width / 2) - 6.2,
                        self.pipe_render - 63,
                    )
                    bottom_pipe_rect_one = pygame.Rect(
                        bottom_pipe[0],
                        bottom_pipe[1] + 3,
                        self.pipe_width / 2,
                        63,
                    )
                    bottom_pipe_rect_two = pygame.Rect(
                        bottom_pipe[0] + 6.2,
                        bottom_pipe[1] + 63,
                        (self.pipe_width / 2) - 6.2,
                        self.pipe_render - 63,
                    )

                    # Handle mode: vis death conditions
                    if self.mode == "vis":
                        if self.death_mode == "easy":
                            if bird_rect.collidepoint(60, 490):
                                self.death = True
                        elif self.death_mode == "normal":
                            if (
                                bird_rect.colliderect(top_pipe_rect_one)
                                or bird_rect.colliderect(bottom_pipe_rect_one)
                                or bird_rect.colliderect(bottom_pipe_rect_two)
                                or bird_rect.colliderect(top_pipe_rect_two)
                                or bird_rect.collidepoint(60, 490)
                            ) and self.score < 1:
                                self.death = True
                        elif self.death_mode == "hard":
                            if (
                                bird_rect.colliderect(top_pipe_rect_one)
                                or bird_rect.colliderect(bottom_pipe_rect_one)
                                or bird_rect.colliderect(bottom_pipe_rect_two)
                                or bird_rect.colliderect(top_pipe_rect_two)
                                or bird_rect.collidepoint(60, 490)
                            ) and self.score > 3:
                                self.death = True

                    if (
                        bird_rect.colliderect(top_pipe_rect_one)
                        or bird_rect.colliderect(bottom_pipe_rect_one)
                        or bird_rect.colliderect(bottom_pipe_rect_two)
                        or bird_rect.colliderect(top_pipe_rect_two)
                        or bird_rect.collidepoint(60, 490)
                    ):

                        self.game_active = False

            # Render and display game environment
            self.win.blit(self.background_image, (0, 0))

            for top_pipe, bottom_pipe in self.pipes:
                # Draw the top pipe
                self.win.blit(self.top_pipe_image, (top_pipe[0], top_pipe[1] - 300))

                # Draw the bottom pipe only if it's within the screen bounds
                if top_pipe[1] + self.pipe_gap < self.win_height:
                    # Check if the top pipe is flipped vertically
                    if self.top_pipe_image.get_flags() & pygame.SRCALPHA:
                        # If flipped, draw the bottom pipe without flipping
                        self.win.blit(self.pipe_image, (bottom_pipe[0], bottom_pipe[1]))
                    else:
                        # If not flipped, draw the bottom pipe with flipping
                        self.win.blit(
                            pygame.transform.flip(self.pipe_image, False, True),
                            (bottom_pipe[0], bottom_pipe[1]),
                        )

            # Draw the bird
            self.win.blit(self.bird_image, (60, self.bird_y))

            # Handles when the game is not active
            if not self.game_active or self.paused:
                if not self.game_active and not self.dead:
                    self.death_animation()
                    if self.bird_y > 445:
                        self.dead = True

                # Handles mode: vis
                if self.mode == "vis":

                    # Handles game pause
                    if self.paused and self.game_active:
                        self.darken_background()
                        self.handle_buttons(buttons)

                    # Handles and automates end screen process for continuous gameplay
                    # When death condition occurs, the mode ends when the count is 0
                    if not self.game_active and self.dead == True:
                        action = self.env.step()
                        self.calculate_reward()
                        self.env.update()

                        self.darken_background()
                        if self.death_mode == "easy" and self.death == True:
                            if count < 10:
                                count += 1
                        elif self.death_mode == "easy" and self.death == False:
                            count -= 1

                        if self.death_mode == "normal" and self.death == True:
                            if count < 10:
                                count += 1
                        elif (
                            self.death_mode == "normal"
                            and self.death == False
                            and self.score > 0
                        ):
                            count -= 1

                        if self.death_mode == "hard" and self.death == True:
                            count = 0
                        self.death = False
                        if count > 0:
                            self.button_function("retry")
                        if count < 1:
                            count = 10
                            self.button_function("end")

                # Handles mode: game
                else:
                    # Hnadles pause
                    if self.paused and self.mode == "pvc":
                        self.darken_background()
                    # Handles end
                    else:
                        self.darken_background()
                        self.handle_buttons(buttons)

            # Display score when not paused
            if not self.paused:
                self.display_score()

            pygame.display.update()
            self.clock.tick(60)


# Ran separate to initiate flappy bird class and run functions
# May be invalid if ran separately
"""Create an instance of the FlappyBirdGame class
flappy_bird_game = FlappyBirdGame("normal", "game")

# Run the game
flappy_bird_game.run_agent()
flappy_bird_game.run()

# After the game is closed, print the state space and action space
state_space = flappy_bird_game.get_state()
action_space = flappy_bird_game.get_action_space()

print("State Space:")
print(state_space)

print("\nAction Space:")
print(action_space)
"""

if __name__ == "__main__":
    # Check if a difficulty argument is provided
    if len(sys.argv) > 1:
        difficulty = sys.argv[1]

        # Handles mode: pvc
        if "pvc" in difficulty:
            difficulty = difficulty.replace(" pvc", "")
            flappy_bird_game = FlappyBirdGame(difficulty, "pvc")

            # Loop that replays the mode until end choice selected from popup
            while not end_decision:
                flappy_bird_game.run_agent()
                if end_decision:
                    break
                flappy_bird_game.run()

        # Handles mode: vis
        elif "vis" in difficulty:
            difficulty = difficulty.replace(" vis", "")
            flappy_bird_game = FlappyBirdGame(difficulty, "vis")

            # Loop that replays the mode until the end choice selected from popup
            while not end_decision:
                flappy_bird_game.run_agent()

        # Handles mode: game
        else:
            flappy_bird_game = FlappyBirdGame(difficulty, "game")
            flappy_bird_game.run()
