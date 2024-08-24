from QLearningAgent import QLearningAgent


class CustomEnvironment:

    # Create instance for Q Learning model and state/ action attributes
    def __init__(self, flappy_bird_game):
        self.flappy_bird_game = flappy_bird_game

        # Handle q-tables for mode: vis
        if self.flappy_bird_game.mode == "vis":
            if self.flappy_bird_game.death_mode == "easy":
                table = ""
            elif self.flappy_bird_game.death_mode == "normal":
                table = "q_table_vis_normal.xlsx"
            elif self.flappy_bird_game.death_mode == "hard":
                table = "q_table_vis_hard.xlsx"

        # Handle q-table for mode: pvc
        if self.flappy_bird_game.mode == "pvc":
            table = "q_table.xlsx"
        self.q_learning = QLearningAgent(self, table)

        # Attributes for env to q-learning represented
        self.state_space = None
        self.new_state_space = None
        self.calc_reward = None
        self.action_space = None

    def get_nearest_pipe(self):
        bird_x = self.state_space["bird_x"]
        pipes = self.state_space["pipes"]

        # Filter the pipes that are ahead of the bird
        pipes_ahead = [pipe for pipe in pipes if pipe[0][0] >= bird_x]

        # Return the nearest set of pipes if available
        return pipes_ahead[0] if pipes_ahead else None

    def calculate_state_space_values(self):
        nearest_pipe = self.get_nearest_pipe()
        if nearest_pipe == None:
            return 0, 0, 0

        # X: Horizontal distance to the next pipe
        X = nearest_pipe[1][0] - self.state_space["bird_x"] if nearest_pipe else 0

        # Y: Vertical distance to the next pipe
        Y = (
            (nearest_pipe[1][1] - 55) - self.state_space["bird_y"]  # 55
            if nearest_pipe
            else 0
        )

        # V: Current velocity of the bird
        V = self.state_space["bird_velocity"]

        # Y1: Initially considered state but not longer included
        """
        # Y1: Vertical distance between the next two pipes
        if nearest_pipe and len(self.state_space["pipes"]) > 1:
            next_pipe_index = self.state_space["pipes"].index(nearest_pipe)
            if next_pipe_index + 1 < len(self.state_space["pipes"]):
                next_next_pipe = self.state_space["pipes"][next_pipe_index + 1]
                Y1 = (
                    (next_next_pipe[1][1] - nearest_pipe[1][1]) if next_next_pipe else 0
                )
            else:
                Y1 = 0
        else:
            Y1 = 0
        """

        return X, Y, V  # Y1

    def update(self):
        # Call environment methods for next state space and reward
        self.state_space = self.flappy_bird_game.get_state_space()
        self.calc_reward = self.flappy_bird_game.get_reward()
        (x_dist, y_dist, v_velocity) = self.calculate_state_space_values()

        # Compile state variables into an array
        state_variables = [x_dist, y_dist, v_velocity]

        # Calculate Q value
        self.q_learning.learn_qValue(state_variables, self.calc_reward)

    def save_file(self):
        # Save Q table
        self.q_learning.export_q_table_to_excel()

    def step(self):
        # Perform action in Flappy Bird game and get the state space and action space
        self.state_space = self.flappy_bird_game.get_state_space()
        self.action_space = self.flappy_bird_game.get_action_space()

        # Calculate state variables from state space
        (
            x_dist,
            y_dist,
            v_velocity,
        ) = self.calculate_state_space_values()

        # In place of the first action taken, it is assumed to be action: nothing
        try:
            last_action = self.action_space[-1]
        except:
            last_action = 0

        game_active = self.state_space["game_active"]

        # Compile state variables into an array
        state_variables = [x_dist, y_dist, v_velocity]

        # Send the state variables and last action to Q Learning model to determine action
        next_action = self.q_learning.learn_action(
            state_variables, last_action, game_active
        )

        return next_action
