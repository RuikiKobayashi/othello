import keras
from keras.layers import Activation, Conv2D, Flatten, Dense, BatchNormalization, add
from keras import backend as K
import tensorflow as tf

BOARD_SIZE = 8
NUM_FILTERS = 128
CHANNELS = 3
BLOCKS = 16
BATCH_SIZE = 64

class Model:
    def __init__(self, epochs = 32, rate = 1e-4,make_predict=True):
        self.epochs = epochs
        self.rate = rate
        self.build(make_predict)
        self.compile()


    def res_block(self, input, out_deep):
        x = Conv2D(int(out_deep / 4), 1, strides=1, padding='same')(input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(int(out_deep / 4), 3, strides=1, padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(out_deep, 1, strides=1, padding='same')(x)
        x = BatchNormalization()(x)

        return add([x, input])

    def build(self, make_predict):
        inputs = keras.Input(shape=(3, BOARD_SIZE, BOARD_SIZE))
        x = Conv2D(NUM_FILTERS, 3, strides=1, padding='same')(inputs)

        for i in range(BLOCKS):
            x = self.res_block(x, NUM_FILTERS)

        x_p = Conv2D(2, 1, strides=1, padding='valid')(x)
        x_p = Activation('relu')(x_p)
        x_p = BatchNormalization()(x_p)
        x_p = Flatten()(x_p)
        policy = Dense(64, activation='softmax', name='policy')(x_p)

        x_v = Conv2D(1, 1, strides=1, padding='valid')(x)
        x_v = Activation('relu')(x_v)
        x_v = BatchNormalization()(x_v)
        x_v = Flatten()(x_v)
        x_v = Dense(256)(x_v)
        value = Dense(1, activation='tanh', name='value')(x_v)

        self.model = keras.Model(inputs=inputs, outputs=[policy, value])
        if make_predict:
            self.model.make_predict_function()

    def compile(self):
        self.model.compile(loss={'policy': 'sparse_categorical_crossentropy', 'value': 'mean_squared_error'},
                           loss_weights={'policy': 0.3, 'value': 0.7},
                           optimizer=keras.optimizers.Adam(lr=self.rate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0, amsgrad=False),
                           metrics=['accuracy'])

    def fit(self, dataS,dataP,dataV):
        # state = dataS.reshape([-1, 3, 8, 8])
        self.model.fit(dataS, [dataP, dataV],
                       validation_split=0.05,
                       epochs=self.epochs,
                       batch_size=BATCH_SIZE,
                       verbose=2)

    def predict(self, x):
        x = x.reshape([-1, 3, BOARD_SIZE, BOARD_SIZE])
        result = self.model.predict(x, batch_size=1, verbose=0)
        return result[0].reshape(-1), result[1][0][0]


    def getPolicy(self, x):
        x = x.reshape([-1, 3, BOARD_SIZE, BOARD_SIZE])
        y = self.model.predict(x, batch_size=1, verbose=0)
        return y[0].reshape(-1)

    def getValu(self, x):
        x = x.reshape([-1, 3, BOARD_SIZE, BOARD_SIZE])
        y = self.model.predict(x, batch_size=1, verbose=0)
        return y[1][0][0]

    def save(self, path):
        self.model.save_weights(path)

    def load(self, path):
        self.model.load_weights(path)

    # def inShape(self, black, white, judge):
    #     x = np.array(list(reversed((("0" * 64) + bin(black)[2:])[-64:])), dtype=np.int8)
    #     white = np.array(list(reversed((("0" * 64) + bin(white)[2:])[-64:])), dtype=np.int8)
    #     judge = np.array(list(reversed((("0" * 64) + bin(judge)[2:])[-64:])), dtype=np.int8)
    #     return 
