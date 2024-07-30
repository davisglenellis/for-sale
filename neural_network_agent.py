import tensorflow as tf
import numpy as np

class NeuralNetworkAgent:
    def __init__(self, buying_state_size, buying_action_size, 
                 selling_state_size, selling_action_size, learning_rate=0.001):
        self.buying_state_size = buying_state_size
        self.buying_action_size = buying_action_size
        self.selling_state_size = selling_state_size
        self.selling_action_size = selling_action_size
        self.learning_rate = learning_rate
        self.buying_model = self.build_model(buying_state_size, buying_action_size)
        self.selling_model = self.build_model(selling_state_size, selling_action_size)

    def build_model(self, state_size, action_size):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(state_size,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(action_size, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), 
                      loss='mse')
        return model

    def get_action(self, state, is_buying_phase, epsilon=0):
        if np.random.rand() <= epsilon:
            return np.random.randint(self.buying_action_size if is_buying_phase else self.selling_action_size)
        
        state = np.reshape(state, [1, -1])
        if is_buying_phase:
            q_values = self.buying_model.predict(state)
        else:
            q_values = self.selling_model.predict(state)
        return np.argmax(q_values[0])

    def train(self, state, action, reward, next_state, done, is_buying_phase):
        target = reward
        if not done:
            next_state = np.reshape(next_state, [1, -1])
            if is_buying_phase:
                target = (reward + 0.95 * np.amax(self.buying_model.predict(next_state)[0]))
            else:
                target = (reward + 0.95 * np.amax(self.selling_model.predict(next_state)[0]))
        
        state = np.reshape(state, [1, -1])
        if is_buying_phase:
            target_f = self.buying_model.predict(state)
            target_f[0][action] = target
            self.buying_model.fit(state, target_f, epochs=1, verbose=0)
        else:
            target_f = self.selling_model.predict(state)
            target_f[0][action] = target
            self.selling_model.fit(state, target_f, epochs=1, verbose=0)

    def save_models(self, buying_filepath, selling_filepath):
        self.buying_model.save(buying_filepath)
        self.selling_model.save(selling_filepath)

    def load_models(self, buying_filepath, selling_filepath):
        self.buying_model = tf.keras.models.load_model(buying_filepath)
        self.selling_model = tf.keras.models.load_model(selling_filepath)


buying_state_size = 10  # Example: adjust based on your buying phase state representation
buying_action_size = 15  # Example: adjust based on your buying phase bidding rules
selling_state_size = 8  # Example: adjust based on your selling phase state representation
selling_action_size = 30  # Example: adjust based on your selling phase options

agent = NeuralNetworkAgent(buying_state_size, buying_action_size, 
                           selling_state_size, selling_action_size)