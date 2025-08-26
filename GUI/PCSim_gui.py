import tkinter as tk
from GUI.styles import Styles as stl
from GUI.widgets import Widget as wg
from tkinter import ttk, filedialog
from tkinter.filedialog import asksaveasfilename
import os
import tifffile
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import src.PCSim.Objects as obj
import src.PCSim.Geometry as geom
import json
import src.PCSim.experiments as exp
import src.PCSim.source as source 
from src.PCSim.TL_conf import TL_CONFIG
import src.PCSim.detector as detector
import src.PCSim.check_Talbot as check_Talbot
from GUI.TLRec_gui import TLRec_GUI
from GUI.text import check_TL_text


class PCSim_gui:

    def __init__(self, master):

        self.parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.granpa_path = os.path.abspath(os.path.join(self.parent_path, os.pardir))
        self.granpa2_path = os.path.abspath(os.path.join(self.granpa_path, os.pardir))
        self.root_path = os.path.abspath(os.path.join(self.granpa2_path, os.pardir))
        #Crea la ventana principal
        #global root
        #root = tk.Tk()
        self.root_path
        global root
        root = master
        #root.title("PCSim Inline")
        #root.configure(background='gray20')

        #style = ttk.Style()
        #print(style.theme_names())

        #style.theme_use('classic')
        global Beam_Shape_OPTIONS, Beam_Spectrum_OPTIONS, Object_OPTIONS, Image_OPTIONS
        spectra_path = os.path.join(self.parent_path, 'Resources','Spectra')
        Beam_Spectrum_OPTIONS = sorted([f for f in os.listdir(spectra_path) if os.path.isfile(os.path.join(spectra_path, f))])
        Beam_Spectrum_OPTIONS.append("Monoenergetic")
        Beam_Shape_OPTIONS = ["Plane", "Conical"]
        Object_OPTIONS = ["Sphere",  "Cylinder"]
        Image_OPTIONS = ["Ideal", "Realistic"]


        stl.configure_style()

        # Create tab container
        self.tab_container = ttk.Notebook(root)
        self.tab_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        self.initialize_vars()
        self.create_tabs()
    
        #root.protocol("WM_DELETE_WINDOW", quit)
        #root.mainloop()

    def create_tabs(self):
        # Create a Frame for each tab
        self.TLRec_tab = ttk.Frame(self.tab_container)
        self.inline_tab = ttk.Frame(self.tab_container)
        self.check_TL_tab = ttk.Frame(self.tab_container)
        self.TL_tab = ttk.Frame(self.tab_container)

        # Add tabs to the tabs container
        self.tab_container.add(self.TLRec_tab, text = 'TLRec')
        self.tab_container.add(self.inline_tab, text="Inline Simulation")
        self.tab_container.add(self.check_TL_tab, text="Check Talbot-Lau effect")
        self.tab_container.add(self.TL_tab, text="Talbot Lau Phase Contrast Simulation")

        self.populate_TLRec_tab()
        self.populate_inline_tab()
        self.populate_checkTL_tab()
        self.populate_TL_tab()
        
    def populate_TLRec_tab(self):
        TLRec_GUI(self.TLRec_tab)

    def populate_inline_tab(self):
        
        parameters_frame = ttk.Frame(self.inline_tab, style='TFrame')
        parameters_frame.grid(row = 0, column = 0, columnspan=2,  sticky='nsew')

        self.i_results_frame = ttk.Frame(self.inline_tab, style='TFrame')
        self.i_results_frame.grid(row = 0, column = 2, rowspan=12,  sticky='nsew')

        self.initialize_Figure(self.i_results_frame, (3,3), 0,0)

        nLabel, _ = wg.create_label_entry(parameters_frame, 'n: size of the wavefront in pixels', 0, 0,textvariable=self.i_n,padx = 20)
        pxLabel, _ = wg.create_label_entry(parameters_frame, 'Pixel size (micrometer)', 1, 0,textvariable=self.i_pixel_size,padx = 20)
        DODLabel,_ = wg.create_label_entry(parameters_frame, 'Distance Object Detector (cm)', 2, 0,textvariable=self.i_DOD,padx = 20)
        self.DSOLabel,_ = wg.create_label_entry(parameters_frame, 'Distance Source-Object (cm)', 3, 0,textvariable=self.i_DSO,padx = 20)
        self.FWHMSouLabel,_ = wg.create_label_entry(parameters_frame, 'Source FWHM (micrometer)', 4, 0,textvariable=self.i_FWHM_source,padx = 20)
        self.BeamShapeLabel,_ = wg.create_label_combobox(parameters_frame, label_text='Beam Shape',row = 5 ,column =0, textvariable = self.i_Beam_Shape, names = Beam_Shape_OPTIONS)
        self.BeamSpectrumLabel,_ = wg.create_label_combobox(parameters_frame, label_text='Spectrum',row = 6 ,column =0, textvariable = self.i_Beam_Spectrum,names = Beam_Spectrum_OPTIONS)
        self.BeamEnergyL,_ = wg.create_label_entry(parameters_frame, 'Energy (keV, necessary to initialize the variable)', row=7, column=0, textvariable=self.i_beam_energy, padx = 20)
        self.ObjectLabel,_ = wg.create_label_combobox(parameters_frame, label_text='Object',row = 8 ,column =0, textvariable = self.i_Object,names = Object_OPTIONS)
        wg.create_button(parameters_frame, 'Set Object Parameters', 9, 0, command = self.open_params)
        self.DetectorL,_ = wg.create_label_combobox(parameters_frame, label_text='Image',row = 10 ,column =0, textvariable = self.i_image_option,names = Image_OPTIONS)
        self.PixelDetectorL,_ = wg.create_label_entry(parameters_frame, 'Detector Pixel Size (microns)', 11, 0,textvariable=self.i_detector_pixel_size,padx = 20)
        self.ResolutionL,_ = wg.create_label_entry(parameters_frame, 'Detector Resolution (FWHM microns)', 12, 0,textvariable=self.i_FWHM_detector,padx = 20)
        self.RunButton = wg.create_button(parameters_frame, 'Run', 13,0,command = self.RunInline)

        ExitButton = wg.create_button(parameters_frame, "Exit", 14, 0, padx = 60, command=root.quit)

    def populate_checkTL_tab(self):
        
        Grating_OPTIONS = ["Custom", "Phase pi/2", "Phase pi"]

        parameters_frame = ttk.Frame(self.check_TL_tab, style='TFrame')
        parameters_frame.bind("<Button-1>", self.modify_TL_dist)
        parameters_frame.grid(row = 0, column = 0, columnspan=2,  sticky='nsew')

        self.c_results_frame = ttk.Frame(self.check_TL_tab, style='TFrame')
        self.c_results_frame.grid(row = 0, column = 2, rowspan=12,  sticky='nsew')

        self.initialize_Figure(self.c_results_frame, (3,3), 0,0)

        nLabel, _ = wg.create_label_entry(parameters_frame, 'n: size of the wavefront in pixels', 0, 0,textvariable=self.c_n,padx = 20)
        pxLabel, _ = wg.create_label_entry(parameters_frame, 'Pixel size (micrometer)', 1, 0,textvariable=self.c_pixel_size,padx = 20)
        FWHMSouLabel,_ = wg.create_label_entry(parameters_frame, 'Source FWHM (micrometer)', 2, 0,textvariable=self.c_FWHM_source,padx = 20)
        EnergyL,_ = wg.create_label_entry(parameters_frame, 'DEsign Energy (keV)', 3, 0,textvariable=self.c_energy,padx = 20)
        PeriodL,_ = wg.create_label_entry(parameters_frame, 'Grating Period (microns)', 4, 0,textvariable=self.c_period,padx = 20)
        DCL,_ = wg.create_label_entry(parameters_frame, 'Duty Cycle', 5, 0,textvariable=self.c_DC,padx = 20)
        materialL,_ = wg.create_label_entry(parameters_frame, 'Material (just used for custom grating)', 6, 0,textvariable=self.c_material,padx = 20)
        barHeightL,_ = wg.create_label_entry(parameters_frame, 'Bar height (micrometer, just for custom grating)', 7, 0,textvariable=self.c_bar_height,padx = 20)
        gratigL,_ = wg.create_label_combobox(parameters_frame, label_text='Grating Type',row = 8 ,column =0, textvariable = self.c_grating_def, names = Grating_OPTIONS)
        multiplesL,_ = wg.create_label_entry(parameters_frame, 'Multiples of Talbot distance to be represented', row=9, column=0, textvariable=self.c_multiple, padx = 20)
        iterationsL,_ = wg.create_label_entry(parameters_frame, 'Number of calculations performed', row=10, column=0, textvariable=self.c_iterations, padx = 20)
        TLDist,_ = wg.create_label_entry(parameters_frame, 'Talbot Distance (cm)', 11, 0,textvariable=self.c_Talbot_distance,padx = 20, state='disable')
        #iterationsL,_ = wg.create_label_combobox(parameters_frame, label_text='Image',row = 8 ,column =0, textvariable = self.c_image_option,names = Image_OPTIONS)
        #self.ResolutionL,_ = wg.create_label_entry(parameters_frame, 'Detector Resolution (pixel Size in microns)', 9, 0,textvariable=self.c_resolution,padx = 20)
        self.RunButton = wg.create_button(parameters_frame, 'Run', 12,0,command = self.RunCheckTL)

        ExitButton = wg.create_button(parameters_frame, "Exit", 13, 0, padx = 60, command=root.quit)
        font = {'family': 'serif',
        'color':  'lightgray',
        'weight': 'normal',
        'size': 10,
        }
        fig_text = Figure(figsize=(5,4))
        fig_text.set_facecolor("#333333")
        canvas = FigureCanvasTkAgg(fig_text, parameters_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row = 11, column = 0, columnspan=3)
        text = fig_text.text(0.5, 0.5,check_TL_text, ha='center', va='center', bbox=dict(facecolor='#333333', alpha=0.5), fontdict=font)
        canvas.figure = fig_text
        canvas.draw()
        #checkTL_text = wg.create_text_area(parameters_frame, 13,0)
        #checkTL_text.config(state='normal')
        #checkTL_text.insert(tk.END, check_TL_text)
        #checkTL_text.config(state='disabled')
        
    def populate_TL_tab(self):
        
        Grating_OPTIONS = ["Phase pi/2", "Phase pi"]
        Movable_OPTIONS = ["G1", "G2"]
        
        parameters_frame = ttk.Frame(self.TL_tab, style='TFrame')
        parameters_frame.grid(row = 0, column = 0, columnspan=2,  sticky='nsew')
        parameters_frame.bind("<Button-1>", self.modify_DOD)
        self.TL_results_frame = ttk.Frame(self.TL_tab, style='TFrame')
        self.TL_results_frame.grid(row = 0, column = 2, rowspan=12,  sticky='nsew')

        self.initialize_Figure(self.TL_results_frame, (3,3), 0,0)
        
        nLabel, _ = wg.create_label_entry(parameters_frame, 'n: size of the wavefront in pixels', 0, 0,textvariable=self.TL_n,padx = 20)
        pxLabel, _ = wg.create_label_entry(parameters_frame, 'Pixel size (microns)', 1, 0,textvariable=self.TL_pixel_size,padx = 20)
        wg.create_label_entry(parameters_frame, 'Source FWHM (micrometer)', 2, 0,textvariable=self.TL_FWHM_source,padx = 20)
        wg.create_label_combobox(parameters_frame, label_text='Beam Shape',row = 3 ,column =0, textvariable = self.TL_BeamShape, names = Beam_Shape_OPTIONS)
        wg.create_label_combobox(parameters_frame, label_text='Spectrum',row = 4 ,column =0, textvariable = self.TL_Beam_Spectrum,names = Beam_Spectrum_OPTIONS)
        wg.create_label_entry(parameters_frame, 'Design Energy (keV)', row=5, column=0, textvariable=self.TL_beam_energy, padx = 20)
        wg.create_label_entry(parameters_frame, 'Distance Source-G1 (cm)', 6, 0,textvariable=self.TL_DSO,padx = 20)
        wg.create_label_entry(parameters_frame, 'Distance Object-G1 (cm)', 7, 0,textvariable=self.TL_DOG1,padx = 20)
        wg.create_label_entry(parameters_frame, 'Multiple of Talbot distance', 8, 0,textvariable=self.TL_TLmultiple,padx = 20)
        wg.create_label_entry(parameters_frame, 'Talbot Distance (cm)', 9, 0,textvariable=self.TL_Talbot_distance,padx = 20, state='disable')
        wg.create_label_entry(parameters_frame, 'Magnification', 10, 0,textvariable=self.TL_M,padx = 20, state='disable')
        wg.create_label_entry(parameters_frame, 'Distance G1-G2 (cm)', 11, 0,textvariable=self.TL_DOD,padx = 20, state='disable')
        wg.create_label_entry(parameters_frame, 'G1 Period (microns)', 12, 0,textvariable=self.TL_Period_G1,padx = 20)
        wg.create_label_entry(parameters_frame, 'G2 Period (microns)', 13, 0,textvariable=self.TL_Period_G2,padx = 20, state = 'disable')
        wg.create_label_combobox(parameters_frame, label_text='G1 Phase',row = 14 ,column =0, textvariable = self.TL_G1_Phase,names = Grating_OPTIONS)
        wg.create_label_combobox(parameters_frame, label_text='Movable Grating',row = 15 ,column =0, textvariable = self.TL_MovableGrating, names = Movable_OPTIONS)
        wg.create_label_entry(parameters_frame, 'Number of steps (int)', 16, 0,textvariable=self.TL_steps,padx = 20)
        wg.create_label_entry(parameters_frame, 'Step Length (microns)', 17, 0,textvariable=self.TL_step_length,padx = 20)
        wg.create_label_combobox(parameters_frame, label_text='Object',row = 18 ,column =0, textvariable = self.TL_Object,names = Object_OPTIONS)
        wg.create_button(parameters_frame, 'Set Object Parameters', 19, 0, command = self.open_params_TL)
        wg.create_label_combobox(parameters_frame, label_text='Image',row = 20 ,column =0, textvariable = self.TL_image_option,names = Image_OPTIONS)
        wg.create_label_entry(parameters_frame, 'Detector Pixel Size (microns)', 21, 0,textvariable=self.TL_detector_pixel_size,padx = 20)
        wg.create_label_entry(parameters_frame, 'Detector Resolution (pixel Size in microns)', 22, 0,textvariable=self.TL_resolution,padx = 20)
        wg.create_button(parameters_frame, 'Run', 23,0,command = self.RunTL)

        ExitButton = wg.create_button(parameters_frame, "Exit", 24, 0, padx = 60, command=root.quit)

    def initialize_vars(self):

        config_path  = os.path.join(os.path.dirname(__file__), "config")

         # Inline
        self.i_n= tk.IntVar()
        self.i_pixel_size= tk.DoubleVar()
        self.i_DSO= tk.DoubleVar()
        self.i_DOD= tk.DoubleVar()
        self.i_FWHM_source = tk.DoubleVar()
        self.i_Beam_Shape= tk.StringVar()
        self.i_Beam_Spectrum= tk.StringVar()
        self.i_beam_energy = tk.DoubleVar()
        self.i_Object = tk.StringVar()
        self.i_image_option = tk.StringVar()
        self.i_resolution = tk.IntVar()

        self.i_radius = tk.DoubleVar()
        self.i_inner_radius = tk.DoubleVar()
        self.i_xshift = tk.IntVar()
        self.i_yshift = tk.IntVar()
        self.i_material = tk.StringVar()
        self.i_orientation = tk.StringVar()
        self.i_FWHM_detector = tk.DoubleVar()
        self.i_detector_pixel_size = tk.DoubleVar()

        
        with open(os.path.join(config_path, 'config_inline.json')) as json_path:
            #default_TLRec_conf = json.load(os.path.join(config_path, 'config_inline.json'))

            default_inline_conf = json.load(json_path)
        
            self.i_n.set(default_inline_conf['n'])
            self.i_pixel_size.set(default_inline_conf['pixel_size'])
            self.i_DSO.set(default_inline_conf['DSO'])
            self.i_DOD.set(default_inline_conf['DOD'])
            self.i_FWHM_source.set(10.)
            self.i_Beam_Shape.set(default_inline_conf['Beam_Shape'])
            self.i_Beam_Spectrum.set(default_inline_conf['Beam_Spectrum'])
            self.i_beam_energy.set(default_inline_conf['energy'])
            self.i_Object.set(default_inline_conf['Object'])
            self.i_radius.set(default_inline_conf['radius'])
            self.i_inner_radius.set(0.)
            self.i_xshift.set(default_inline_conf['xshift'])
            self.i_yshift.set(default_inline_conf['yshift'])
            self.i_material.set(default_inline_conf['material'])
            self.i_image_option.set(default_inline_conf['image_option'])
            self.i_orientation.set('Vertical')
            self.i_resolution.set(default_inline_conf['resolution'])
            self.i_FWHM_detector.set(30.)
            self.i_detector_pixel_size.set(default_inline_conf['detector_pixel_size']) #um

        # Check TL

        self.c_n = tk.IntVar()
        self.c_pixel_size = tk.DoubleVar()
        self.c_FWHM_source = tk.DoubleVar()
        self.c_energy = tk.DoubleVar()
        self.c_period = tk.DoubleVar()
        self.c_DC = tk.DoubleVar()
        self.c_material = tk.StringVar()
        self.c_bar_height = tk.DoubleVar()
        self.c_multiple = tk.IntVar()
        self.c_iterations = tk.IntVar()
        self.c_grating_def = tk.StringVar()
        self.c_Talbot_distance = tk.DoubleVar()
        #self.c_image_option = tk.StringVar()
        #self.c_resolution = tk.IntVar()

        with open(os.path.join(config_path, 'config_checkTL.json')) as json_path:
            #default_TLRec_conf = json.load(os.path.join(config_path, 'config_inline.json'))

            default_checkTL_conf = json.load(json_path)
            self.c_n.set(default_checkTL_conf['n'])
            self.c_pixel_size.set(default_checkTL_conf['pixel_size'])
            self.c_FWHM_source.set(10.)
            self.c_energy.set(default_checkTL_conf['energy'])
            self.c_period.set(default_checkTL_conf['period'])
            self.c_DC.set(default_checkTL_conf['DC'])
            self.c_material.set(default_checkTL_conf['material'])
            self.c_bar_height.set(default_checkTL_conf['bar_height'])
            self.c_multiple.set(default_checkTL_conf['multiples'])
            self.c_iterations.set(default_checkTL_conf['iterations'])
            self.c_grating_def.set(default_checkTL_conf['grating_option'])
            #self.c_image_option.set(default_checkTL_conf['image_option'])
            #self.c_resolution.set(default_checkTL_conf['resolution'])

        # Talbot Lau
        self.TL_n = tk.IntVar()
        self.TL_pixel_size = tk.DoubleVar()

        self.TL_FWHM_source = tk.DoubleVar()
        self.TL_BeamShape = tk.StringVar()
        self.TL_Beam_Spectrum= tk.StringVar()
        self.TL_beam_energy = tk.DoubleVar()

        self.TL_DSO = tk.DoubleVar()
        self.TL_DOG1 = tk.DoubleVar()
        self.TL_DOD = tk.DoubleVar()
        self.TL_Talbot_distance = tk.DoubleVar()
        self.TL_M = tk.DoubleVar()
        self.TL_TLmultiple = tk.IntVar()

        self.TL_Object = tk.StringVar()
        self.TL_radius = tk.DoubleVar()
        self.TL_inner_radius = tk.DoubleVar()
        self.TL_material= tk.StringVar()
        self.TL_xshift = tk.IntVar()
        self.TL_yshift = tk.IntVar()
        self.TL_orientation = tk.StringVar()

        self.TL_Period_G1 = tk.DoubleVar() 
        self.TL_Period_G2 = tk.DoubleVar()
        self.TL_ThicknessG1 = tk.DoubleVar() #um
        self.TL_ThicknessG2 = tk.DoubleVar() #um
        self.TL_G1_Phase = tk.StringVar()
        self.TL_MovableGrating = tk.StringVar()
        self.TL_steps = tk.IntVar()
        self.TL_step_length = tk.DoubleVar()

        self.TL_resolution = tk.DoubleVar() #um
        self.TL_detector_pixel_size = tk.IntVar()
        self.TL_image_option = tk.StringVar()

        with open(os.path.join(config_path, 'config_TLSim.json')) as json_path:
            #default_TLRec_conf = json.load(os.path.join(config_path, 'config_inline.json'))

            default_TL_conf = json.load(json_path)
            self.TL_n.set(default_TL_conf['n'])
            self.TL_FWHM_source.set(10.)
            self.TL_pixel_size.set(default_TL_conf['pixel_size'])

            self.TL_BeamShape.set(default_TL_conf['Beam_Shape'])
            self.TL_Beam_Spectrum.set(default_TL_conf['Beam_Spectrum'])
            self.TL_beam_energy.set(default_TL_conf['energy'])

            self.TL_DSO.set(default_TL_conf['DSG1'])
            self.TL_DOG1.set(default_TL_conf['DOG1'])
            #self.TL_DOD.set(default_TL_conf['DOD'])
            self.TL_TLmultiple.set(default_TL_conf['TLmultiple'])

            self.TL_Object.set(default_TL_conf['Object'])
            self.TL_radius.set(default_TL_conf['radius'])
            self.TL_inner_radius.set(0.)
            self.TL_material.set(default_TL_conf['material'])
            self.TL_xshift.set(default_TL_conf['xshift'])
            self.TL_yshift.set(default_TL_conf['yshift'])
            self.TL_orientation.set(default_TL_conf['orientation'])

            self.TL_Period_G1.set(default_TL_conf['period_G1'])
            self.TL_ThicknessG1.set(default_TL_conf['thickness_G1'])
            self.TL_ThicknessG2.set(default_TL_conf['thickness_G2'])
            self.TL_G1_Phase.set(default_TL_conf['G1_Phase'])
            self.TL_MovableGrating.set(default_TL_conf['MovableGrating'])
            self.TL_steps.set(default_TL_conf['steps'])
            self.TL_step_length.set(default_TL_conf['step_length'])

            self.TL_image_option.set(default_TL_conf['image_option'])
            self.TL_resolution.set(default_TL_conf['resolution'])
            self.TL_detector_pixel_size.set(default_TL_conf['detector_pixel_size'])


        
    def RunInline(self):
        n = self.i_n.get()
        DSO = self.i_DSO.get()
        DOD = self.i_DOD.get()
        pixel_size = self.i_pixel_size.get()
        Beam_Shape = self.i_Beam_Shape.get()
        FWHM_source = self.i_FWHM_source.get()
        Beam_Spectrum = os.path.splitext(self.i_Beam_Spectrum.get())[0]
        beam_energy = self.i_beam_energy.get()
        Object = self.i_Object.get()

        Material = os.path.splitext(self.i_material.get())[0]
        image_option = self.i_image_option.get()
        FWHM_detector = self.i_FWHM_detector.get()
        detector_pixel_size = self.i_detector_pixel_size.get()
        
        #try:
         #   resolution = self.i_resolution.get()
        #except:
         #   resolution = 1

        if Object == 'Sphere':
            radius = self.i_radius.get()
            x_shift =  self.i_xshift.get() 
            y_shift =  self.i_yshift.get()
            MyObject1 = obj.Sphere(n, radius, pixel_size, Material, DSO, x_shift, y_shift)
        
        elif Object == 'Cylinder':
            outer_radius = self.i_radius.get()
            inner_radius = self.i_inner_radius.get()
            x_shift =  self.i_xshift.get() 
            y_shift =  self.i_yshift.get()
            Orientation = self.i_orientation.get()
            MyObject1 = obj.Cylinder(n, outer_radius, inner_radius, Orientation, pixel_size, Material, DSO, x_shift, y_shift)
        
        if Beam_Spectrum == 'Monoenergetic':
            Beam_Spectrum = 'Mono'
       
        MySource = source.Source((FWHM_source, FWHM_source),Beam_Spectrum, beam_energy, Beam_Shape, pixel_size)
        MyDetector = detector.Detector(image_option, detector_pixel_size, FWHM_detector, 'gaussian', pixel_size)
        MyGeometry = geom.Geometry(DSO+DOD)

        #PSF_source = MySource.Source_PSF((n,n), M)

        Sample = [MyObject1]

        Intensity = exp.Experiment_Inline(n, MyGeometry, MySource, MyDetector, Sample)
        
        
        self.Plot_Figure(self.i_results_frame, Intensity,0,0, (3,3), 'Inline Simulation')
        bt1 = wg.create_button(self.i_results_frame, 'Save Image', 1,0, command=  lambda : self.save_image(Intensity))
  
    def RunCheckTL(self):

        n = self.c_n.get()
        pixel_size = self.c_pixel_size.get() #um
        FWHM_source = self.c_FWHM_source.get()
        Energy = self.c_energy.get() #keV
        Period = self.c_period.get() # um
        DC = self.c_DC.get()
        Material = self.c_material.get()
        bar_height = self.c_bar_height.get()
        multiples = self.c_multiple.get()#Multiples of Talbot Distance defined as Dt = 2*p**2/wavelength
        iterations = self.c_iterations.get()
        grating_option = self.c_grating_def.get()
        wavelength = 1.23984193/(1000*Energy) # in um

        MySource = source.Source((FWHM_source, FWHM_source),'Mono', Energy, 'Plane', pixel_size)
        
        if grating_option == 'Custom':
            grating_type = 'custom'
            title = 'Custom Grating'
        elif grating_option == 'Phase pi':
            grating_type = 'phase_pi'
            bar_height = None
            Material = None
            title = 'pi-phase Grating'
        elif grating_option == 'Phase pi/2':
            grating_type = 'phase_pi_2'
            bar_height = None
            Material = None
            title = 'pi/2-phase Grating'

        Intensities= check_Talbot.Talbot_carpet(n, MySource, Period, DC, multiples, iterations, grating_type,pixel_size, Energy, material=Material, grating_height= bar_height)

        
        
        self.Plot_check_TL(self.c_results_frame, Intensities, 0, 0, (3,3), title, multiples, n)
        bt1 = wg.create_button(self.c_results_frame, 'Save Image', 1,0, command=  lambda : self.save_image(Intensities))

    

    def RunTL(self):
        n = self.TL_n.get()
        pixel_size = self.TL_pixel_size.get()
        FWHM_source = self.TL_FWHM_source.get()
        Beam_Shape = self.TL_BeamShape.get()
        Beam_Spectrum = os.path.splitext(self.TL_Beam_Spectrum.get())[0]
        design_energy = self.TL_beam_energy.get()

        DSG1 = self.TL_DSO.get() #Distance source-object in cm, 15 cm Experimento.   16.69 con 23 keV y 6 um de periodo
        DOG1 = self.TL_DOG1.get() # Object-G1 distance in cm
        object = self.TL_Object.get()
        radius = self.TL_radius.get()
        inner_radius = self.i_inner_radius.get()
        material= os.path.splitext(self.TL_material.get())[0]
        Period_G1 = self.TL_Period_G1.get()
        G1_Phase = self.TL_G1_Phase.get()
        FWHM_detector = self.TL_resolution.get()
        detector_pixel_size = self.TL_detector_pixel_size.get()
        xshift = self.TL_xshift.get()
        yshift = self.TL_yshift.get()
        image_option = self.TL_image_option.get()
        angle = 0


        Objects=[]
        if Beam_Spectrum == 'Monoenergetic':
            Beam_Spectrum = 'Mono'
        if G1_Phase == 'Phase pi/2':
            G1_type = 'phase_pi_2'
        elif G1_Phase == 'Phase pi':
            G1_type = 'phase_pi'

        MySource = source.Source((FWHM_source, FWHM_source),Beam_Spectrum, design_energy, Beam_Shape, pixel_size)
        mean_energy = MySource.mean_energy
        mean_wavelength = 1.23984193/(mean_energy*1000)
        MyDetector = detector.Detector(image_option, detector_pixel_size, FWHM_detector, 'gaussian', pixel_size)

        configuration = TL_CONFIG(Design_energy = design_energy, G1_Period = Period_G1, DSG1=DSG1, Movable_Grating = self.TL_MovableGrating.get(),
                                G1_type = G1_type, TL_multiple = self.TL_TLmultiple.get(), 
                                Number_steps = self.TL_steps.get(), Step_length = self.TL_step_length.get(), pixel_size = pixel_size, angle = 0, resolution = FWHM_detector, 
                                pixel_detector = detector_pixel_size)


        if object == 'Sphere':
            object1 = obj.Sphere(n, radius, pixel_size, material, DSG1-DOG1, xshift,yshift)
        
        elif object == 'Cylinder':
            orientation = self.TL_orientation.get()
            object1 = obj.Cylinder(n, radius, inner_radius,orientation,pixel_size, material, DSO = DSG1-DOG1, x_shift_px=xshift, y_shift_px=yshift)
            
        Objects=[object1]
        
        pixel_size = configuration.pixel_size
        geometry = geom.Geometry()  
        distance, G2Period = geometry.calculate_Talbot_distance_and_G2period(MySource, configuration)
        geometry.DSD  = DSG1+distance
        configuration.G2_Period = G2Period

        G1 = obj.Grating(n , Period_G1, 0.5, pixel_size, 'Si', DSG1, grating_type = G1_type, design_energy = design_energy)
        G2 = obj.Grating(n , G2Period, 0.5, pixel_size, 'Au', DSG1+distance, 40,grating_type = 'custom', design_energy = design_energy)

        i, ir = exp.Experiment_Phase_Stepping(n, MyDetector, MySource, geometry, Objects, G1, G2, configuration, padding = 0)
    
        self.Plot_Modulation_Curve(self.TL_results_frame, i, ir, 0, 0, (3,3), 'Phase Stepping Curve', columnspan=2)
        self.Plot_Figure(self.TL_results_frame, i[0,:,:], 1, 0, (3,3), 'One Projection', columnspan=2)
        bt1 = wg.create_button(self.TL_results_frame, 'Save Stack Object Images', 2,0, command=  lambda : self.save_stack_image(i))
        bt2 = wg.create_button(self.TL_results_frame, 'Save Stack Reference Images', 2,1, command=  lambda : self.save_stack_image(ir))

        #DPC, Phase, At, Transmission, DF = DPC_Retrieval(ib, ibr, G2Period, DSO, distance,0,mean_energy)

    def modify_DOD(self, event):
        DSO = self.TL_DSO.get()
        Period_G1 = self.TL_Period_G1.get()
        Talbot_multiple = self.TL_TLmultiple.get()
        FWHM_source = self.TL_FWHM_source
        Spectrum = os.path.splitext(self.TL_Beam_Spectrum.get())[0]
        energy = self.TL_beam_energy.get()
        pixel_size = self.TL_pixel_size
        G1_Phase = self.TL_G1_Phase.get()
        Beam_Shape = self.TL_BeamShape.get()

        if Spectrum == 'Monoenergetic':
            Spectrum = 'Mono'

        Source = source.Source((FWHM_source, FWHM_source),Spectrum, energy, Beam_Shape, pixel_size)
       
        mean_energy = Source.mean_energy
        mean_wavelength = 1.23984193/(mean_energy*1000)
        
        if Beam_Shape == 'Conical':
            if G1_Phase == 'Phase pi':
            
                distance_Talbot = Period_G1**2/(8*mean_wavelength)*10**(-4)
                distance = DSO*Talbot_multiple*distance_Talbot/(DSO-Talbot_multiple*distance_Talbot)
                M = (DSO+distance)/DSO
                G2Period =Period_G1*M/2 # pi
            if G1_Phase == 'Phase pi/2':
                distance_Talbot = Period_G1**2/(2*mean_wavelength)*10**(-4) #pi/2
                distance = DSO*Talbot_multiple*distance_Talbot/(DSO-Talbot_multiple*distance_Talbot)
                M = (DSO+distance)/DSO
                G2Period =Period_G1*M # pi/2

        if Beam_Shape == 'Plane': 
            M =1
            if G1_Phase == 'Phase pi':
                G2Period = Period_G1/2
                distance = Period_G1**2/(8*mean_wavelength)*10**(-4)
                distance_Talbot = distance
            if G1_Phase == 'Phase pi/2':
                G2Period = Period_G1
                distance = Period_G1**2/(2*mean_wavelength)*10**(-4)
                distance_Talbot = distance

        self.TL_Talbot_distance.set(distance_Talbot)
        self.TL_Period_G2.set(G2Period)
        self.TL_DOD.set(distance)
        self.TL_M.set(M)

    def modify_TL_dist(self, event):
        
        Period_G1 = self.c_period.get()

        energy = self.c_energy.get()
        grating = self.c_grating_def.get()
        mean_wavelength = 1.23984193/(energy*1000)
        
        if grating == 'Absorption':
            G2Period = Period_G1
            distance = 2*Period_G1**2/(mean_wavelength)*10**(-4)
            distance_Talbot = distance

        elif grating == 'Phase pi':
            G2Period = Period_G1/2
            distance = Period_G1**2/(8*mean_wavelength)*10**(-4)
            distance_Talbot = distance
        elif grating == 'Phase pi/2':
            G2Period = Period_G1
            distance = Period_G1**2/(2*mean_wavelength)*10**(-4)
            distance_Talbot = distance

        self.c_Talbot_distance.set(distance_Talbot)
        #self.c_Period_G2.set(G2Period)



    def Plot_Modulation_Curve(self, frame, image, image_reference,row, column, figsize, title, columnspan=1):
        plt.close()
        params = {"text.color" : "white",
          "xtick.color" : "white",
          "ytick.color" : "white",
          "axes.labelcolor": "white",
          "axes.grid": True,
          "legend.labelcolor": 'black'}
        plt.rcParams.update(params)
        plt.tight_layout()

        fig=Figure(figsize=figsize)
        fig.set_facecolor("#333333")
        ax = fig.add_subplot(1,1,1)
        
        im = ax.plot(image[:, image.shape[1]//2, image.shape[2]//2], color = 'red', label='Object')
        im = ax.plot(image_reference[:, image_reference.shape[1]//2, image_reference.shape[2]//2], color='blue', label='Reference')
        ax.legend()
        ax.set_title(title)
        ax.set_xlabel('Phase Stepping')
        #plt.show()
        canvas1 = FigureCanvasTkAgg(fig, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=row, column=column,columnspan=columnspan,ipadx=90, ipady=20)
        #toolbarFrame1 = tk.Frame(master=frame)
        #toolbarFrame1.grid(row=row+1,column=column)

    def Plot_check_TL(self, frame, image, row, column, figsize, title, multiples, n):
        plt.close()
        params = {"text.color" : "white",
          "xtick.color" : "white",
          "ytick.color" : "white",
          "axes.grid": False,
          "axes.labelcolor": "white"}
        plt.rcParams.update(params)
        plt.tight_layout()

        fig=Figure(figsize=figsize)
        fig.set_facecolor("#333333")
        ax = fig.add_subplot(1,1,1)
        
        im = ax.imshow(image,"gray",interpolation='none', extent=[0,multiples,n,0], aspect='auto')
        ax.set_title(title)
        ax.set_xlabel('Multiples of Talbot distance')
        fig.colorbar(im,ax=ax)
        #plt.show()
        canvas1 = FigureCanvasTkAgg(fig, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=row, column=column, ipadx=90, ipady=20)
        #toolbarFrame1 = tk.Frame(master=frame)
        #toolbarFrame1.grid(row=row+1,column=column)
    
    def initialize_Figure(self, frame, figsize, row, column):

        fig = Figure(figsize = figsize)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        fig.set_facecolor("#333333")

        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, ipadx=60, ipady=50)


    def Plot_Figure(self, frame, image, row, column, figsize, title, columnspan=1):
        plt.close()
        params = {"text.color" : "white",
          "xtick.color" : "white",
          "ytick.color" : "white",
          "axes.grid": False,
          "axes.labelcolor": "white"}
        plt.rcParams.update(params)
        plt.tight_layout()

        fig=Figure(figsize=figsize)
        fig.set_facecolor("#333333")
        ax = fig.add_subplot(1,1,1)
        
        im = ax.imshow(image,"gray")
        ax.set_title(title)
        fig.colorbar(im,ax=ax)
        #plt.show()
        canvas1 = FigureCanvasTkAgg(fig, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=row, column=column, columnspan=columnspan, ipadx=90, ipady=20)
        toolbarFrame1 = tk.Frame(master=frame)
        toolbarFrame1.grid(row=row+1,column=column)

    def open_params(self):

        global params_window
        params_window = tk.Toplevel()
        params_window.title("Object Parameters")

        paramsFrame = ttk.Frame(params_window)
        paramsFrame.grid(row=0, column=0, sticky="ns")
        
        if self.i_Object.get() == 'Sphere':
            radiusL,_ = wg.create_label_entry(paramsFrame, "Radius (micrometer):", 0, 0,textvariable=self.i_radius)
            xshiftL,_ = wg.create_label_entry(paramsFrame, "X-direction shift (pixels):", 1, 0,textvariable=self.i_xshift)
            yshiftL,_ = wg.create_label_entry(paramsFrame, "Y-direction shift (pixels):", 2, 0,textvariable=self.i_yshift)

        elif self.i_Object.get() == 'Cylinder':
            ORIENTATION_OPTIONS = ['Horizontal', 'Vertical']
            radiusL,_ = wg.create_label_entry(paramsFrame, "Outer radius (micrometer):", 0, 0,textvariable=self.i_radius)
            IradiusL,_ = wg.create_label_entry(paramsFrame, "Inner radius (micrometer):", 1, 0,textvariable=self.i_inner_radius)
            xshiftL,_ = wg.create_label_entry(paramsFrame, "X-direction shift (pixels):", 2, 0,textvariable=self.i_xshift)
            yshiftL,_ = wg.create_label_entry(paramsFrame, "Y-direction shift (pixels):", 3, 0,textvariable=self.i_yshift)
            orientationL,_ = wg.create_label_combobox(paramsFrame, 'Orientation', ORIENTATION_OPTIONS, 4,0,textvariable=self.i_orientation)
            
        
        materialL,_ = wg.create_label_file_combobox(paramsFrame,'Material', os.path.join(self.parent_path, 'Resources','complex_refractive_index'),5,0, self.i_material)
        

        ApplyButton = wg.create_button(paramsFrame, 'Apply Changes', 9,0 ,padx = 20, pady= 10, command = self.apply_changes)
        
    def apply_changes(self):
        params_window.destroy()

    def open_params_TL(self):
        global params_window
        params_window = tk.Toplevel()
        params_window.title("Object Parameters")
        paramsFrame = ttk.Frame(params_window)
        paramsFrame.grid(row=0, column=0, sticky="ns")

        if self.TL_Object.get() == 'Sphere':
            radiusL,_ = wg.create_label_entry(paramsFrame, "Radius (micrometer):", 0, 0,textvariable=self.TL_radius)
            xshiftL,_ = wg.create_label_entry(paramsFrame, "X-direction shift (pixels):", 1, 0,textvariable=self.TL_xshift)
            yshiftL,_ = wg.create_label_entry(paramsFrame, "Y-direction shift (pixels):", 2, 0,textvariable=self.TL_yshift)
        elif self.TL_Object.get() == 'Cylinder':
            ORIENTATION_OPTIONS = ['Horizontal', 'Vertical']
            radiusL,_ = wg.create_label_entry(paramsFrame, "Outer radius (micrometer):", 0, 0,textvariable=self.TL_radius)
            radiusL,_ = wg.create_label_entry(paramsFrame, "Inner radius (micrometer):", 1, 0,textvariable=self.TL_inner_radius)
            xshiftL,_ = wg.create_label_entry(paramsFrame, "X-direction shift (pixels):", 2, 0,textvariable=self.TL_xshift)
            yshiftL,_ = wg.create_label_entry(paramsFrame, "Y-direction shift (pixels):", 3, 0,textvariable=self.TL_yshift)
            orientationL,_ = wg.create_label_combobox(paramsFrame, 'Orientation', ORIENTATION_OPTIONS, 4,0,textvariable=self.TL_orientation)

        materialL,_ = wg.create_label_file_combobox(paramsFrame,'Material', os.path.join(self.parent_path, 'Resources','complex_refractive_index'),5,0, self.TL_material)
        ApplyButton = wg.create_button(paramsFrame, 'Apply Changes', 9,0 ,padx = 20, pady= 10, command = self.apply_changes)

    def save_image(self, data):
        files = [('All Files', '*.*'), 
                    ('Python Files', '*.py'),
                    ('HDF5 File', '*.hdf5'),
                    ('Tiff File', '*.tif')]
        file = asksaveasfilename(filetypes = files, defaultextension = '.tif')
            #file = asksaveasfilename()
        if not file: 
            return
        
        im = Image.fromarray(data)
        sv = im.save(file)

    def save_stack_image(self, data):
        files = [('All Files', '*.*'), 
                    ('Python Files', '*.py'),
                    ('HDF5 File', '*.hdf5'),
                    ('Tiff File', '*.tif')]
        file = asksaveasfilename(filetypes = files, defaultextension = '.tif')
            #file = asksaveasfilename()
        if not file: 
            return
        
        data = np.stack(data, axis =0)
        tifffile.imwrite(file, data.astype(np.float32), photometric='minisblack')
        #imageio.volwrite(file,im)
        