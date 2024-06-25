from datetime import datetime, timedelta
import tensorflow as tf
import pandas as pd
from keras.models import Model
from keras.layers import LSTM, Dense, Input, TimeDistributed, Flatten, Concatenate, Reshape, Masking
import os
from data_to_tensor import location2sentence
from tensorflow.keras.utils import Sequence
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, recall_score, precision_score, \
    mean_squared_error
import warnings

# 忽略 SettingWithCopyWarning 警告
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# Define image input shape
image_height = 190
image_width = 190
channels = 13
time_steps = 9
hours = 24
w_features = 14

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
lstm_output = LSTM(units=50, return_sequences=False)(masked_input)

# TimeDistributed Dense layer
output = Dense(units=1, activation='sigmoid')(lstm_output)

# Define and compile the model
model = Model(inputs=[image_input, extra_input], outputs=output)
model.compile(loss=tf.keras.losses.BinaryCrossentropy(), optimizer='adam', metrics=['accuracy'])

model.summary()


def make_all_dates(directory_path):
    import os
    import pandas as pd
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

    fire_weather = pd.DataFrame(rows, columns=["latitude", "longitude", "date"]).astype(str)
    return fire_weather


class FireDataGenerator(Sequence):
    def __init__(self, data_frame, batch_size=2, shuffle=True):
        self.data_frame = data_frame.drop(columns=["label"])  # 完整的标签数据框
        self.labels = data_frame["label"]
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(len(self.data_frame))
        if self.shuffle:
            np.random.shuffle(self.indices)

    def __len__(self):
        return int(np.ceil(len(self.data_frame) / self.batch_size))

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

    def __getitem__(self, index):
        batch_indices = self.indices[index * self.batch_size:(index + 1) * self.batch_size]
        batch = self.data_frame.iloc[batch_indices]
        X, y = self.__data_generation(batch)
        return X, y

    def __data_generation(self, batch):
        pic_list = []
        weather_list = []
        labels_list = []

        for i, fire in batch.iterrows():
            sentence = location2sentence(self.data_frame, fire)
            label = self.labels.loc[i]
            pic_list.append(sentence[0])
            weather_list.append(sentence[1])
            labels_list.append(label)

        # 转换为适合模型输入的张量格式
        pic_list = tf.convert_to_tensor(pic_list, dtype=tf.float32)
        weather_list = tf.convert_to_tensor(weather_list, dtype=tf.float32)
        labels_list = tf.convert_to_tensor(labels_list, dtype=tf.float32)
        labels_list = tf.expand_dims(labels_list, axis=-1)  # 确保标签的维度正确

        return [pic_list, weather_list], labels_list


def data_preprocess():
    # positive data
    fire_path = os.path.abspath(os.getcwd()) + r"\data_mining\fire_labels\fire_labels_final.csv"
    fires = pd.read_csv(fire_path)
    fires['latitude'] = fires['latitude'].astype(str)
    fires['longitude'] = fires['longitude'].astype(str)
    fires['date'] = fires['date'].astype(str)
    fire_pictures = make_all_dates(os.path.abspath(os.getcwd()) + r"\data_mining\sentinel_images")
    fires = fires[['latitude', 'longitude', 'date']]
    fires = pd.merge(fire_pictures, fires, on=['latitude', 'longitude', 'date'], how='inner')
    fires = fires.drop_duplicates()
    fires['label'] = 1
    # negative data
    no_fire_path = os.path.abspath(os.getcwd()) + r"\data_mining\no_fire_probably.csv"
    no_fires = pd.read_csv(no_fire_path)
    no_fires['latitude'] = no_fires['latitude'].astype(str)
    no_fires['longitude'] = no_fires['longitude'].astype(str)
    no_fires['date'] = no_fires['date'].astype(str)
    no_fire_pictures = make_all_dates(os.path.abspath(os.getcwd()) + r"\data_mining\sentinel_images_no_fire")
    no_fires = pd.merge(no_fire_pictures, no_fires, on=['latitude', 'longitude', 'date'], how='inner')
    no_fires = no_fires.drop_duplicates()
    no_fires['label'] = 0

    data = pd.concat([fires, no_fires], ignore_index=True)
    data = data.sample(frac=1)
    return data


def run():
    fires = data_preprocess()
    # 初始化数据生成器
    # Split data into training and validation sets
    train_df, test_df = train_test_split(fires, test_size=0.3, random_state=13)
    # Initialize data generators
    train_generator = FireDataGenerator(train_df, batch_size=32, shuffle=True)
    test_generator = FireDataGenerator(test_df, batch_size=32, shuffle=False)

    ##  model load here

    # path = os.path.abspath(os.getcwd()) + r"\model.h5"
    # model = tf.keras.models.load_model(path)

    #  model train here
    model.fit(x=train_generator, epochs=10, verbose=1)  # validation_data=test_generator
    print("train done.")
    model.save('model.h5')
    print("save done.")

    all_true_classes = []
    all_predicted_classes = []

    # 假设使用 model.predict 进行预测
    for data_lists, labels_list in test_generator:
        predictions = model.predict(data_lists)

        # 对每个预测结果使用阈值 0.5 进行二元分类

        # 将当前批次的真实类别添加到列表中
        all_true_classes.append(labels_list)

        # 将当前批次的预测类别添加到列表中
        all_predicted_classes.append(predictions)

    # 合并所有批次的真实类别和预测类别
    all_true_classes = np.concatenate(all_true_classes, axis=0)
    all_predicted_classes = np.concatenate(all_predicted_classes, axis=0)

    # 打印最终的形状，确保一致性
    all_true_classes = all_true_classes.reshape(all_true_classes.shape[0])
    all_predicted_classes = all_predicted_classes.reshape(all_predicted_classes.shape[0])

    print("all_true_classes shape:", all_true_classes)
    print("all_predicted_classes shape:", all_predicted_classes)

    threshold = 0.5
    all_predicted_classes = (all_predicted_classes >= threshold).astype(int)

    accuracy = accuracy_score(all_true_classes, all_predicted_classes)
    print("accuracy_score:")
    print(accuracy)

    recall = recall_score(all_true_classes, all_predicted_classes)
    print("recall_score:")
    print(recall)

    precision = precision_score(all_true_classes, all_predicted_classes)
    print("precision_score:")
    print(precision)

    f1 = f1_score(all_true_classes, all_predicted_classes)
    print("f1_score:")
    print(f1)

    cm = confusion_matrix(all_true_classes, all_predicted_classes)
    print("confusion_matrix:")
    print(cm)


if __name__ == "__main__":
    # breakpoint()
    run()
# fires['date'] = fires['date'].astype(str)
