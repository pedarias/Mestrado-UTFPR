import os
import cv2
import numpy as np
from sklearn import preprocessing
from progress.bar import Bar
from sklearn.cluster import MiniBatchKMeans
import time

def main():
    mainStartTime = time.time()
    trainImagePath = './images_split/train/'
    testImagePath = './images_split/test/'
    trainFeaturePath = './features_labels/sift/train/'
    testFeaturePath = './features_labels/sift/test/'
    print(f'[INFO] ========= TRAINING IMAGES ========= ')
    trainImages, trainLabels = getData(trainImagePath)
    trainEncodedLabels, encoderClasses = encodeLabels(trainLabels)
    trainSiftDescriptors = extractSiftDescriptors(trainImages)
    kmeans, k = trainKMeans(trainSiftDescriptors)
    trainFeatures = buildHistogram(trainSiftDescriptors,kmeans,k)
    saveData(trainFeaturePath,trainEncodedLabels,trainFeatures,encoderClasses)
    print(f'[INFO] =========== TEST IMAGES =========== ')
    testImages, testLabels = getData(testImagePath)
    testEncodedLabels, encoderClasses = encodeLabels(testLabels)
    testSiftDescriptors = extractSiftDescriptors(testImages)
    testFeatures = buildHistogram(testSiftDescriptors,kmeans,k)
    saveData(testFeaturePath,testEncodedLabels,testFeatures,encoderClasses)
    elapsedTime = round(time.time() - mainStartTime,2)
    print(f'[INFO] Code execution time: {elapsedTime}s')

def getData(path):
    images = []
    labels = []
    if os.path.exists(path):
        for dirpath , dirnames , filenames in os.walk(path):   
            if (len(filenames)>0): #it's inside a folder with files
                folder_name = os.path.basename(dirpath)
                bar = Bar(f'[INFO] Getting images and labels from {folder_name}',max=len(filenames),suffix='%(index)d/%(max)d Duration:%(elapsed)ds')            
                for index, file in enumerate(filenames):
                    label = folder_name
                    labels.append(label)
                    full_path = os.path.join(dirpath,file)
                    image = cv2.imread(full_path)
                    images.append(image)
                    bar.next()
                bar.finish()
        return images, np.array(labels,dtype=object)
    
# SIFT (Scale Invariant Feature Transform)
# permite detectar e extrair descritores ou caraterísticas locais, invariáveis a translação, rotação e escala    
# localização de pontos chaves na imagem (keypoints)
# num conjunto de imagens, cada imagem pode ter quantidades de keypoints diferentes entre si
# para cada keypoint: obtém-se um vetor de características com 128 valores numéricos, chamado de descritor
def extractSiftDescriptors(images):
    siftDescriptorsList = []
    bar = Bar('[INFO] Extrating SIFT descriptors...',max=len(images),suffix='%(index)d/%(max)d  Duration:%(elapsed)ds')
    sift = cv2.SIFT_create()
    for image in images:
        if(len(image.shape)>2): #imagem colorida
            image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        blur_image = cv2.medianBlur(image,3)
        # os descritores SIFT são vetores de tamanho 128 que 
        # descrevem pontos de interesse (keypoints) de cada imagem
        # para cada imagem, extrai-se um número de keypoints e seus respectivos descritores 
        # descriptors = uma matriz de tamanho num_keypoints x 128 valores numéricos
        keypoints, descriptors = sift.detectAndCompute(blur_image,None) # calcula quem são os keypoints e os 128 valores p cada
        siftDescriptorsList.append(descriptors)
        bar.next() 
    bar.finish()
    # como cada imagem pode ter diferentes números de keypoints, o tipo objeto
    # permite retornar um vetor de matrizes com tamanhos diferentes
    return np.array(siftDescriptorsList,dtype=object)

def trainKMeans(siftDescriptors):
    print('[INFO] Clustering the SIFT descriptors of all train images...')
    k = 100 # número de clusters do KMeans
    # n_init = número de vezes que o algoritmo KMeans será executado com diferentes 
    # centróides iniciais. 'auto' = valor será definido automaticamente
    kmeans = MiniBatchKMeans(n_clusters=k, n_init='auto', random_state=42)
    startTime = time.time()
    # o kmeans.fit requer uma matriz de tanho num_amostras x num_características
    # como o siftDescriptors é um vetor de matrizes de tamanho num_imagens x 1
    # e cada matriz dentro desse vetor é do tamanho num_keypoints x 128
    # np.vstack empilha verticalmente as matrizes resultando em uma única matriz 
    # de tamanho num_amostras x 128 (onde num_amostras = num_keypoints x num_imagens)

    # o KMeans agrupa as linhas (amostras) da matriz siftDescriptors de todas as imagens
    # com base na proximidade (similaridade) de suas características (vetores de tamanho 128)
    # assim, vetores de características similares podem estar no mesmo grupo, pois descrevem 
    # keypoints similares ao longo de todas as imagens analisadas
    kmeans.fit(np.vstack(siftDescriptors))
    elapsedTime = round(time.time() - startTime,2)
    print(f'[INFO] Clustering done in {elapsedTime}s')
    # retorna o modelo treinado kmeans e o número de clusters k
    return kmeans, k

def buildHistogram(siftDescriptors, kmeans_model, n_clusters):
    print('[INFO] Building histograms...')
    startTime = time.time()
    histogramList = []
    # o siftDescriptors é um vetor de matrizes de tamanho num_imagens x 1
    # e cada matriz dentro desse vetor é do tamanho num_keypoints x 128
    for i in range(len(siftDescriptors)):
        histogram = np.zeros(n_clusters)
        # siftDescriptors[i]: uma matriz n_keypoints x 128 
        # cada linha da matriz acima contém um vetor de características de tamanho 128
        # kmeans.predict retorna um vetor (idx_arr) de tamanho n_keypoints x 1 
        # contendo o índice do grupo em que cada vetor de características pertence
        idx_arr = kmeans_model.predict(siftDescriptors[i])
        for d in range(len(idx_arr)):
            # cada elemento do vetor histogram corresponde a um cluster e 
            # o valor do elemento indica quantos descritores SIFT da imagem corrente 
            # foram atribuídos a esse cluster. Assim, o histogram armazena a 
            # distribuição dos descritores SIFT (cada vetor de tamanho 128) da imagem corrente 
            # em relação aos clusters (grupos) gerados pelo modelo KMeans 
            histogram[idx_arr[d]] += 1 
        histogramList.append(histogram)
    elapsedTime = round(time.time() - startTime,2)
    print(f'[INFO] Histogram built in {elapsedTime}s')
    # retorna uma matriz de tamanho num_imagens x num_clusters (tamanho de cada histograma)
    # essa matriz será salva em arquivo como as features extraídas pelo método SIFT
    return np.array(histogramList,dtype=object)

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
    # os nomes dos vetores são utilizados como nomes dos arquivos
    #f'{labels=}' retorna o nome e o valor da variável labels
    #split('=')[0] retorna apenas o nome da variável retornado por f'{labels=}'
    label_filename = f'{labels=}'.split('=')[0]+'.csv'
    feature_filename = f'{features=}'.split('=')[0]+'.csv'
    encoder_filename = f'{encoderClasses=}'.split('=')[0]+'.csv'
    np.savetxt(path+label_filename,labels, delimiter=',',fmt='%i')
    np.savetxt(path+feature_filename,features, delimiter=',') # float não precisa definir formato
    np.savetxt(path+encoder_filename,encoderClasses, delimiter=',',fmt='%s') 
    elapsedTime = round(time.time() - startTime,2)
    print(f'[INFO] Saving done in {elapsedTime}s')

if __name__ == "__main__":
    main()
