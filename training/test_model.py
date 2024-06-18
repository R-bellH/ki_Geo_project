from keras.models import Model
from keras.layers import LSTM, Dense, Input, TimeDistributed, Flatten, Concatenate, Reshape, Masking

# Define image input shape
image_height = 177
image_width = 190
channels = 13
time_steps = 14

# Define image input
image_input = Input(shape=(time_steps, image_height, image_width, channels))

# Flatten images across height, width, and channels
flattened_images = TimeDistributed(Flatten())(image_input)

# Define extra input shape
extra_input_shape = (time_steps, 24, 3)

# Define extra input
extra_input = Input(shape=extra_input_shape)

# Reshape extra input to be compatible for concatenation
reshaped_extra_input = Reshape((time_steps, 24 * 3))(extra_input)

# Concatenate flattened images and reshaped extra input
concatenated_input = Concatenate(axis=-1)([flattened_images, reshaped_extra_input])

# Masking layer
masked_input = Masking(mask_value=0.0)(concatenated_input)

# LSTM layer
lstm_output = LSTM(units=50, return_sequences=True)(masked_input)

# TimeDistributed Dense layer
output = TimeDistributed(Dense(units=1, activation='sigmoid'))(lstm_output)

# Define and compile the model
model = Model(inputs=[image_input, extra_input], outputs=output)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()
