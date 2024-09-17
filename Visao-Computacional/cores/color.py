import cv2
import numpy as np
import matplotlib.pyplot as plt

#por padrão a openCV lê a imagem em BGR 
def read_image(filename):
    image = cv2.imread(filename)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    return image
    
def grayscale_image(image):
    if (np.ndim(image) > 2): #imagem colorida
        image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    return image

# inverte os níveis de intensidade em uma imagem
# útil para realçar detalhes claros em imagens escuras.
def negative_image(image):
    image = 255 - image 
    return image

#aumenta pixel de baixa intensidade e diminui de alta intensidade
#pixel claro ficar escuro e escuro ficar claro, esta função tende a deixar a imagem mais clara.
def log_transform(image): 
    image = image.astype(float)
    c = 255 / np.log(1+np.max(image)) #permite manter os níveis de intensidade [0,255]
    image = c * np.log(1+image)
    image = image.astype(np.uint8)
    return image
#Esta função e a de cima são não lineares - log e exp
def gamma_correction(image,gamma):
    image = image.astype(float)          #if gamma<1 = log_transform,
    image = pow((image/255),gamma) * 255 #else o inverso i.e, escuro ficar mais escuro e claro ficar mais claro 
    image = image.astype(np.uint8)
    return image

def gray_histogram(image):
    num_bins = 256
    hist = cv2.calcHist([image],[0],None,[num_bins],[0,num_bins]) 
    #plot histogram
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    xs = np.arange(0,num_bins,1)
    ax.bar(xs,hist.flatten(),zs=0,zdir='y',color='black',ec='black',alpha=0.8)
    ax.set_xlabel('Níveis de intensidade')
    ax.set_yticks([0])
    ax.set_zlabel('Quantidade de pixels',labelpad=10)
    plt.show()       

def color_histogram(image):
    num_bins = 256
    hist_r = cv2.calcHist([image],[0],None,[num_bins],[0,num_bins])
    hist_g = cv2.calcHist([image],[1],None,[num_bins],[0,num_bins])
    hist_b = cv2.calcHist([image],[2],None,[num_bins],[0,num_bins])
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    xs = np.arange(0,num_bins,1)
    ax.bar(xs,hist_r.flatten(),zs=0,zdir='y',color='red',ec='red',alpha=0.8)
    ax.bar(xs,hist_g.flatten(),zs=10,zdir='y',color='green',ec='green',alpha=0.8)
    ax.bar(xs,hist_b.flatten(),zs=20,zdir='y',color='blue',ec='blue',alpha=0.8)
    ax.set_xlabel('Níveis de intensidade')
    ax.set_yticks([0,10,20])
    ax.set_yticklabels(['Red','Green','Blue'])
    ax.set_zlabel('Quantidade de pixels',labelpad=10)
    plt.show()

def show_histogram(image):
    if (np.ndim(image) > 2): #entao a imagem possui 3 canais (colorida)
        color_histogram(image)
    else:
        gray_histogram(image)
#Ajuste de Contraste -- expande ou comprime a distribuição do histograma 
def gray_contrast_stretch(image,max,min):
    image = ((max-min)/(np.max(image)-np.min(image)))*(image - np.min(image))+min
    #if > 1 expande, if < 1 comprime
    image = np.array(image.clip(0,255),dtype='uint8') # 'clip' força os valores a ficarrem entre [0,255]
    return image

def color_contrast_stretch(image,max,min):
    r,g,b = cv2.split(image) # divide cada canal em individual
    r = ((max-min)/(np.max(r)-np.min(r)))*(r - np.min(r))+min #mesma coisa p cada canal, como acima
    g = ((max-min)/(np.max(g)-np.min(g)))*(g - np.min(g))+min
    b = ((max-min)/(np.max(b)-np.min(b)))*(b - np.min(b))+min
    r = np.array(r.clip(0,255),dtype='uint8')
    g = np.array(g.clip(0,255),dtype='uint8')
    b = np.array(b.clip(0,255),dtype='uint8')
    image = cv2.merge([r,g,b]) #faz o merge antes de devolver p interface gráfica
    return image

# Função para aplicar o ajuste de contraste caso a imagem seja ou não colorida
def contrast_stretch(image,max,min):
    if (np.ndim(image) > 2): #entao a imagem possui 3 canais (colorida)
        image = color_contrast_stretch(image,max,min)
    else:
        image = gray_contrast_stretch(image,max,min)
    return image

# Equalização de Histograma -- deixar ele mais próximo de uma dist uniforme
def gray_histogram_equalization(image):
    image = cv2.equalizeHist(image)
    return image

def color_histogram_equalization(image):
    r,g,b = cv2.split(image)
    r = cv2.equalizeHist(r)
    g = cv2.equalizeHist(g)
    b = cv2.equalizeHist(b)
    image = cv2.merge([r,g,b])
    return image
# Se a imagem for colorida chama a função p colorida, caso contrário p 1 canal só
def histogram_equalization(image):
    if (np.ndim(image) > 2): #entao a imagem possui 3 canais (colorida)
        image = color_histogram_equalization(image)
    else:
        image = gray_histogram_equalization(image)
    return image

# Técnicas para alterar o brilho e o contraste
# O brilho é o valor de intensidade, o valor do pixel. O contraste é a distribuição dos pixels entre esses níveis de intensidade