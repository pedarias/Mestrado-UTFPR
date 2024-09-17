import logging
import os
# Define o nível de log da Tensorflow para 3 e ignora os demais níveis
logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 (INFO), 1 (WARNING), 2 (ERROR), 3 (FATAL)
import numpy as np
from tensorflow import keras
from sklearn.metrics import classification_report,confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns # pip install seaborn
from tkinter import filedialog


initialdir = os.path.dirname(os.path.abspath(__file__))
filename = filedialog.askopenfilename(filetypes=[("Model files", "*.keras")],initialdir=initialdir)
if filename:
    # Carrega o modelo salvo em arquivo no formato .keras
    model = keras.models.load_model(filename)

# Define o caminho para a pasta contendo as imagens de teste
test_data_dir = './dataset/test'
# Define o caminho para salvar os resultados
result_path = './results/cnn/'
# Define o nome do resultado utilizando o nome do modelo carregado
result_name = os.path.splitext(os.path.basename(filename))[0]

# Define o tamanho das imagens de entrada
img_width, img_height = 224, 224

# Cria um gerador de imagens de teste
test_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# Carrega e redimensiona as imagens de teste usando o gerador de imagens
test_generator = test_datagen.flow_from_directory(
    test_data_dir,
    target_size=(img_width, img_height),
    batch_size=1,
    class_mode='categorical',
    shuffle=False)

# Realiza as previsões usando o modelo
predictions = model.predict(test_generator)

# Obtém os rótulos reais das imagens de teste
true_labels = test_generator.classes

# Obtém os rótulos previstos pelo modelo
predicted_labels = np.argmax(predictions, axis=1)

# Calcula a matriz de confusão
conf_matrix = confusion_matrix(true_labels, predicted_labels)

# Calcula a acurácia do modelo em percentual
accuracy = accuracy_score(true_labels, predicted_labels)*100

# Gera a figura da matriz de confusão usando o pacote seaborn
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g')


# Obtém os nomes das classes a partir dos nomes das subpastas da pasta teste
class_names = sorted(os.listdir(test_data_dir))
# OU
# Obtém os nomes das classes a partir do gerador de imagens de teste
class_names = list(test_generator.class_indices.keys())

# Adiciona os nomes das classes, rótulos, título, subtítulo 
# e salva a figura da matriz de confusão
plt.xticks(np.arange(len(class_names))+0.5, class_names, rotation=0, ha='right')
plt.yticks(np.arange(len(class_names))+0.5, class_names, rotation=0, va='center')
plt.xlabel('Rótulos Previstos')
plt.ylabel('Rótulos Reais')
plt.title('Matriz de Confusão',fontsize=18,weight='bold',x=0.5,y=1.05)
plt.suptitle(f'Acurácia do Modelo: {accuracy:.2f}%', fontsize=14,x=0.435,y=0.92)
plt.savefig(result_path+'Matriz_Confusao_'+result_name, dpi=300)
plt.clf()

# Obtém um relatório de classificação da scikit-learn como um dicionário
report_dict = classification_report(true_labels, predicted_labels, 
                                    target_names=class_names, output_dict=True)

# Função para criar e salvar um gráfico para a métrica escolhida
def plot_and_save_metric(metric_name):
    # cria um dicionário para a métrica de interesse (precision, recall ou f1-score)
    metric_data = {
        # chave-valor = nome da classe : valor  da métrica
        class_name: metrics[metric_name] 
        for class_name, metrics in report_dict.items() 
        # apenas as classes da lista class_names 
        # serão incluídas no dicionário metric_data.
        if class_name in class_names
    }
    sns.barplot(x=list(metric_data.keys()), y=list(metric_data.values()))
    plt.xlabel('Classes')
    plt.ylabel(metric_name.capitalize())
    plt.title(f'{metric_name.capitalize()} por Classe')
    plt.xticks(rotation=0)
    # Adiciona rótulos de texto para os valores máximos em cada barra
    for index, value in enumerate(metric_data.values()):
        plt.text(index, value, str(round(value, 2)), ha='center', va='bottom')
    # Salva a figura        
    plt.savefig(result_path+metric_name+'_'+result_name, dpi=300)
    # Limpa a figura
    plt.clf()

# Precisão
plot_and_save_metric('precision')

# Recall
plot_and_save_metric('recall')

# F1-score
plot_and_save_metric('f1-score')

print(f'[INFO] Programa encerrado!')
print(f'[INFO] Resultados salvos na pasta: {result_path}')


