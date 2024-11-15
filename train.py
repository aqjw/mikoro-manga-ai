# train.py

from model import build_model, INPUT_SHAPE, NUM_CLASSES
import math
import os
import numpy as np
from PIL import Image
import tensorflow as tf
import warnings
from IPython.display import clear_output
import matplotlib.pyplot as plt

from utils import cvtColor, resize_image, resize_label, normalize

BATCH_SIZE = 16
EPOCHS = 30
VAL_SUBSPLITS = 1


def rand(a=0, b=1):
    return np.random.rand() * (b - a) + a


class UnetDataset(tf.keras.utils.Sequence):
    def __init__(self, annotation_lines, input_shape, batch_size, num_classes, _train, dataset_path):
        self.annotation_lines = annotation_lines
        self.length = len(self.annotation_lines)
        self.input_shape = input_shape
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.train = _train
        self.dataset_path = dataset_path

    def __len__(self):
        return math.ceil(len(self.annotation_lines) / float(self.batch_size))

    def __getitem__(self, index):
        images = []
        targets = []
        for i in range(index * self.batch_size, (index + 1) * self.batch_size):
            i = i % self.length
            # print('self.annotation_lines[i]', self.annotation_lines[i].split())
            name = self.annotation_lines[i].split()[0]
            # name = self.annotation_lines[i]
            jpg_path = os.path.join(os.path.join(self.dataset_path, "JPEGImages"), name + ".jpg")
            png_path = os.path.join(os.path.join(self.dataset_path, "SegmentationClassPNG"), name + ".png")
            # print('jpg_path, png_path', jpg_path, png_path)
            jpg = Image.open(jpg_path)
            png = Image.open(png_path)

            jpg, png = self.process_data(jpg,
                                         png,
                                         self.input_shape,
                                         random=self.train)

            images.append(jpg)
            targets.append(png)

        images = np.array(images)
        targets = np.array(targets)
        return images, targets

    def process_data(self, image, label, input_shape, random=True):
        image = cvtColor(image)
        label = Image.fromarray(np.array(label))
        h, w, _ = input_shape

        # resize
        image, _, _ = resize_image(image, (w, h))
        label, _, _ = resize_label(label, (w, h))

        if random:
            # flip
            flip = rand() < .5
            if flip:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                label = label.transpose(Image.FLIP_LEFT_RIGHT)

        # np
        image = np.array(image, np.float32)
        image = normalize(image)

        label = np.array(label)
        label[label >= self.num_classes] = self.num_classes

        return image, label


def create_mask(pred_mask):
    pred_mask = tf.argmax(pred_mask, axis=-1)
    pred_mask = pred_mask[..., tf.newaxis]
    return pred_mask[0]


def display(display_list):
    plt.figure(figsize=(15, 15))

    title = ['Input Image', 'True Mask', 'Predicted Mask']

    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i + 1)
        plt.title(title[i])
        plt.imshow(tf.keras.utils.array_to_img(display_list[i]))
        plt.axis('off')
    plt.show()


class DisplayCallback(tf.keras.callbacks.Callback):
    # sample for predictions
    def __init__(self, images, masks):
        super(DisplayCallback, self).__init__()

        self.sample_image, _sample_mask = images[0], masks[0]
        self.sample_mask = _sample_mask[..., tf.newaxis]

    def on_epoch_end(self, epoch, logs=None):
        clear_output(wait=True)

        display([
            self.sample_image, self.sample_mask,
            create_mask(self.model.predict(self.sample_image[tf.newaxis, ...]))
        ])

        print('\nSample Prediction after epoch {}\n'.format(epoch + 1))


class ModelCheckpointCallback(tf.keras.callbacks.Callback):

    def __init__(self,
                 filepath,
                 monitor='val_loss',
                 verbose=0,
                 save_best_only=False,
                 save_weights_only=False,
                 mode='auto',
                 period=1):
        super(ModelCheckpointCallback, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.epochs_since_last_save = 0

        if mode not in ['auto', 'min', 'max']:
            warnings.warn(
                'ModelCheckpoint mode %s is unknown, '
                'fallback to auto mode.' % mode, RuntimeWarning)
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf
        else:
            if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
                self.monitor_op = np.greater
                self.best = -np.Inf
            else:
                self.monitor_op = np.less
                self.best = np.Inf

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.epochs_since_last_save += 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            filepath = self.filepath.format(epoch=epoch + 1, **logs)
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warnings.warn(
                        'Can save best model only with %s available, '
                        'skipping.' % self.monitor, RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print(
                                '\nEpoch %05d: %s improved from %0.5f to %0.5f,'
                                ' saving model to %s' %
                                (epoch + 1, self.monitor, self.best, current,
                                 filepath))
                        self.best = current
                        if self.save_weights_only:
                            self.model.save_weights(filepath, overwrite=True)
                        else:
                            self.model.save(filepath, overwrite=True)
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve' %
                                  (epoch + 1, self.monitor))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving model to %s' %
                          (epoch + 1, filepath))
                if self.save_weights_only:
                    self.model.save_weights(filepath, overwrite=True)
                else:
                    self.model.save(filepath, overwrite=True)


def train(dataset_path='datasets/train_voc', logs_path='logs', max_samples=None):
    dataset_txt_path = os.path.join(dataset_path, "ImageSets/Segmentation")

    # Read dataset txt files
    with open(os.path.join(dataset_txt_path, "train.txt"), "r", encoding="utf8") as f:
        train_lines = f.readlines()

    with open(os.path.join(dataset_txt_path, "val.txt"), "r", encoding="utf8") as f:
        val_lines = f.readlines()

    # Limit dataset size if max_samples is set
    if max_samples is not None:
        train_lines = train_lines[:max_samples]
        val_lines = val_lines[:max_samples]

    print(INPUT_SHAPE)
    train_batches = UnetDataset(train_lines, INPUT_SHAPE, BATCH_SIZE, NUM_CLASSES, True, dataset_path)
    val_batches = UnetDataset(val_lines, INPUT_SHAPE, BATCH_SIZE, NUM_CLASSES, False, dataset_path)

    steps_per_epoch = len(train_lines) // BATCH_SIZE
    validation_steps = len(val_lines) // BATCH_SIZE // VAL_SUBSPLITS

    print('len(train_lines)', len(train_lines))
    print('len(val_lines)', len(val_lines))
    print('len(train_batches)', len(train_batches))
    print('len(val_batches)', len(val_batches))
    print('steps_per_epoch', steps_per_epoch)
    print('validation_steps', validation_steps)

    images, masks = train_batches.__getitem__(0)
    display_callback = DisplayCallback(images, masks)

    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    checkpoint_callback = ModelCheckpointCallback(
        os.path.join(logs_path, 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.weights.h5'),
        monitor='val_loss',
        save_weights_only=True,
        save_best_only=True,
        period=1)

    images, labels = val_batches.__getitem__(0)
    assert images is not None and labels is not None, "Validation data contains None values"
    print("Validation data passed the initial check")

    model = build_model()
    model_history = model.fit(train_batches,
                              epochs=EPOCHS,
                              steps_per_epoch=steps_per_epoch,
                              validation_steps=validation_steps,
                              validation_data=val_batches,
                              callbacks=[display_callback, checkpoint_callback])

    model.save_weights(os.path.join(logs_path, 'the-last-model.weights.h5'), overwrite=True)

    # Training result
    loss = model_history.history['loss']
    val_loss = model_history.history['val_loss']

    plt.figure()
    plt.plot(model_history.epoch, loss, 'r', label='Training loss')
    plt.plot(model_history.epoch, val_loss, 'bo', label='Validation loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss Value')
    plt.ylim([0, 1])
    plt.legend()
    plt.show()


# if __name__ == '__main__':
#     # Example: set max_samples to 100 for quick testing
#     train(max_samples=100)
