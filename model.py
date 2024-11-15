# model.py

import os
import logging
import tensorflow as tf

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

NUM_CLASSES = 2  # Number of classes including background
INPUT_SHAPE = [224, 224, 3]  # Input shape (H, W, C)


def upsample(filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)

    # Upsampling block with Conv2DTranspose, BatchNormalization, Dropout, and ReLU
    result = tf.keras.Sequential()
    result.add(tf.keras.layers.Conv2DTranspose(
        filters,
        size,
        strides=2,
        padding='same',
        kernel_initializer=initializer,
        use_bias=False
    ))
    result.add(tf.keras.layers.BatchNormalization())

    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))

    result.add(tf.keras.layers.ReLU())
    return result


def unet_model(output_channels: int, down_stack, up_stack):
    # Define input layer
    inputs = tf.keras.layers.Input(shape=INPUT_SHAPE)

    # Downsampling through the model
    skips = down_stack(inputs)
    x = skips[-1]
    skips = reversed(skips[:-1])

    # Upsampling with skip connections
    for up, skip in zip(up_stack, skips):
        x = up(x)
        concat = tf.keras.layers.Concatenate()
        x = concat([x, skip])

    # Final layer with Conv2DTranspose
    last = tf.keras.layers.Conv2DTranspose(
        filters=output_channels,
        kernel_size=3,
        strides=2,
        padding='same'
    )
    x = last(x)

    # Final Conv2D layer to ensure correct output shape
    x = tf.keras.layers.Conv2D(
        output_channels, 1, activation='softmax', padding='same'
    )(x)

    return tf.keras.Model(inputs=inputs, outputs=x)


def build_up_stack():
    # Define upsampling stack
    return [
        upsample(256, 3),
        upsample(128, 3),
        upsample(64, 3),
        upsample(32, 3),
    ]


def build_model(model_path: str = None):
    # Define base model for feature extraction
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=INPUT_SHAPE,
        include_top=False
    )

    # Use specific layers' activations
    layer_names = [
        'block_1_expand_relu',  # 64x64
        'block_3_expand_relu',  # 32x32
        'block_6_expand_relu',  # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',  # 4x4
    ]
    base_model_outputs = [base_model.get_layer(name).output for name in layer_names]

    # Create feature extraction model
    down_stack = tf.keras.Model(inputs=base_model.input, outputs=base_model_outputs)
    down_stack.trainable = False

    # Build U-Net model
    up_stack = build_up_stack()
    model = unet_model(NUM_CLASSES, down_stack, up_stack)
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=['accuracy']
    )

    # Load model weights if path is provided
    if model_path:
        try:
            model.load_weights(model_path)
            print(f'{model_path} model loaded.')
        except Exception as e:
            print(f'Error loading model weights: {e}')

    model.summary()
    return model


# Функция для загрузки модели только один раз
_model_instance = None


def model_singleton():
    global _model_instance
    if _model_instance is None:
        logging.info("Loading model...")
        # TODO: get path from env
        _model_instance = build_model('logs/the-last-model.weights.h5')
    return _model_instance
