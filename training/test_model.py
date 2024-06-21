from datetime import datetime, timedelta
import tensorflow as tf
import pandas as pd
from keras.models import Model
from keras.layers import LSTM, Dense, Input, TimeDistributed, Flatten, Concatenate, Reshape, Masking
import os
from data_to_tensor import location2sentence

# Define image input shape
image_height = 190
image_width = 190
channels = 13
time_steps = 9
hours=24
w_features=14

# Define image input
image_input = Input(shape=(time_steps, image_height, image_width, channels))

# Flatten images across height, width, and channels
flattened_images = TimeDistributed(Flatten())(image_input)

# Define extra input shape
extra_input_shape = (time_steps, hours, w_features)

# Define extra input
extra_input = Input(shape=extra_input_shape)

# Reshape extra input to be compatible for concatenation
reshaped_extra_input = Reshape((time_steps, hours * w_features))(extra_input)

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
model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True), optimizer='adam', metrics=['accuracy'])

def data(fire_data):
    data=[]
    for index, row in fire_data.iterrows():
        sentence=location2sentence(make_all_dates(),row)
        data.append(sentence)
def make_all_dates():
    import os
    import pandas as pd
    # Specify the directory path
    directory_path = path = os.path.abspath(os.getcwd()) +r"\ki_Geo_project\data_mining\sentinel_images"  # Replace with your directory path
    # Get a list of all entries (files and subdirectories) in the specified directory
    entries = os.listdir(directory_path)
    # Iterate over each entry
    rows = []
    for entry in entries:
        lat, long = entry.split(",")
        # Create the full path to the entry
        full_path = os.path.join(directory_path, entry)

        # Check if the entry is a directory
        if os.path.isdir(full_path):

            # List all files and subfolders within the subfolder
            dates = os.listdir(full_path)
            for date in dates:
                rows.append([lat, long, date.split(".")[0]])

    fire_weather = pd.DataFrame(rows, columns=["latitude", "longitude", "date"])
    return fire_weather

def run():
    path = os.path.abspath(os.getcwd()) + r"\ki_Geo_project\data_mining\fire_labels\fire_labels_final.csv"
    fires = pd.read_csv(path)
    fires['latitude']=fires['latitude'].astype(str)
    fires['longitude']=fires['longitude'].astype(str)
    fires['date']=fires['date'].astype(str)
    pictures = make_all_dates()
    fires = fires[['latitude', 'longitude', 'date']]
    labels = pd.merge(pictures, fires, on=['latitude', 'longitude', 'date'], how='inner')
    fires=labels.drop_duplicates()
    print(len(fires))
    weather_list, pic_list=[],[]
    labels_list=[]
    for _, fire in fires.iterrows():
        print(fire)
        sentence, labels = location2sentence(fires, fire) # sentence shape [(17, 9, 190, 190, 13), (17, 9, 24, 14)] labels shape (17, 9)
        pic_list.append(sentence[0])
        weather_list.append(sentence[1])
        labels_list.append(labels)
    print("search done.")
    pic_list= tf.convert_to_tensor(pic_list, dtype='float32')
    weather_list= tf.convert_to_tensor(weather_list, dtype='float32')
    labels_list=tf.convert_to_tensor(labels_list, dtype='float32')
    labels_list=tf.expand_dims(labels_list,axis=-1)
    # labels_list=tf.convert_to_tensor(labels_list)
    print("transfer done.")
    model.summary()

    print(pic_list.shape)
    print(weather_list.shape)
    print(labels_list.shape)
    model.fit(x=[pic_list,weather_list], y=labels_list, batch_size=2, epochs=10, validation_split=0.2,verbose=1)
    print("train done.")
    loss, accuracy = model.evaluate(x=[pic_list,weather_list], y=labels_list)
    print(f'Validation Loss: {loss:.4f}, Validation Accuracy: {accuracy:.4f}')
    model.save('model.h5')
    print("save done.")

if __name__=="__main__":
    #breakpoint()
    run()
# fires['date'] = fires['date'].astype(str)

# breakpoint()

