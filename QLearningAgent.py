import numpy as np
import random
import pandas as pd
import os
import ast


class QLearningAgent:
    def __init__(self, environment, table):
        # learning rate, discount factor and epsilon defined
        self.gamma = 0.97  # 0.99 ~ 0.9
        if table == "q_table.xlsx":
            self.epsilon = 0.0001  # 0.01 ~ 0.0001
            self.alpha = 0.25  # 0.4 ~ 0.15
        else:
            self.epsilon = 0.01
            self.alpha = 0.35  # 0.4 ~ 0.15

        # Q table/array (x,y,v,action) and instances defined
        self.q_table_dimensions = (10, 40, 21, 2)
        self.q_table = self.import_q_table_from_excel(table)
        self.environment = environment

        self.current_state = None
        self.action = None

    def discretize_state(self, state):
        # Convert continuous states into discrete bins
        x_bin = min(int(state[0] // 61), 9)
        y_bin = min(int((state[1] + 285) // 16), 39)
        v_bin = min(int(state[2] + 10), 20)
        return x_bin, y_bin, v_bin

    def choose_action(self, discrete_state, action):
        # Q value based on the state given to collect all actions: flap and nothing
        q_values = self.q_table[discrete_state]

        # Choose action based on epsilon
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random action
            return np.random.choice([0, 1])
        else:
            # Exploitation: choose the action with the highest Q-value
            best_action = np.argmax(q_values)
            return best_action

    def learn_action(self, states, action, game_active):
        # Agent choose action from discrete states
        discrete_states = self.discretize_state(states)
        next_action = self.choose_action(discrete_states, action)

        # Set the agent's action decided as the action
        self.action = next_action

        # Set the current state and return the action
        self.current_state = discrete_states
        return self.action

    def learn_qValue(self, new_states, reward):
        # Discretize the next state based on the action taken
        new_discrete_state = self.discretize_state(new_states)

        # Get the maximum Q-value for the next state
        max_future_q = np.max(self.q_table[new_discrete_state])

        # Get the Q value from the current current state and action
        current_q = self.q_table[self.current_state + (self.action,)]

        # Calculate the new Q value
        new_q = (1 - self.alpha) * current_q + self.alpha * (
            reward + self.gamma * max_future_q
        )

        # Update the Q table/array with new Q value
        self.q_table[self.current_state + (self.action,)] = new_q

    def export_q_table_to_excel(self, file_name="q_table.xlsx"):
        # Initialize an empty array to store the data
        data = []

        # Iterate over each state to populate the array
        for x in range(0, self.q_table_dimensions[0]):
            for y in range(0, self.q_table_dimensions[1]):
                for v in range(0, self.q_table_dimensions[2]):
                    # Retrieve Q-values for both actions at this state
                    state = (
                        x,
                        y,
                        v,
                    )
                    q_value_0 = self.q_table[state + (0,)]
                    q_value_1 = self.q_table[state + (1,)]
                    data.append([state, q_value_0, q_value_1])

        # Create a DataFrame from the data array
        df = pd.DataFrame(data, columns=["State", "Action 0", "Action 1"])

        # Save to Excel
        script_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_directory, file_name)
        df.to_excel(file_path, index=False)

    def import_q_table_from_excel(self, table):
        # Determine Q table to use based on the value given
        if table != "":
            script_directory = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(script_directory, table)
            if os.path.isfile(file_path):
                df = pd.read_excel(file_path)
                q_table = np.zeros(self.q_table_dimensions)

                # Convert the "State" column from string to tuple using ast.literal_eval
                df["State"] = df["State"].apply(ast.literal_eval)

                self.explored_states_count = 0
                # Iterate over rows and fill the Q table/array
                for _, row in df.iterrows():
                    state = row["State"]
                    action_0 = float(row["Action 0"])
                    action_1 = float(row["Action 1"])

                    q_table[state + (0,)] = action_0
                    q_table[state + (1,)] = action_1
                return q_table

        # Return empty Q table/array if no value passed
        else:
            return np.zeros(self.q_table_dimensions)
