import logging
import os
# Define o nível de log da Tensorflow para 3 e ignora os demais níveis
logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 (INFO), 1 (WARNING), 2 (ERROR), 3 (FATAL)
import numpy as np
import tensorflow as tf
from tensorflow import keras
import time
from sklearn import preprocessing


# Obtém as imagens pré-processadas e labels
def getData(path):
    images = []
    labels = []
    if os.path.exists(path):
        for dirpath , dirnames , filenames in os.walk(path):   
            if (len(filenames)>0): # é uma pasta que contém arquivos
                folder_name = os.path.basename(dirpath)
                for index, file in enumerate(filenames):
                    label = folder_name
                    labels.append(label)
                    full_path = os.path.join(dirpath,file)
                    img = keras.preprocessing.image.load_img(full_path, target_size = (224,224))
                    img_array = keras.preprocessing.image.img_to_array(img)
                    # adiciona mais 1 dimensão em img_array
                    img_array = np.expand_dims(img_array, axis=0)
                    # Scale pixel values from [0,255] to [-1,1] interval
                    preproc_img = keras.applications.mobilenet.preprocess_input(img_array)
                    images.append(preproc_img)
        return np.vstack(images), np.array(labels)
    

def getCNNModel():
    img_shape = (224,224,3)
    base_model = keras.applications.MobileNet(input_shape=img_shape,
                                              weights='imagenet',
                                              include_top=True)
    base_model.summary()
    reshape_2_layer = base_model.get_layer('reshape_2').output
    model = keras.Model(inputs=base_model.input,outputs=reshape_2_layer)
    model.summary()
    return model

def extractCNNFeatures(images,model):
    features = model.predict(images, batch_size=32)
    return np.array(features)

def encodeLabels(labels):
    startTime = time.time()
    print(f'[INFO] Encoding labels to numerical labels')
    encoder = preprocessing.LabelEncoder() 
    encoded_labels = encoder.fit_transform(labels)
    elapsedTime = round(time.time() - startTime,2)
    print(f'[INFO] Encoding done in {elapsedTime}s')
    return np.array(encoded_labels,dtype=object), encoder.classes_

def saveData(path,labels,features,encoderClasses):
    startTime = time.time()
    print(f'[INFO] Saving data')
    #the name of the arrays will be used as filenames
    #f'{labels=}' gets both variable name and its corresponding values.
    #split('=')[0] gets the variable name from f'{labels=}'
    label_filename = f'{labels=}'.split('=')[0]+'.csv'
    feature_filename = f'{features=}'.split('=')[0]+'.csv'
    encoder_filename = f'{encoderClasses=}'.split('=')[0]+'.csv'
    np.savetxt(path+label_filename,labels, delimiter=',',fmt='%i')
    np.savetxt(path+feature_filename,features, delimiter=',') #float does not need format
    np.savetxt(path+encoder_filename,encoderClasses, delimiter=',',fmt='%s') 
    elapsedTime = round(time.time() - startTime,2)
    print(f'[INFO] Saving done in {elapsedTime}s')

def process_data(image_path, feature_path,model):
    # Obter dados das imagens e rótulos
    images, labels = getData(image_path)
    # Codificar os rótulos
    encoded_labels, encoder_classes = encodeLabels(labels)
    # Extrair características CNN
    features = extractCNNFeatures(images, model)
    # Salvar os dados
    saveData(feature_path, encoded_labels, features, encoder_classes)

def main():
    mainStartTime = time.time()
    trainImagePath = './dataset/train'
    testImagePath = './dataset/test'
    trainFeaturePath = './features_labels/cnn/train/'
    testFeaturePath = './features_labels/cnn/test/'
    model = getCNNModel()
    print(f'[INFO] ========= PROCESSANDO IMAGENS DE TREINAMENTO ========= ')
    process_data(trainImagePath,trainFeaturePath,model)
    print(f'[INFO] =========== PROCESSANDO IMAGENS DE TESTE =========== ')
    process_data(testImagePath,testFeaturePath,model)
    elapsedTime = round(time.time() - mainStartTime,2)
    print(f'[INFO] Code execution time: {elapsedTime}s')

if __name__ == "__main__":
    main()