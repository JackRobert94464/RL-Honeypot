import numpy as np
import keras

@keras.saving.register_keras_serializable()
def ddqn_loss_fn(y_true, y_pred, actionsAppend):
    s1, s2 = y_true.shape
    countact = len(actionsAppend)
    num_actions = len(actionsAppend[0])
    indices = np.zeros(shape=(s1 * num_actions, 2))
    indices[:, 0] = np.repeat(np.arange(s1), num_actions)
    indices[:, 1] = np.tile(np.arange(num_actions), s1)
    loss = keras.losses.mean_squared_error(keras.backend.gather(y_true, indices=indices.astype(int)),
                                           keras.backend.gather(y_pred, indices=indices.astype(int)))
    return loss
