import logging
import os
# Define o nível de log da Tensorflow para 3 e ignora os demais níveis
logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 (INFO), 1 (WARNING), 2 (ERROR), 3 (FATAL)
import tensorflow as tf
from tensorflow import keras
from datetime import datetime
import matplotlib.pyplot as plt
import time
import keyboard #pip install keyboard

def getTrainDataGenerator(train_data_dir,img_shape,batch_size):
    # Cria um gerador de imagens de treinamento
    train_datagen = keras.preprocessing.image.ImageDataGenerator(
        vertical_flip = True,
        horizontal_flip = True,
        rescale=1./255) 
    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size = img_shape[:2], 
        batch_size = batch_size,
        class_mode = 'categorical', 
        subset='training',
        shuffle=True,
        seed=42) 
    return train_generator

def getValidDataGenerator(valid_data_dir,img_shape,batch_size):
    # Cria um gerador de imagens de validação
    valid_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    valid_generator = valid_datagen.flow_from_directory(
        valid_data_dir, 
        target_size = img_shape[:2], 
        batch_size=batch_size,
        class_mode= 'categorical',
        shuffle=True)
    return valid_generator

def getTestDataGenerator(test_data_dir,img_shape):
    # Cria um gerador de imagens de teste
    test_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_data_dir, 
        target_size = img_shape[:2], 
        batch_size=1, # a previsão é realizada em  1 imagem por vez
        class_mode= 'categorical')
    return test_generator

def getModel(img_shape,num_classes):
    img_shape = (224,224,3)
    # Carrega o modelo de CNN da Keras sem a camada de saída (include_top = False)
    base_model = keras.applications.MobileNet(input_shape = img_shape,
                                              weights = 'imagenet',
                                              include_top=False)
    # Define que o modelo base pode ser retreinado
    base_model.trainable = True
    # Define o formato de entrada da CNN
    inputs = keras.Input(shape=img_shape)
    # x recebe o modelo base da Keras sem a camada de saída
    # apenas para extração de características
    x = base_model(inputs)
    # adiciona-se ao modelo atual uma camada de normalização em lote
    # para acelerar a convergência e melhorar a estabilidade do modelo
    x = keras.layers.BatchNormalization()(x)
    # adiciona-se ao modelo atual uma camada para reduzir a dimensionalidade dos dados
    # preservando informações importantes e descartando informações menos relevantes
    x = keras.layers.GlobalAveragePooling2D()(x)
    # adiciona-se uma camada dropout para desativar uma fração de neurônios para reduzir overfitting
    x = keras.layers.Dropout(0.2, seed=42)(x)
    # adiciona-se uma camada densa para classificação, com parâmetros que também
    # permitem evitar overfitting e com a função de ativação relu
    x = keras.layers.Dense(64,
                           kernel_regularizer=keras.regularizers.L1L2(l1=0.0001, l2=0.0001),
                           bias_regularizer=keras.regularizers.L2(0.001),
                           activity_regularizer=keras.regularizers.L2(0.0001),
                           activation='relu')(x)
    # adiciona-se uma camada dropout para desativar uma fração de neurônios para reduzir overfitting
    x = keras.layers.Dropout(0.5, seed=42)(x)
    # adiciona-se uma camada densa para classificação com um total de neurônios igual
    # ao número de classes dos daos e com a função de ativação softmax utilizada em problemas multiclasses
    outputs = keras.layers.Dense(num_classes,activation='softmax')(x)
    # define o modelo final utilizando as camadas adicionadas anteriormente
    model = keras.Model(inputs,outputs)
    # exibe um resumo das camadas do modelo no console ou terminal
    model.summary()
    return model

def compileModel(model,metric):
    # define o otimizar para o cálculo de ajuste dos parâmetros/pesos do modelo
    optimizer = keras.optimizers.Adam()
    # define a função para o cálculo do loss (erro entre o valor previsto e o esperado) 
    loss=keras.losses.CategoricalCrossentropy()
    # o modelo é configurado com essas informações e está pronto para ser treinado
    model.compile(optimizer=optimizer,loss=loss, metrics=[metric])
    return model

def get_checkpoint_callback(checkpoint_filepath):
    # Criação do callback para pontos de verificação
    checkpoint_callback = keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_filepath,
        save_weights_only=True,
        monitor='val_accuracy',
        mode='max',
        save_best_only=True)
    return checkpoint_callback

def get_log_callback(log_filepath):
    # Criação do callback para log dos valores de acurácia e loss a cada época
    log_callback = keras.callbacks.CSVLogger(log_filepath, separator=',', append=False)
    return log_callback


def get_reduce_lr_callback():
    # Reduz a tx de aprend se a mudança for menor do q o factor em val_los
    reduce_lr_callback = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=1, #quantidade de épocas que espera para reduzir a tx de aprend
        verbose=1
    )
    return reduce_lr_callback

def get_early_stop_callback():
    # Para o treinamento se val_loss parar de diminuir por 3 épocas consecutivas
    early_stop = keras.callbacks.EarlyStopping(monitor = 'val_loss',
                                                    mode = 'auto',
                                                    patience = 3,
                                                    verbose = 1,
                                                    restore_best_weights = True)
    return early_stop


# códigos de escape ANSI para alterar cor de fonte fundo 
# ao imprimir msgs no terminal
class ConsoleColor:
    # fundo verde
    GREEN_BG = '\033[42m'
    # cor branca para a fonte
    WHITE = '\033[97m'
    # redefine a formatação de volta ao padrão.
    END = '\033[0m'

# Subclasse da classe Callback do Keras
class StopTrainingCallback(tf.keras.callbacks.Callback):
    # Função para ser chamada quando uma tecla for pressionada
    def on_key_pressed(self, event):
        if event.name == 'esc':
            self.model.stop_training = True
            print(f'{ConsoleColor.GREEN_BG}{ConsoleColor.WHITE}'
                  f'Treinamento interrompido pelo usuário. Por favor, aguarde...'
                  f'{ConsoleColor.END}')
            # Remove o listener de teclas pressionadas
            keyboard.unhook_all()

    # sobrescrita do método da classe Callback executado no começo de cada época
    def on_epoch_begin(self, epoch, logs=None):
        print(f'{ConsoleColor.GREEN_BG}{ConsoleColor.WHITE}'
              f'Pressione a tecla "ESC" caso queira parar o treinamento agora.'
              f'{ConsoleColor.END}')

def get_user_stop_training_callback():
    # Callback personalizado para parar o treinamento
    user_stop = StopTrainingCallback()
    return user_stop

def train_model(model,train_generator,valid_generator,checkpoint_filepath,callback_list):
    EPOCHS = 10
    # realiza o treinamento do modelo utilizando os dados de treinamento para o aprendizado
    # e os dados de validação para auxiliar no cálculos dos pesos do modelo a cada época
    # e executa as funções presentes na lista de callbacks
    history = model.fit(train_generator, epochs = EPOCHS, verbose=1, validation_data = 
            valid_generator, callbacks=callback_list)
    # Os melhores pesos armazenados nos checkpoints são carregados no modelo
    model.load_weights(checkpoint_filepath)
    return model, history

def evaluate_model(model,test_generator):
    # após o fim do treinamento, avalia a acurácia do modelo em cima dos dados de teste
    test_loss, test_acc = model.evaluate(test_generator, verbose=2)
    print(f'\nTest Accuracy:{test_acc*100}%')

def plot_history(history,metric):
    # plota a evolução da acurácia e loss ao longo das épocas de treinamento
    plt.figure(1)
    # accuracy
    plt.subplot(211)
    plt.plot(history.history[metric])
    plt.plot(history.history['val_'+metric])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='lower right')
    # loss
    plt.subplot(212)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='upper right')
    plt.tight_layout()
    plt.show()

def getCurrentFileNameAndDateTime():
    fileName =  os.path.basename(__file__).split('.')[0] 
    dateTime = datetime.now().strftime('-%d%m%Y-%H%M')
    return fileName+dateTime

def save_model(model,saved_model_path):
    model_filename = getCurrentFileNameAndDateTime()+'.keras'
    model_path = os.path.join(saved_model_path, model_filename)
    model.save(model_path)
    print(f'[INFO] O modelo treinado foi salvo na pasta {saved_model_path}')

def main():
    mainStartTime = time.time()
    train_data_dir = './dataset/train'
    valid_data_dir = './dataset/val'
    test_data_dir = './dataset/test'
    log_filepath = './csv/logger.csv'
    checkpoint_filepath = './checkpoint/cp.weights.h5'
    saved_model_path = './saved_models/'
    metric = 'accuracy'
    img_shape = (224,224,3)
    batch_size = 32
    num_classes = 4
    train_generator = getTrainDataGenerator(train_data_dir,img_shape,batch_size)
    valid_generator = getValidDataGenerator(valid_data_dir,img_shape,batch_size)
    test_generator = getTestDataGenerator(test_data_dir,img_shape)
    check = get_checkpoint_callback(checkpoint_filepath)
    log = get_log_callback(log_filepath)
    early_stop = get_early_stop_callback()
    user_stop = get_user_stop_training_callback()
    reduce_lr = get_reduce_lr_callback()
    callback_list = [check, log, early_stop, reduce_lr, user_stop]
    # Listener para teclas pressionadas
    keyboard.on_press(user_stop.on_key_pressed)
    model = getModel(img_shape,num_classes)
    compiled_model = compileModel(model,metric)
    trained_model, history = train_model(compiled_model,train_generator,valid_generator,
                                         checkpoint_filepath,callback_list)
    save_model(trained_model,saved_model_path)
    evaluate_model(trained_model,test_generator)
    plot_history(history,metric)
    elapsedTime = round(time.time() - mainStartTime,2)
    print(f'[INFO] Code execution time: {elapsedTime}s')


if __name__ == "__main__":
    main()