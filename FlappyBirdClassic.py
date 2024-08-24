import pygame
import random
import os


class FlappyBirdGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up paths for images
        current_dir = os.path.dirname(__file__)
        image_dir = os.path.join(current_dir, "images")

        # Load images
        self.background_image = pygame.image.load(
            os.path.join(image_dir, "background.png")
        )
        self.pipe_image = pygame.image.load(os.path.join(image_dir, "pipe.png"))
        self.bird_image = pygame.image.load(os.path.join(image_dir, "bird.png"))

        # Rescale images
        self.background_image = pygame.transform.scale(
            self.background_image, (650, 500)
        )
        self.bird_image = pygame.transform.scale(self.bird_image, (60, 60))
        self.pipe_image = pygame.transform.scale(self.pipe_image, (50, 300))

        # Flip the pipe image vertically
        self.top_pipe_image = pygame.transform.flip(self.pipe_image, False, True)

        # Bird variables
        self.bird_y = 200
        self.bird_velocity = 0
        self.gravity = 0.22
        self.flap_force = -5.4  # This will be the force applied when the bird flaps

        # Pipes variables
        self.pipe_gap = 210
        self.pipe_width = 50
        self.pipe_distance = 190  # The distance at which new pipes will generate
        self.pipes = []

        # Game state variables
        self.game_active = True
        self.paused = False

        # Score variables
        self.score = -2  # Start at -2 to handle the initial increments
        self.score_displayed = 0  # Displayed score (starts at 0)

        self.current_actions = []

        # Pygame window setup
        self.win_width, self.win_height = 650, 500
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.font_color = (255, 255, 255)

    def get_state(self):
        """
        Get the current state of the game.

        Returns:
            dict: Dictionary containing the current state variables.
        """
        return {
            "bird_y": self.bird_y,
            "bird_velocity": self.bird_velocity,
            "pipes": self.pipes,
            "game_active": self.game_active,
            "paused": self.paused,
            "score": self.score,
        }

    def get_state_space(self):
        """
        Get the state space information.

        Returns:
            dict: Dictionary containing information about the state space.
        """
        # You might need to adjust this based on your specific needs
        return {
            "bird_y": {"min": 0, "max": self.win_height - 50},
            "bird_velocity": {"min": float("-inf"), "max": float("inf")},
            "pipes": {
                "min": 0,
                "max": float("inf"),
            },  # Adjust based on your specific representation of pipes
            "game_active": {"values": [True, False]},
            "paused": {"values": [True, False]},
            "score": {"min": float("-inf"), "max": float("inf")},
        }

    def get_action(self):
        """
        Get the action space information.

        Returns:
            dict: Dictionary containing information about the action space.
        """
        return {
            "flap": 1,  # You can use any integer to represent the action
            "do_nothing": 0,  # You can use any integer to represent the action
        }

    def get_action_space(self):
        """
        Get the action space information.

        Returns:
            list: List containing the current actions (1 for flap, 0 for do nothing).
        """
        return self.current_actions

    def generate_pipe(self):
        min_pipe_distance = 85
        top_pipe_height = random.randint(
            min_pipe_distance, self.win_height - min_pipe_distance - self.pipe_gap
        )
        top_pipe_pos = (self.win_width, top_pipe_height)
        bottom_pipe_pos = (self.win_width, top_pipe_height + self.pipe_gap)
        self.pipes.append((top_pipe_pos, bottom_pipe_pos))
        if len(self.pipes) > 4:
            self.pipes.pop(0)

    def handle_buttons(self, buttons):
        pygame.draw.rect(self.win, (0, 0, 0), (175, 150, 300, 300))
        for button in buttons:
            pygame.draw.rect(self.win, button["color"], button["rect"])
            self.win.blit(button["text"], button["text_rect"])

            # Check for button click
            mouse_pos = pygame.mouse.get_pos()
            if button["rect"].collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    self.button_function(button["action"])

    def display_score(self):
        score_text = self.font.render(
            f"Score: {self.score_displayed}", True, self.font_color
        )
        score_rect = score_text.get_rect(center=(self.win_width // 2, 50))
        self.win.blit(score_text, score_rect)

    def darken_background(self):
        darkened = pygame.Surface(self.win.get_size())
        darkened.set_alpha(128)
        darkened.fill((0, 0, 0))
        self.win.blit(darkened, (0, 0))

    def button_function(self, action):
        if action == "end":
            state_space = self.get_state()
            action_space = self.get_action_space()

            print("State Space:")
            print(state_space)

            print("\nAction Space:")
            print(action_space)
            pygame.quit()
            quit()
        elif action == "retry":
            self.current_actions = []
            self.pipes = []
            self.bird_y = 200
            self.bird_velocity = 0
            self.game_active = True
            self.paused = False
            self.score = -2  # Reset score to -2
            self.score_displayed = 0  # Reset displayed score to 0
            self.generate_pipe()

    def append_action_space(self, flap_this_frame):
        if flap_this_frame:
            # Check if the conditions for popping the last item are met
            if (
                len(self.current_actions) > 1
                and self.current_actions[-2] in [0, 1]
                and self.current_actions[-1] == 0
            ):
                self.current_actions.pop()

            # Append "flap" action only for the frame when flap occurs
            self.current_actions.append(self.get_action()["do_nothing"])

    def run(self):
        running = True
        prev_bird_y = self.bird_y  # Initialize the previous bird y position
        self.generate_pipe()  # Generate initial pipe
        self.paused = False
        buttons = [
            {
                "rect": pygame.Rect(225, 300, 200, 50),
                "color": (200, 200, 200),
                "text": self.font.render("End", True, (0, 0, 0)),
                "text_rect": pygame.Rect(300, 310, 200, 50),
                "action": "end",
            },
            {
                "rect": pygame.Rect(225, 200, 200, 50),
                "color": (200, 200, 200),
                "text": self.font.render("Retry", True, (0, 0, 0)),
                "text_rect": pygame.Rect(295, 210, 200, 50),
                "action": "retry",
            },
        ]

        while running:
            flap_this_frame = (
                True  # Flag to track if the flap key is pressed in the current frame
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if self.game_active and not self.paused:
                            # Get the current action based on bird's movement
                            self.current_actions.append(self.get_action()["flap"])
                            flap_this_frame = False
                            self.bird_velocity = self.flap_force
                        elif self.paused:
                            self.paused = False
                        elif not self.game_active:
                            self.handle_buttons(buttons)
                    elif event.key == pygame.K_p:
                        if self.game_active:
                            self.paused = not self.paused

            if self.game_active and not self.paused:
                self.append_action_space(flap_this_frame)
                self.bird_velocity += self.gravity  # Apply gravity to bird's velocity
                self.bird_y += (
                    self.bird_velocity
                )  # Update bird's position based on velocity

                # Keep bird within screen bounds
                self.bird_y = max(min(self.bird_y, self.win_height - 50), 0)

                # Scroll pipes to the left
                for i, (top_pipe, bottom_pipe) in enumerate(self.pipes):
                    top_pipe_list = list(top_pipe)
                    bottom_pipe_list = list(bottom_pipe)
                    top_pipe_list[0] -= 3
                    bottom_pipe_list[0] -= 3
                    self.pipes[i] = (tuple(top_pipe_list), tuple(bottom_pipe_list))

                # Generate new pipes when the distance is reached
                if (
                    self.pipes
                    and self.pipes[-1][0][0] < self.win_width - self.pipe_distance
                ):
                    self.generate_pipe()
                    self.score += 1  # Increment score when new pipes are generated
                    if (
                        self.score_displayed < self.score
                    ):  # Displayed score catches up to the real score
                        self.score_displayed += 1

                # Collision detection for pipes
                bird_rect = pygame.Rect(60, self.bird_y, 37, 37)  # Bird's bounding box
                for top_pipe, bottom_pipe in self.pipes:
                    top_pipe_rect = pygame.Rect(
                        top_pipe[0], 0, self.pipe_width - 8, top_pipe[1] + 74
                    )  # Bounding box for top pipe
                    bottom_pipe_rect = pygame.Rect(
                        bottom_pipe[0],
                        bottom_pipe[1],
                        self.pipe_width - 8,
                        self.pipe_gap,
                    )  # Bounding box for bottom pipe
                    if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(
                        bottom_pipe_rect
                    ):
                        self.game_active = False  # Set game state to inactive when collision is detected

                # Update previous bird y position
                prev_bird_y = self.bird_y

            # Render and display game environment
            self.win.blit(self.background_image, (0, 0))  # Draw the background

            if not self.game_active or self.paused:
                self.darken_background()

                # Display buttons
                self.handle_buttons(buttons)

            for top_pipe, bottom_pipe in self.pipes:
                # Draw the top pipe
                self.win.blit(
                    self.top_pipe_image, (top_pipe[0], top_pipe[1] - self.pipe_gap)
                )

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

            self.win.blit(self.bird_image, (50, self.bird_y))  # Draw the bird

            if not self.game_active or self.paused:
                # Display buttons
                self.handle_buttons(buttons)

            if not self.paused:
                # Display the score
                self.display_score()

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


# Create an instance of the FlappyBirdGame class
flappy_bird_game = FlappyBirdGame()

# Run the game
flappy_bird_game.run()

# After the game is closed, print the state space and action space
state_space = flappy_bird_game.get_state()
action_space = flappy_bird_game.get_action_space()

print("State Space:")
print(state_space)

print("\nAction Space:")
print(action_space)
