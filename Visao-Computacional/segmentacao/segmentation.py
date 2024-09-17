from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from skimage.measure import find_contours
from skimage.morphology import dilation, disk, remove_small_objects, label
from scipy import ndimage
import numpy as np
import cv2

# Segmentação por Cor 
# segmenta uma imagem com base em um intervalo de cores especificado. Usa o espaço de cores HSV (Hue, Saturation, Value), 
# que é mais eficaz para trabalhar com cores em comparação ao espaço RGB.
def color_segmentation(image,lower_range,upper_range):
    if (len(image.shape)>2): #imagem colorida
        blur_image = cv2.medianBlur(image,5) #Aplica uma suavização para reduzir o ruído.
        hsv = cv2.cvtColor(blur_image, cv2.COLOR_RGB2HSV) #Converte a imagem de RGB para HSV.
        mask = cv2.inRange(hsv,lower_range,upper_range) # Cria uma máscara binária, destacando pixels dentro do intervalo de cor especificado.
        result = cv2.bitwise_and(image,image,mask=mask) # Aplica a máscara à imagem original para extrair a região de interesse.
    return 'Máscara Obtida', mask, 'Resultado da Segmentação', result

# Limiarização Binária
# Converte uma imagem para escala de cinza e, então, aplica uma limiarização binária. 
# É útil para segmentar imagens com alto contraste entre o objeto e o fundo.
def threshold(image, t):
    if (len(image.shape)>2): #imagem colorida
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) #Converte para escala de cinza se a imagem for colorida.
    else:
        gray_image = image
    blur_image = cv2.medianBlur(gray_image,5)
    t, mask = cv2.threshold(blur_image,t,255,cv2.THRESH_BINARY_INV) #Aplica uma limiarização com um valor predefinido.
    mask = ndimage.binary_fill_holes(mask).astype(np.uint8) #Preenche buracos na máscara binária.
    result = cv2.bitwise_and(image,image,mask=mask) # Extrai os objetos usando a máscara obtida.
    return 'Máscara Obtida', mask, 'Resultado da Segmentação', result

#Limiarização de Otsu
# extensão da limiarização binária que calcula automaticamente um valor de limiar ótimo baseado no histograma da imagem.   
def otsu_threshold(image):
    if (len(image.shape)>2): #imagem colorida
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    else:
        gray_image = image
    blur_image = cv2.medianBlur(gray_image,5) #Reduz ruído com filtro de mediana.
    t, mask = cv2.threshold(blur_image,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) #Calcula automaticamente o limiar de Otsu e aplica a limiarização.
    mask = ndimage.binary_fill_holes(mask).astype(np.uint8) #Preenche buracos para formar regiões contínuas.
    result = cv2.bitwise_and(image,image,mask=mask) #Extrai a região segmentada usando a máscara gerada.
    return f'Máscara Obtida (Threshold = {t})', mask, 'Resultado da Segmentação', result

# Detecção de Bordas com Canny
# Um dos métodos mais eficientes para detecção de bordas, detectando variações significativas de intensidade.
def canny(image,lower_thresh_rate):
    if (len(image.shape)>2): #imagem colorida
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) #Converte para escala de cinza.
    else:
        gray_image = image
    blur_image = cv2.medianBlur(gray_image,5) #Suaviza a imagem.
    t, mask = cv2.threshold(blur_image,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) #Estabelece limiares superior e inferior com base no método de Otsu.
    lower = int(t*lower_thresh_rate)#limiar inferior
    upper = t #Usa Otsu para definir o limiar superior.
    edges = cv2.Canny(blur_image,lower,upper) #Aplica o algoritmo de Canny para detectar bordas.
    (contours,h) = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #Identifica contornos das bordas detectadas
    result = cv2.drawContours(image.copy(),contours,-1,color=(0,225,0),thickness=3) # desenha na imagem original.
    return f'Bordas detectadas', edges, 'Resultado da Segmentação', result 

#Segmentação Watershed
# Ideal para segmentar objetos conectados onde a distinção entre objetos adjacentes é difícil.
def watershed_segmentation(image):
    if (len(image.shape)>2): #imagem colorida
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    else:
        gray_image = image
    blur_image = cv2.medianBlur(gray_image,5)
    t, mask = cv2.threshold(blur_image,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) #Usa Otsu para definir um limiar.
    mask = ndimage.binary_fill_holes(mask).astype(np.uint8)
    # aplicar a transformação de distância
    distance = ndimage.distance_transform_edt(mask) #Calcula a transformação de distância euclidiana.
    #encontrar o pontos onde a distância de cada pixel até o fundo da imagem
    #binária é máxima em sua vizinhança local
    dist_max = peak_local_max(distance,footprint=np.ones((3,3)), labels=mask) #Identifica os picos locais na imagem de distância, representando os pontos mais distantes do fundo.
    mask2 = np.zeros(distance.shape,dtype=bool)
    mask2[tuple(dist_max.T)] = True
    markers, _ = ndimage.label(mask2) #Marca regiões conectadas na máscara.
    #labels - uma matriz onde cada pixel da imagem de entrada é rotulado
    # com valores inteiros que indicam a qual bacia ele pertence
    labels=watershed(-distance,markers,mask=mask) #Aplica o algoritmo Watershed usando as marcações como marcadores.
    #remover pequenas regiões ou bacias rotuladas pelos labels
    labels = remove_small_objects(labels,min_size=100) #Remove objetos pequenos que podem ser ruído.

    #encontrar as bordas dos objetos segmentados pelo watershed
    contours = find_contours(labels,0.5) #Encontra contornos dos objetos segmentados
    #desenhar as bordas na imagem colorida
    result = image.copy()
    border_mask = np.zeros_like(result[:,:,0],dtype=bool)
    for contour in contours:
        contour = contour.astype(int)
        border_mask[contour[:,0], contour[:,1]] = True
    border_mask = dilation(border_mask,disk(2)) #dilata para visualização clara.
    #atribuir a cor verde para a borda
    result[border_mask] = [0,255,0]

    return f'Bordas detectadas', mask, 'Resultado da Segmentação', result