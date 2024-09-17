import cv2
import math
import numpy as np

#oPENcV por padrão lê a imagem em BGR
def read_image(filename): 
    image = cv2.imread(filename)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    return image #nesse momento a imagem é uma matriz (Array)
                 #vai ter 1 canal se for escala cinza ou 3 se for colorida (RGB)   
    
def resize_image(image,width,height):
    rows, cols, channels = image.shape 
    w = int(math.ceil(cols*width/100))
    h = int(math.ceil(rows*height/100))
    new_size = (w,h)
    image = cv2.resize(image,new_size) #criei um novo tamanho w e h
    return image

#Filtro suavização de média -- linear
#calcula a média dos valores dos pixels dentro da área do kernel.
def average_filter(image,kernel_size):
    image = cv2.blur(image,(kernel_size,kernel_size))
    return image

# Média ponderada usando distrib Gaussiana. -- linear
# usa um kernel cujos valores são determinados pela função de distribuição Gaussiana.
#Ele atribui maior peso ao pixel central e pesos menores à medida que se distancia do centro, o que resulta em um efeito de suavização mais natural.
# Quão maior o desvio padrão (siigma) maior a suavização
def gaussian_filter(image,kernel_size):
    standard_deviation = 0
    image = cv2.GaussianBlur(image,(kernel_size,kernel_size),standard_deviation)
    return image

#Filtro de Mediana -- não linear
# Substitui o valor do pixel central pela mediana dos valores na vizinhança do pixel central (inclui o pixel central)
# Eficiente para remover ruídos (como sal e pimenta)
# Mantém bordas e detalhes importantes produzindo um borramento ou blur reduzido em relação aos filtros lineares (média) utilizando máscaras de tamanho similar.
def median_filter(image,kernel_size):
    image = cv2.medianBlur(image,kernel_size)
    return image

#ruídos
def salt_and_pepper_noise(image):
    #h (rows), w (cols)
    h,w, c = image.shape
    noise = np.zeros((h,w),np.uint8) #cria uma matriz (h,w) de valores zero (imagem preta)
    cv2.randu(noise,0,255) # randomiza esses valores entre 0 e 255 / 'imagem de tv'
    image[noise <= 5] = 0  # se f(x,y) <=5 cria um pixel preto
    image[noise >= 250] = 255 # se f(x,y) >=250 cria pixel branco
    return image

#Filtro de Sobel - detecção de bordas horizontais e verticais 
#Aplica a operação de convolução utilizando dois kernels, 
#Resulta em duas imagens chamadas de gradiente, uma representando as bordas horizontais e outra as bordas verticais.
#A magnitude do gradiente, calculada como a combinação das duas imagens gradiente, é frequentemente usada para identificar bordas fortes na imagem.
def sobel_filter(image):
    if len(image.shape) > 2: #imagem eh colorida
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)  
    else:
        gray_image = image
    #detectar bordas na direcao x (verticais)
    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F,1,0,ksize=3) #kernel1
    #detectar bordas na direcao y (horizontais)
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F,0,1,ksize=3) #kernel2

    #magnitude dos gradientes
    gradient_magnitude = np.sqrt(np.square(sobel_x) + np.square(sobel_y))

    #normalizar para o intervalo [0,255]
    gradient_magnitude *= 255.0 / gradient_magnitude.max()
    edge_image = np.uint8(gradient_magnitude)
    #filtro de sobel acaba aqui
    if len(image.shape) > 2: #imagem eh colorida
        edge_image = cv2.cvtColor(edge_image,cv2.COLOR_GRAY2RGB) 
    
    #image = cv2.add(image,edge_image)
    image = cv2.addWeighted(image, 0.7, edge_image, 0.3, 0) # mesclando com a imagem de entrada para realçar as bordas
 
    return image
    
# utiliza um kernel Laplaciano que realça mudanças abruptas na intensidade dos pixels
# destaca as bordas e os detalhes finos, aumentando a nitidez da imagem.
def laplacian_filter(image):
    image = median_filter(image,3)
    kernel = np.array([[0, -1, 0],
                       [-1, 4, -1],
                       [0, -1, 0]])
    laplacian = cv2.filter2D(image,-1,kernel)
    image = cv2.add(image,laplacian) # mesclando com a imagem de entrada para realçar as bordas
    return image

def highboost_filter(image,a):
    image = median_filter(image,3)
    kernel = np.array([[0, -1, 0],
                       [-1, 4+a, -1],
                       [0, -1, 0]])
    laplacian = cv2.filter2D(image,-1,kernel)
    image = cv2.add(image,laplacian)
    return image
