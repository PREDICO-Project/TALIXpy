import tkinter as tk
from GUI.styles import Styles as stl
from GUI.widgets import Widget as wg
from tkinter import ttk, filedialog
from tkinter.filedialog import asksaveasfilename
import os
#from skimage import io
import tifffile
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import src.TLRec.Image_Display as Image_Display 
from src.TLRec.Experimental_Retrieval import Modulation_Curve_Reconstruction
from src.TLRec.utils import Apply_Phase_Wiener_filter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import json
#from GUI.config.default_conf import default_TLRec_conf
import time

class TLRec_GUI:

    def __init__(self, master):

        #Crea la ventana principal
        #global root
        #root = tk.Tk()
        global root
        root = master
        #root.title("TLRec")
        #root.configure(background='gray20')
        #root.state('zoomed')
        #root.attributes('-fullscreen', True)
        #root.geometry("1000x1000")

        #style = ttk.Style()
        #print(style.theme_names())

        #style.theme_use('classic')

        stl.configure_style()
        
        self.generate_load_files_frame()
        self.generate_raw_images_frame()
        self.generate_option_frame()
        self.generate_Modulation_Curve_frame()
        self.generate_PC_images_frame()
        self.initialize_variables()
    
        #root.protocol("WM_DELETE_WINDOW", quit)

        #root.mainloop()

    def initialize_variables(self):
        
        self.G1Period_default= tk.DoubleVar()
        self.G2Period_default= tk.DoubleVar()
        self.Energy_Default= tk.DoubleVar()
        self.DSG1_Default= tk.DoubleVar()
        self.DOG1_Default = tk.DoubleVar()
        self.DG1G2_Default= tk.DoubleVar()
        self.pixel_size= tk.DoubleVar()
        self.v0 = tk.DoubleVar()
        self.n = tk.IntVar()
        self.s = tk.DoubleVar()
        
        config_path  = os.path.join(os.path.dirname(__file__), "config")
        with open(os.path.join(config_path, 'config_TLRec.json')) as json_path:
            #default_TLRec_conf = json.load(os.path.join(config_path, 'config_inline.json'))

            default_TLRec_conf = json.load(json_path)
            self.G1Period_default.set(default_TLRec_conf["G1Period"])  #micrometer
            self.G2Period_default.set(default_TLRec_conf['G2Period'])  #micrometer
            self.Energy_Default.set(default_TLRec_conf['Design_Energy'])#keV
            self.DSG1_Default.set(default_TLRec_conf['DSG1']) #Distance source-G1 in cm
            self.DOG1_Default.set(default_TLRec_conf['DOG1']) #Distance Object-G1 in cm
            self.DG1G2_Default.set(default_TLRec_conf['DG1G2']) #Distance G1-G2 in cm.
            self.pixel_size.set(default_TLRec_conf['Detetor_pixel_size'])
            self.v0.set(default_TLRec_conf['v0'])
            self.n.set(default_TLRec_conf['m'])
            self.s.set(default_TLRec_conf['s'])

    def quit():
        root.quit()   # stops mainloop
        root.destroy()

    def generate_option_frame(self):

        OPTIONS = [
        "Least Squares",
        "Fast Least Squares",
        "Step Correction",
        "Fast FFT",
        "FFT"
        ]
        global Frame4
        Frame4 = ttk.Frame(root,borderwidth=2, relief='groove')
        Frame4.grid(row = 3, column=0, columnspan=2)

        global Frame5
        Frame5= ttk.Frame(root)
        Frame5.grid(row = 4, column=0, columnspan=2)

        label = tk.Label(Frame4, text = 'Reconstruction Parameters', width=30)
        label.grid(row = 0, column = 0)
        self.Algorithm_ComboBoxLabel, self.Algorithm_ComboBox = wg.create_label_combobox(Frame4, label_text='Reconstruction Algorithm',row = 1,column =0, names = OPTIONS,state = 'disabled')
        self.Algorithm_ComboBox.current(0)
        
        self.UploadButton = wg.create_button(Frame4,'Confirm Algorithm', 2, 0, state = 'disabled', command= lambda:self.Upload(self.Algorithm_ComboBox))

        self.RetrieveButton = wg.create_button(Frame4,'Retrieve', 2, 1, state = 'disabled', command= lambda:self.Run(self.Algorithm_ComboBox))


        self.XLabel, self.X_position = wg.create_label_entry(Frame5, 'x coordinate', 0, 0,padx = 20, state='disable')
        self.YLabel, self.Y_position = wg.create_label_entry(Frame5, 'y coordinate', 1, 0,padx = 20, state='disable')
        
        self.CompareButton = wg.create_button(Frame5, 'Update Modulation Curve', 2, 0, padx = 60, state = 'disable',command = lambda: self.Compare_Fit(self.images, self.images_reference, 
        int(self.X_position.get()),int(self.Y_position.get()), rec_type=self.Algorithm_ComboBox))

    def generate_load_files_frame(self):
        main_frame = ttk.Frame(root, style='TFrame')
        main_frame.grid(row = 0, column = 0, columnspan=2,  sticky='nsew')

        button_reference = wg.create_button(main_frame, "Load Reference Images", 0, 0, command = self.UploadReference)
        self.button_images = wg.create_button(main_frame, "Load Object Images", 1, 0, state = 'disable', command = self.UploadAction)
        
        self.filenameEntry = wg.create_entry(main_frame,1,1)
        self.filename_r_Entry = wg.create_entry(main_frame,0,1)

        Modify_configButton = wg.create_button(main_frame, 'Modify Default Parameters', 2, 0, padx = 60, command = self.Open_config_params)
        
        ExitButton = wg.create_button(main_frame, "Exit", 3, 0, padx = 60, command=root.quit)


    def UploadReference(self):
        filename = filedialog.askopenfilename()
        self.filename_r_Entry.delete(0, tk.END)
        self.filename_r_Entry.insert(0, os.path.basename(filename))
        self.images_reference = tifffile.imread(filename)

        #self.images_reference = io.imread(filename)
        self.button_images['state'] = 'normal'
    
    def UploadAction(self):

        filename = filedialog.askopenfilename()
        self.filenameEntry.delete(0, tk.END)
        self.filenameEntry.insert(0, os.path.basename(filename))
        
        self.images = tifffile.imread(filename)
        #self.images = io.imread(filename)

        self.update_canvas(self.canvas_object, self.images[0])
        self.update_canvas(self.canvas_reference, self.images_reference[0])
        
        (z,y,x) = self.images.shape
        (zr,yr,xr) = self.images_reference.shape
        
        j = tk.IntVar()
        jr = tk.IntVar()
        

        def Change_Images(j):
            #self.Show_Image(images, int(j)-1, self.Frame_images)
            self.update_canvas(self.canvas_object, self.images[int(j)-1])
        def Change_Ref_Images(jr):
            self.update_canvas(self.canvas_reference, self.images_reference[int(jr)-1])
            #self.Show_Image(images_reference, int(jr)-1, self.Frame_Ref_images)
        
        slider1 = tk.Scale(self.Frame_images, from_=1, to=z, resolution = 1, orient='horizontal', variable= j,command = Change_Images, bg = 'gray20', fg='white', troughcolor='white', highlightthickness=0) 
        slider1.grid(row=1, column=0)
    
        slider2 = tk.Scale(self.Frame_Ref_images, from_=1, to=zr, resolution = 1, orient='horizontal', variable= jr,command =  Change_Ref_Images, bg = 'gray20', fg='white', troughcolor='white', highlightthickness=0) 
        slider2.grid(row=1, column=0)
        
        self.Algorithm_ComboBoxLabel['state'] = 'normal'
        self.Algorithm_ComboBox['state'] = 'normal'
        self.UploadButton['state'] = 'normal'

    def Open_config_params(self):

        global params_window
        params_window = tk.Toplevel()
        params_window.title("Default Parameters")

        paramsFrame = ttk.Frame(params_window)
        paramsFrame.grid(row=0, column=0, sticky="ns")
        
        
        wg.create_label_entry(paramsFrame, "G1 Period (micrometer):", 0, 0,textvariable=self.G1Period_default)
        wg.create_label_entry(paramsFrame, "G2 Period (micrometer):", 1, 0,textvariable=self.G2Period_default)

        wg.create_label_entry(paramsFrame, "Design Energy (keV):", 2, 0,textvariable=self.Energy_Default)

        wg.create_label_entry(paramsFrame, "Distance Source-G1 (cm):", 3, 0,textvariable=self.DSG1_Default)
        wg.create_label_entry(paramsFrame, "Distance Object-G1 (cm):", 4, 0,textvariable=self.DOG1_Default)
        wg.create_label_entry(paramsFrame, "Distance G1-G2 (cm):", 5, 0,textvariable=self.DG1G2_Default)
        wg.create_label_entry(paramsFrame, "Detector pixel size (micrometer):", 6, 0,textvariable=self.pixel_size)
        wg.create_label_entry(paramsFrame, "Frequency cut-off (Wiener filter):", 7, 0,textvariable=self.v0)
        wg.create_label_entry(paramsFrame, "Butterworth's filter n-order (int):", 8, 0,textvariable=self.n)
        wg.create_label_entry(paramsFrame, "Butterworth's filter signal:", 9, 0,textvariable=self.s)

        wg.create_button(paramsFrame, 'Save/Modify',10,0, command =self.apply_changes_json )

    def apply_changes_json(self):
        config_path  = os.path.join(os.path.dirname(__file__), "config")
        with open(os.path.join(config_path, 'config_TLRec.json'), 'r') as json_path:
            default_TLRec_conf = json.load(json_path)
            default_TLRec_conf["G1Period"] = self.G1Period_default.get()
            default_TLRec_conf['G2Period'] = self.G2Period_default.get() #micrometer
            default_TLRec_conf['Design_Energy'] = self.Energy_Default.get()#keV
            default_TLRec_conf['DSG1']=self.DSG1_Default.get() #Distance source-G1 in cm
            default_TLRec_conf['DOG1']=self.DOG1_Default.get() #Distance Object-G1 in cm
            default_TLRec_conf['DG1G2'] = self.DG1G2_Default.get() #Distance G1-G2 in cm.
            default_TLRec_conf['Detetor_pixel_size'] =self.pixel_size.get()
            default_TLRec_conf['v0'] =self.v0.get()
            default_TLRec_conf['m'] = self.n.get()
            default_TLRec_conf['s'] = self.s.get()

        with open(os.path.join(config_path, 'config_TLRec.json'), "w") as jsonFile:
            json.dump(default_TLRec_conf, jsonFile)
        
        params_window.destroy()
       


    def generate_raw_images_frame(self):
        """
        Generate the Frames where the object and reference images will be shown
        """
        self.Frame_Ref_images = ttk.Frame(root, style='TFrame')
        self.Frame_Ref_images.grid(row=1, column=0)

        self.Frame_images = ttk.Frame(root, style='TFrame')
        self.Frame_images.grid(row=1, column=1)

        # Initialize the canvas
        self.canvas_object = self.create_canvas(self.Frame_images, 0 ,0, width = 175, height = 200)
        self.canvas_reference = self.create_canvas(self.Frame_Ref_images, 0 ,0, width = 175, height = 200)
        

    def generate_Modulation_Curve_frame(self):
        
        self.SinesPlot = ttk.Frame(root, style='TFrame')
        #SinesPlot = tk.Frame(root)
        self.SinesPlot.grid(row=5, column = 0, columnspan=2)

        self.initialize_Figure(self.SinesPlot, (3, 1), 1,0)

        #self.Modulation_curve_canvas = self.create_canvas(self.SinesPlot, 0, 0, width=500, height=400) 

    def generate_PC_images_frame(self):
        self.CanvasPlot = ttk.Frame(root, style='TFrame')
        self.CanvasPlot.grid(row=0, column= 2, rowspan =6, columnspan = 3)

        self.initialize_Figure(self.CanvasPlot, (2, 2), 0,0)
        self.initialize_Figure(self.CanvasPlot, (2, 2), 0,1)
        self.initialize_Figure(self.CanvasPlot, (2, 2), 2,0)
        self.initialize_Figure(self.CanvasPlot, (2, 2), 2,1)
        #self.DPC_canvas = self.create_canvas(self.CanvasPlot, 0, 0, 200, 300)
        #self.Phase_canvas = self.create_canvas(self.CanvasPlot, 0, 1, 200, 300)
        #self.At_canvas = self.create_canvas(self.CanvasPlot, 2, 0, 200, 300)
        #self.DF_canvas = self.create_canvas(self.CanvasPlot, 2, 1, 200, 300)

    def create_canvas(self, frame, row, column, width, height):
        canvas = tk.Canvas(frame,width= width, height= height, bg='gray20', highlightthickness=0)
        canvas.grid(row=row, column=column, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return canvas
    
    def update_canvas(self, canvas, image):
    
        width, height = canvas.winfo_width(), canvas.winfo_height()
        
        image_pil = Image.fromarray(np.uint8((image-np.min(image))/(np.max(image)-np.min(image))*255))
        resized_image = image_pil.resize((width, height))
        photo = ImageTk.PhotoImage(resized_image)
        
        canvas.image = photo  
        canvas.create_image(0, 0, anchor = tk.NW, image=canvas.image)

    def save_image(self, data):
      files = [('All Files', '*.*'), 
                ('Python Files', '*.py'),
                ('HDF5 File', '*.hdf5'),
                ('Tiff File', '*.tiff')]
      file = asksaveasfilename(filetypes = files, defaultextension = '.tif')
        #file = asksaveasfilename()
      if not file: 
          return
      
      im = Image.fromarray(data)
      sv = im.save(file)


    def Upload(self, reconstruction):        

        self.Compare_Fit(self.images, self.images_reference,  self.images.shape[2]//2, self.images.shape[1]//2, rec_type=reconstruction)

        self.CompareButton['state'] = 'normal'
        self.Y_position['state'] = 'normal'
        self.X_position['state'] = 'normal'
        self.RetrieveButton['state'] = 'normal'

    def Compare_Fit(self, images, images_reference, x_position, y_position, rec_type):
        if rec_type.get() == 'FFT':  
            rtype = 'FFT'
        elif rec_type.get() == 'Least Squares' or rec_type.get() == 'Least Squares Kaeppler' or rec_type.get() == 'Improve_least_squares' or rec_type.get() == 'Dose Correction':  
            rtype = 'least_squares'
        elif rec_type.get() == 'Fast Least Squares':
            rtype = 'fast_lstsq'
        elif rec_type.get() == 'Step Correction':
            rtype = 'Step_correction'
        elif rec_type.get() == 'Fast FFT':
            rtype = 'Fast_FFT'
        plt.close()

        params = {"text.color" : "black",
          "xtick.color" : "black",
          "ytick.color" : "black"}
        plt.rcParams.update(params)
        
        x_data, y_data, x, y = Image_Display.Pixel_intensity_one_period(images, x_position,y_position,rtype, Fourier=False)
        x_data_r, y_data_r, x_r, y_r = Image_Display.Pixel_intensity_one_period(images_reference, x_position,y_position,rtype,Fourier=False)
        fig=Figure(figsize=(3,1.5))
        ax = fig.add_subplot(1,1,1)
        ax.set_title('Fit at ({},{})'.format(x_position, y_position))
        ax.scatter(x_data, y_data, color= "blue",marker= ".")
        ax.plot(x, y,label='Sample', color ="blue")
        ax.scatter(x_data_r, y_data_r, color= "green",marker= ".")
        ax.plot(x_r,y_r, label='Reference', color ="green")
        ax.legend(loc='best')
        ax.set_ylabel("Intensity")
        ax.set_xlabel(r'$\chi$') 
        old_x_axis = (0,np.pi/2,np.pi,3*np.pi/2,2*np.pi)
        new_x_axis = ('0',r'$\pi/2$',r'$\pi$',r'$3\pi/4$',r'$2\pi$')
        #ax.set_xticks(old_x_axis, new_x_axis)
        
        canvasf = FigureCanvasTkAgg(fig, master=self.SinesPlot)
        canvasf.get_tk_widget().grid(row=1, column=0, ipadx=60, ipady=40)
        canvasf.draw()
        
        #toolbarFrame = Button(SinesPLot,text='Save Image', command=save_image(fig))
        #toolbarFrame.grid(row=2,column=0)        

    def initialize_Figure(self, frame, figsize, row, column):

        fig = Figure(figsize = figsize)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        fig.set_facecolor("#333333")

        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, ipadx=60, ipady=50,pady=10)

    def Plot_Figure(self, frame, image, row, column, figsize, title):
        plt.close()
        params = {"text.color" : "white",
          "xtick.color" : "white",
          "ytick.color" : "white"}
        plt.rcParams.update(params)

        fig=Figure(figsize=figsize)
        fig.set_facecolor("#333333")
        ax = fig.add_subplot(1,1,1)
        
        im = ax.imshow(image,"gray")
        ax.set_title(title)
        fig.colorbar(im,ax=ax)
        #plt.show()
        canvas1 = FigureCanvasTkAgg(fig, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=row, column=column, ipadx=90, ipady=20)
        toolbarFrame1 = tk.Frame(master=frame)
        toolbarFrame1.grid(row=row+1,column=column)

    def Run(self, reconstruction):
        global Diff_Phase, attenuation, transmission, Dark_Field, Phase
        #Compare_Fitting(images, images_reference,1,float(G2PeriodV.get()), 400, 400, FFT=False)
        if reconstruction.get() == 'Least Squares':
            rec_type='least_squares'
        if reconstruction.get() == 'Fast Least Squares':
            rec_type = 'fast_lstsq'
        if reconstruction.get() == 'Least Squares Kaeppler':
            rec_type='least_squares_corrections'
        if reconstruction.get() == 'Improve_least_squares':
            rec_type = 'Improve_least_squares' 
        if reconstruction.get() == 'Step Correction':
            rec_type = 'Step_correction' 
        if reconstruction.get() == 'Dose Correction':
            rec_type = 'Dose_correction' 
        if reconstruction.get() == 'FFT':
            rec_type = 'FFT'
        if reconstruction.get() == 'Fast FFT':
            rec_type = 'Fast_FFT'
        start_time = time.perf_counter()
        Diff_Phase, attenuation, transmission, Dark_Field, Phase, Phase_Stepping_Curve_reference, Phase_Stepping_Curve_object = Modulation_Curve_Reconstruction(self.images, self.images_reference,
        self.G2Period_default.get(),self.DSG1_Default.get(), self.DG1G2_Default.get(), self.DOG1_Default.get(), self.Energy_Default.get(), self.pixel_size.get(),type=rec_type, unwrap_phase=False)
        end_time = time.perf_counter()
        print("time: {} s".format(end_time-start_time))
        Phase = Apply_Phase_Wiener_filter(Diff_Phase, self.pixel_size.get(), self.pixel_size.get(), self.v0.get(), self.n.get(), self.s.get())
        
        self.Plot_Figure(self.CanvasPlot, Diff_Phase, 0, 0, (3,3), 'Phase Gradient')
        self.Plot_Figure(self.CanvasPlot, Phase, 0, 1, (3,3), 'Integrated Phase')
        self.Plot_Figure(self.CanvasPlot, transmission, 2, 0, (3,3), 'Transmission')
        self.Plot_Figure(self.CanvasPlot, Dark_Field, 2, 1, (3,3), 'Dark Field')
    
        bt1 = wg.create_button(self.CanvasPlot, 'Save Image', 1,0, command=  lambda : self.save_image(Diff_Phase))
        bt2 = wg.create_button(self.CanvasPlot, 'Save Image', 1,1, command=  lambda : self.save_image(Phase))
        bt3 = wg.create_button(self.CanvasPlot, 'Save Image', 3,0, command=  lambda : self.save_image(transmission))
        bt4 = wg.create_button(self.CanvasPlot, 'Save Image', 3,1, command=  lambda : self.save_image(Dark_Field))
        
    
if __name__ == "__main__":
    TLRec_GUI()