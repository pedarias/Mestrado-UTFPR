import tkinter as tk
from tkinter import filedialog
import tkinter.font
from tkinter import TclError
from PIL import Image, ImageTk
import numpy as np
from matplotlib import pyplot as plt
import colorsys
import os
import filtering
import color
import segmentation

class Window(tk.Tk):
  
    def __init__(self):
        super().__init__()    
        self.current_image = None 
        self.tkimage = None
        self.history = [] 
        self.history_index = -1
        self.last_clicked_menu = None
        self.menus = None
        self.create_main_window()
        self.create_menubar()  
        self.create_control_frame()
        self.create_image_canvas()       
        self.disable_menus() 

    # Volta a aplicacao para o estado inicial ao abrir uma nova imagem
    def reset_state(self):
        self.current_image = None
        self.tkimage = None
        self.history = []
        self.history_index = -1
        self.clear_control_frame()

    # Cria a janela principal
    def create_main_window(self):
        self.title('Filtragem de Imagem')
        self.width= self.winfo_screenwidth()               
        self.height= self.winfo_screenheight()            
        self.geometry("%dx%d" % (self.width*.8, self.height*.8))
        try:
            # Tenta maximizar usando o método state disponível em alguns sistemas operacionais
            self.state('zoomed')
        except TclError:
            # Caso o 'zoomed' não seja suportado, define a geometria da janela para o tamanho da tela
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
    
    # Cria o frame onde serao posicionados controles como botao, spinner, slide, etc
    def create_control_frame(self):
        self.controls = tk.Frame(self)
        self.controls.pack(side=tk.TOP,expand=True,pady=(0,10))

     # Limpa o frame de controle
    def clear_control_frame(self):
        for widget in self.controls.winfo_children():
            widget.destroy()

    # Cria a barra de menu
    def create_menubar(self): 
        # Cria a barra de menu
        self.menu_bar = tk.Menu(self, tearoff="off")
        self.config(menu=self.menu_bar)
        # Define da estrutura da barra de menu utilizando um dicionario aninhado
        self.menus = {
            'Arquivo': {
                'Abrir...': self.load_image,
                'Sair': self.quit
            },
            'Editar': {
                'Desfazer':self.undo,
                'Refazer': self.redo
            },
            'Imagem': {
                'Redimensionar': self.create_resize_image_controls,
                'Escala de cinza': self.create_color_controls(color.grayscale_image)
            },
            'Filtros': {
                'Suavização': {
                    'Média': self.create_filter_controls(filtering.average_filter),
                    'Gaussiano': self.create_filter_controls(filtering.gaussian_filter),
                    'Mediana': self.create_filter_controls(filtering.median_filter)
                },
                'Aguçamento': {
                    'Sobel': self.create_filter_controls(filtering.sobel_filter),
                    'Laplaciano': self.create_filter_controls(filtering.laplacian_filter),
                    'High-boost': self.create_filter_controls(filtering.highboost_filter)
                },
                'Ruído': {
                    'Sal e Pimenta': self.create_filter_controls(filtering.salt_and_pepper_noise)
                }
            },
            'Cores': {
                'Negativo': self.create_color_controls(color.negative_image),
                'Brilho e Contraste': {
                    'Transformação Logarítmica':self.create_color_controls(color.log_transform),
                    'Correção Gamma':self.create_gamma_correction_controls,
                    'Ajuste de Contraste':self.create_contrast_stretch_controls,
                    'Equalização de Histograma':self.create_color_controls(color.histogram_equalization),
                },
                'Histograma': self.create_histogram_controls
            },
            'Segmentação': {
                'Cor': self.create_color_seg_controls(segmentation.color_segmentation),
                'Limiarização': self.create_threshold_controls(segmentation.threshold),
                'Limiarização Otsu': self.create_otsu_threshold_controls(segmentation.otsu_threshold),
                'Detecção de bordas (Canny)': self.create_canny_controls(segmentation.canny),
                'Watershed': self.create_watershed_controls(segmentation.watershed_segmentation)
            }
        } 
        # Itera sobre o dicionário aninhado para criar cada item de menu
        for menu_name, menu_items in self.menus.items():
            menu = tk.Menu(self.menu_bar, tearoff="off")
            self.menu_bar.add_cascade(label=menu_name, menu=menu)
            for item_name, command in menu_items.items():
                # Se command for um outro dicionario, cria-se um submenu
                if isinstance(command, dict):
                    submenu = tk.Menu(menu, tearoff="off")
                    menu.add_cascade(label=item_name, menu=submenu)
                    for subitem_name, subcommand in command.items():
                        submenu.add_command(label=subitem_name, command=self.wrap_command(subcommand))
                # Senao, cria um item de menu
                else:
                    menu.add_command(label=item_name, command=self.wrap_command(command))

    def wrap_command(self, command):
        if callable(command):
            return lambda: self.execute_command(command)
        else:
            return lambda: self.execute_command(None)

    def execute_command(self, command):
        if command:
            self.last_clicked_menu = self.get_menu_name(command)
            #print(f"Menu: {self.last_clicked_menu}")  # Imprime o nome do menu associado ao comando
            if (self.last_clicked_menu == 'Cor'):
                tkinter.messagebox.showinfo(title='', message='Clique em um pixel da imagem para escolher uma cor!')
            command()  # Executa a função associada ao comando

    def get_menu_name(self, command):
        for menu_name, menu_items in self.menus.items():
            if command in menu_items.values():
                return self.find_menu_name(command, menu_items)
        return None  # Retorna None se o comando não for encontrado em nenhum menu

    def find_menu_name(self, command, menu_items):
        for item_name, item_command in menu_items.items():
            if item_command == command:
                return item_name
            elif isinstance(item_command, dict):
                submenu_name = self.find_menu_name(command, item_command)
                if submenu_name:
                    return submenu_name
        return None

    def disable_submenu(self,menu_index,submenu_index):
        menu_bar = self.menu_bar.winfo_children()
        menu_bar[menu_index].entryconfig(submenu_index, state='disabled')

    def enable_submenu(self,menu_index,submenu_index):
        menu_bar = self.menu_bar.winfo_children()
        menu_bar[menu_index].entryconfig(submenu_index, state='active')

    def undo(self):
        if self.history_index > 0:            
            self.history_index -= 1
            self.display_image()
            
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.display_image()

    def update_history(self,image):
        self.history_index += 1
        # se o indice atual igual ao tamanho da lista, insere uma copia da imagem no final
        if self.history_index == len(self.history):
            self.history.append(image.copy())
        # senão, altera a imagem existente na posição atual da lista
        else: 
            self.history[self.history_index] = image.copy()
  
    def create_button(self, text, command):
        button = tk.Button(self.controls, text=text, command=command, width=20)
        button.pack(side=tk.TOP, pady=5)
        return button

    # Desabilita todos os menus, exceto o menu 'Arquivo' ('Abrir...')
    def disable_menus(self):
        for index in range(self.menu_bar.index(tk.END)+1):
            menu_entry = self.menu_bar.entrycget(index, "label")
            if menu_entry != "Arquivo":
                self.menu_bar.entryconfig(index, state='disabled')
            else:
                self.menu_bar.entryconfig(index, state='active')
    
    # Habilita todos os menus
    def enable_menus(self):
        for index in range(self.menu_bar.index(tk.END)+1):
            self.menu_bar.entryconfig(index, state='active')

    # Cria o canvas para exibição da imagem
    def create_image_canvas(self):
        image_frame = tk.Frame(self)
        image_frame.pack()
        yscrollbar = tk.Scrollbar(image_frame, orient = tk.VERTICAL)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        xscrollbar = tk.Scrollbar(image_frame, orient = tk.HORIZONTAL)
        xscrollbar.pack(side = tk.BOTTOM, fill = tk.X)
        self.current_image_canvas = tk.Canvas(image_frame, 
                                      width = self.width*.8, 
                                      height = self.height*.75,
                                      xscrollcommand = xscrollbar.set, 
                                      yscrollcommand = yscrollbar.set)
        self.current_image_canvas.bind("<Button-1>", self.get_color)
        self.current_image_canvas.pack()
        yscrollbar.config(command = self.current_image_canvas.yview)
        xscrollbar.config(command = self.current_image_canvas.xview)

    # Carrega a imagem para exibicao no canvas
    def load_image(self):
        self.reset_state()
        filename = filedialog.askopenfilename(initialdir=os.getcwd())
        if filename:
            img = filtering.read_image(filename=filename)
            if (img is not None):
                self.update_history(img.copy())
                self.display_image()
                self.enable_menus()
    
    # Exibe a imagem no canvas
    def display_image(self):
        # verifica se os submenus Desfazer e Refazer devem estar desabilitados ou nao
        if self.history_index == 0: 
            self.disable_submenu(1,0)
        else:
            self.enable_submenu(1,0)
        if self.history_index == len(self.history)-1:
            self.disable_submenu(1,1)
        else:
            self.enable_submenu(1,1)
        # recupera a imagem corrente do historico para exibir no canvas
        self.current_image = self.history[self.history_index].copy()
        img = Image.fromarray(self.current_image)
        self.tkimage = ImageTk.PhotoImage(img)
        width,height = img.size
        self.current_image_canvas.config(scrollregion=(0,0,width,height))
        self.current_image_canvas.create_image(0,0,anchor="nw",image=self.tkimage)

    # Exibe os valores dos pixels
    def display_pixel_values(self):
        self.clear_control_frame()
        filtering.show_pixel_values(self.current_image)

    # Cria os controles para redimensionar a imagem
    def create_resize_image_controls(self):
        self.clear_control_frame()
        width_label = tk.Label(self.controls,text='Largura: ', height=4)
        width_label.pack(side=tk.LEFT)
        font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
        var = tk.IntVar()
        var.set(50) # percentual padrao para redimensionamento
        self.width_spin = tk.Spinbox(self.controls, from_=1, to=200, textvariable=var, increment=1, font=font, width=4)
        self.width_spin.pack(side=tk.LEFT)
        perc_label1 = tk.Label(self.controls,text=' %', height=4)
        perc_label1.pack(side=tk.LEFT)
        heigth_label = tk.Label(self.controls,text='Altura: ', height=4)
        heigth_label.pack(side=tk.LEFT)
        self.height_spin = tk.Spinbox(self.controls, from_=1, to=200, textvariable=var, increment=1, font=font, width=4)
        self.height_spin.pack(side=tk.LEFT)
        perc_label2 = tk.Label(self.controls,text=' %', height=4)
        perc_label2.pack(side=tk.LEFT)
        self.create_button('Aplicar', self.apply_resize_image)

    # Aplica o redimensionamento da imagem
    def apply_resize_image(self):
        width = int(self.width_spin.get())
        height = int(self.height_spin.get())
        self.current_image = filtering.resize_image(self.current_image,width,height)
        self.update_history(self.current_image)
        self.display_image()    

    # Cria os controles para os filtros
    def create_filter_controls(self, filter_function):
        def create_controls():
            self.clear_control_frame()
            font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
            
            if filter_function in [filtering.average_filter, filtering.gaussian_filter, filtering.median_filter]:
                var = tk.IntVar()
                var.set(3) 
                kernel_label = tk.Label(self.controls, text='Tamanho do kernel: ', height=4)
                kernel_label.pack(side=tk.LEFT)
                self.kernel_spin = tk.Spinbox(self.controls, from_=3, to=31, textvariable=var, increment=2, font=font, width=2)
                self.kernel_spin.pack(side=tk.LEFT)
                slider = tk.Scale(self.controls, from_=3, to=31, variable=var, tickinterval=2, resolution=2, length=300, orient="horizontal")
                slider.pack(side=tk.LEFT)
            elif filter_function == filtering.highboost_filter:
                font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
                var = tk.DoubleVar()
                var.set(1) 
                factor_label = tk.Label(self.controls,text='Fator de amplificação: ', height=4)
                factor_label.pack(side=tk.LEFT)
                self.boost_spin = tk.Spinbox(self.controls, from_=1, to=3, textvariable=var, increment=0.1, font=font, width=3)
                self.boost_spin.pack(side=tk.LEFT)
                slider = tk.Scale(self.controls, from_=1, to=3, variable=var, tickinterval=1, resolution=0.1, length=300, orient="horizontal")
                slider.pack(side=tk.LEFT) 
            self.create_button('Aplicar', apply_filter)
        
        # Aplica o filtro de acordo com o parametro filter_function
        def apply_filter():
            if filter_function in [filtering.average_filter, filtering.gaussian_filter, filtering.median_filter]:
                kernel_size = int(self.kernel_spin.get())
                self.current_image = filter_function(self.current_image, kernel_size)
                self.update_history(self.current_image)
            elif filter_function == filtering.highboost_filter:
                boost = float(self.boost_spin.get())
                self.current_image = filter_function(self.current_image, boost)
                self.update_history(self.current_image)
            else: #Sobel, Laplaciano, Salt and Pepper
                self.current_image = filter_function(self.current_image)
                self.update_history(self.current_image)
            self.display_image()

        return create_controls

    def create_color_controls(self,transform_function):
        def create_controls():
            self.clear_control_frame()
            self.create_button('Aplicar', apply_image_transform) 

        def apply_image_transform():
            self.current_image = transform_function(self.current_image)
            self.update_history(self.current_image)
            self.display_image()
        
        return create_controls
    
    def create_gamma_correction_controls(self):
        self.clear_control_frame()
        font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
        const_var = tk.DoubleVar()
        const_var.set(1) #default value
        gamma_label = tk.Label(self.controls,text='Gamma: ', height=4)
        gamma_label.pack(side=tk.LEFT)
        self.gamma_spin = tk.Spinbox(self.controls, from_=0.1, to=3, textvariable=const_var, increment=0.1, font=font, width=3)
        self.gamma_spin.pack(side=tk.LEFT)
        slider = tk.Scale(self.controls,from_=0.1, to=3, variable=const_var,tickinterval=1, resolution=0.1,length= 300, orient="horizontal")
        slider.pack(side=tk.LEFT)
        self.create_button('Aplicar', self.apply_gamma_correction) 

    def create_contrast_stretch_controls(self):
        self.clear_control_frame()
        font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
        const1_var = tk.IntVar()
        const1_var.set(255) #default value
        max_label = tk.Label(self.controls,text='Maior nível de intensidade: ', height=4)
        max_label.pack(side=tk.LEFT)
        self.max_spin = tk.Spinbox(self.controls, from_=128, to=255, textvariable=const1_var, increment=1, font=font, width=3)
        self.max_spin.pack(side=tk.LEFT)
        slider1 = tk.Scale(self.controls,from_=128, to=255, variable=const1_var,tickinterval=10, resolution=1,length= 300, orient="horizontal")
        slider1.pack(side=tk.LEFT)
        const2_var = tk.IntVar()
        const2_var.set(0) #default value
        min_label = tk.Label(self.controls,text='Menor nível de intensidade: ', height=4)
        min_label.pack(side=tk.LEFT)
        self.min_spin = tk.Spinbox(self.controls, from_=0, to=127, textvariable=const2_var, increment=1, font=font, width=3)
        self.min_spin.pack(side=tk.LEFT)
        slider2 = tk.Scale(self.controls,from_=0, to=127, variable=const2_var,tickinterval=10, resolution=1,length= 300, orient="horizontal")
        slider2.pack(side=tk.LEFT)
        self.create_button('Aplicar', self.apply_contrast_stretch)

    def create_histogram_controls(self):
        self.clear_control_frame()
        color.show_histogram(self.current_image)

    def apply_gamma_correction(self):
        gamma = float(self.gamma_spin.get())
        self.current_image = color.gamma_correction(self.current_image,gamma)
        self.update_history(self.current_image)
        self.display_image() 

    def apply_contrast_stretch(self):
        max = int(self.max_spin.get())
        min = int(self.min_spin.get())
        self.current_image = color.contrast_stretch(self.current_image,max,min)
        self.update_history(self.current_image)
        self.display_image() 

    def get_color(self, event):
        if(self.last_clicked_menu == 'Cor'):
            if (len(self.current_image.shape) > 2): #imagem colorida
                x,y = event.x,event.y
                #print(f'clicked at: {x,y}')
                h,w = self.current_image.shape[:2]
                #print(w,h)
                if(x < w and y < h):
                    img = Image.fromarray(self.current_image)
                    self.rgb_color = img.getpixel((x,y))
                    self.update_segmentation_controls(True)
            else: 
                self.update_segmentation_controls(False)

    def convert_rgb2hsv_values(self,r,g,b):
        #in colorsys the coordinates are all between 0 and 1.
        r,g,b = r/255,g/255,b/255
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        #OpenCV uses HSV ranges between (0-179, 0-255, 0-255)
        h,s,v = int(h*179),int(s*255),int(v*255)
        #print(h,s,v)
        return h,s,v

    def update_segmentation_controls(self,color):
        if (color):
            r,g,b = self.rgb_color[0],self.rgb_color[1],self.rgb_color[2]
            h,s,v = self.convert_rgb2hsv_values(r,g,b)
            h_lower = max(0, min(h-10, 179)) #clamp the result of the subtraction between 0 and 179
            h_upper = max(0, min(h+10, 179)) #clamp the result of the sum between 0 and 179
            try: #if the variables below exists
                self.low_h.set(h_lower)
                self.high_h.set(h_upper)
            except AttributeError: #otherwise do nothing
                None
        else: 
            tkinter.messagebox.showinfo(title='', message='A imagem deve ser colorida para obter a cor!')

    def create_color_seg_controls(self,segmentation_function):
        def create_controls():
            self.clear_control_frame()
            font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
            low_label = tk.Label(self.controls,text='Menor nível de: H ', height=4)
            low_label.pack(side=tk.LEFT)
            self.low_h = tk.IntVar()
            self.low_s = tk.IntVar()
            self.low_v = tk.IntVar()
            self.low_h.set(160) #default value
            self.low_s.set(50) #default value
            self.low_v.set(50) #default value
            low_hue_spin = tk.Spinbox(self.controls, from_=0, to=179, textvariable=self.low_h, increment=1, font=font, width=3)
            low_hue_spin.pack(side=tk.LEFT)
            low_label0 = tk.Label(self.controls,text='S ', height=4)
            low_label0.pack(side=tk.LEFT)
            low_saturation_spin = tk.Spinbox(self.controls, from_=0, to=255, textvariable=self.low_s, increment=1, font=font, width=3)
            low_saturation_spin.pack(side=tk.LEFT)
            low_label1 = tk.Label(self.controls,text='V ', height=4)
            low_label1.pack(side=tk.LEFT)
            low_value_spin = tk.Spinbox(self.controls, from_=0, to=255, textvariable=self.low_v, increment=1, font=font, width=3)
            low_value_spin.pack(side=tk.LEFT)
            high_label = tk.Label(self.controls,text='Maior nível de: H ', height=4)
            high_label.pack(side=tk.LEFT)
            self.high_h = tk.IntVar()
            self.high_s = tk.IntVar()
            self.high_v = tk.IntVar()
            self.high_h.set(179) #default value
            self.high_s.set(255) #default value
            self.high_v.set(255) #default value
            high_hue_spin = tk.Spinbox(self.controls, from_=0, to=179, textvariable=self.high_h, increment=1, font=font, width=3)
            high_hue_spin.pack(side=tk.LEFT)
            high_label0 = tk.Label(self.controls,text='S ', height=4)
            high_label0.pack(side=tk.LEFT)
            high_saturation_spin = tk.Spinbox(self.controls, from_=0, to=255, textvariable=self.high_s, increment=1, font=font, width=3)
            high_saturation_spin.pack(side=tk.LEFT)
            high_label1 = tk.Label(self.controls,text='V ', height=4)
            high_label1.pack(side=tk.LEFT)
            high_value_spin = tk.Spinbox(self.controls, from_=0, to=255, textvariable=self.high_v, increment=1, font=font, width=3)
            high_value_spin.pack(side=tk.LEFT)
            self.create_button('Segmentar', apply_image_seg) 

        def apply_image_seg():
            if (len(self.current_image.shape) > 2): #imagem colorida
                lower_range = np.array([self.low_h.get(), self.low_s.get(), self.low_v.get()])
                upper_range = np.array([self.high_h.get(), self.high_s.get(), self.high_v.get()])
                t1,m,t2,r = segmentation_function(self.current_image,lower_range,upper_range)
                self.create_update_pyplot_window(t1,m,t2,r)      
            else:
                tkinter.messagebox.showinfo(title='', message='A imagem deve ser colorida!')         
        
        return create_controls
    

    def create_threshold_controls(self,segmentation_function):
        def create_controls():
            self.clear_control_frame()
            font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
            self.threshold = tk.IntVar()
            self.threshold.set(127) #default value
            factor_label = tk.Label(self.controls,text='Limiar: ', height=4)
            factor_label.pack(side=tk.LEFT)
            thresh_spin = tk.Spinbox(self.controls, from_=0, to=255, textvariable=self.threshold, increment=1, font=font, width=3)
            thresh_spin.pack(side=tk.LEFT)
            slider = tk.Scale(self.controls,from_=0, to=255, variable=self.threshold,tickinterval=20, resolution=1,length= 300, orient="horizontal")
            slider.pack(side=tk.LEFT)
            self.create_button('Segmentar', apply_image_seg) 

        def apply_image_seg():
            t1,m,t2,r = segmentation_function(self.current_image,self.threshold.get())
            self.create_update_pyplot_window(t1,m,t2,r)           
        
        return create_controls

    def create_otsu_threshold_controls(self,segmentation_function):
        def create_controls():
            self.clear_control_frame()
            self.create_button('Segmentar', apply_image_seg) 

        def apply_image_seg():
            t1,m,t2,r = segmentation_function(self.current_image)
            self.create_update_pyplot_window(t1,m,t2,r)           
        
        return create_controls
    
    def create_canny_controls(self,segmentation_function):
        def create_controls():
            self.clear_control_frame()
            font = tkinter.font.Font(family='Helvetica', size=12, weight='bold')
            self.lower_thresh_rate = tk.DoubleVar()
            self.lower_thresh_rate.set(0.5) #default value
            thresh_label = tk.Label(self.controls,text='Percentual do Limiar Inferior em relação ao Limiar Superior: ', height=4)
            thresh_label.pack(side=tk.LEFT)
            thresh_spin = tk.Spinbox(self.controls, from_=0, to=1, textvariable=self.lower_thresh_rate, increment=0.1, font=font, width=3)
            thresh_spin.pack(side=tk.LEFT)
            slider = tk.Scale(self.controls,from_=0, to=1, variable=self.lower_thresh_rate,tickinterval=0.1, resolution=0.1,length= 300, orient="horizontal")
            slider.pack(side=tk.LEFT)
            self.create_button('Segmentar', apply_image_seg) 

        def apply_image_seg():
            t1,m,t2,r = segmentation_function(self.current_image,self.lower_thresh_rate.get())
            self.create_update_pyplot_window(t1,m,t2,r)           
        
        return create_controls
    
    def create_watershed_controls(self,segmentation_function):
        def create_controls():
            self.clear_control_frame()
            self.create_button('Segmentar', apply_image_seg) 

        def apply_image_seg():
            t1,m,t2,r = segmentation_function(self.current_image)
            self.create_update_pyplot_window(t1,m,t2,r)           
        
        return create_controls
    
    def create_update_pyplot_window(self,title1, mask, title2, result):
        plt.close('all')
        plt.figure(figsize=[9,4]) #pyplot window to show segmentation result
        plt.subplot(121)
        plt.title(title1,fontdict={'fontsize': 14})
        plt.imshow(mask, cmap='gray')
        plt.axis('off')
        plt.subplot(122)
        plt.title(title2,fontdict={'fontsize': 14})
        if (len(result.shape) > 2): #imagem colorida    
            plt.imshow(result)
        else:
            plt.imshow(result, cmap='gray')
        plt.axis('off')
        plt.show()     

if __name__== '__main__':
    app=Window()
    app.mainloop()