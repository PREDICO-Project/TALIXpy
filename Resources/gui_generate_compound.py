import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import sys, os
from tkinter.filedialog import asksaveasfilename
from generate_compounds import generate_refrative_index_compound


current_path = os.path.dirname(__file__)
print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))) # FIX IT


from GUI.styles import Styles as stl
from GUI.widgets import Widget as wg

aux_text = r""" 
    The complex refractive index is defined as:

    $n = 1 - \delta + i\beta$ 
        
    These components can be calculated through 
    the atomic scattering factors:
    
    $\delta = \frac{n_a\cdot r_e\cdot \lambda^2}{2\pi}f_1$

    $\beta = \frac{n_a\cdot r_e\cdot \lambda^2}{2\pi}f_2$

    Atomic scattering factors are obtained from:

    https://physics.nist.gov/PhysRefData/FFast/html/form.html

    $\beta$ is calculated from the attenuation coefficient.

    $\beta = \frac{\mu \lambda}{4\pi}$


    """
aux_text1 = r""" Text File with the Energy (keV), $\delta$ and $\beta$ is 
created in **complex_refractive_index** folder"""

def quit():
    root.quit()   # stops mainloop
    root.destroy()

def run():
    data, filename = generate_refrative_index_compound(compound.get(), density.get(), name.get())
    save_file(data)


def save_file(data):
    files = [('All Files', '*.*'), 
            ('Text Files', '*.txt'),]
    file = asksaveasfilename(filetypes = files, defaultextension = '.txt')
    #file = asksaveasfilename()
    if not file: 
        return
      
    current_path = os.path.dirname(__file__)
    np.savetxt(file, data)

def create_main_menu():
    font = {'family': 'serif',
        'color':  'lightgray',
        'weight': 'normal',
        'size': 10,
        }
    global root, compound, density, name
    

    root = tk.Tk()
    root.title("Calculate complex refractive index")
    #root.configure(background='gray20')
    #root.state('zoomed')

    # Variable Initialization
    compound = tk.StringVar()
    density = tk.DoubleVar()
    name = tk.StringVar()

    main_frame = ttk.Frame(root, style='TFrame')

    main_frame.pack(fill=tk.BOTH, expand=True)
    
    stl.configure_style()
    #wg.create_button(main_frame,"TLRec",0,1,padx=50, command=launch_TLRec_GUI )
    #wg.create_button(main_frame,"Phase Contrast Simulation",1,1,padx=50, command=launch_PhaseContrast_Sim_GUI)
    

    wg.create_label_entry(main_frame, 'Introduce Chemical formulation (eg H20, SiO3...)', 0, 0, textvariable=compound)
    #wg.create_label_entry(main_frame, 'Introduce name (Optional eg Water)', 1, 0, textvariable=name)
    wg.create_label_entry(main_frame, 'Introduce density of the compound (g/cm3)', 2, 0, textvariable=density)

    wg.create_button(main_frame, 'Run & Save' ,4, 0, command = run)
    
    fig_text = Figure(figsize=(5,4))
    fig_text.set_facecolor("#333333")
    canvas = FigureCanvasTkAgg(fig_text, main_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row = 6, column = 0, columnspan=3)
    text = fig_text.text(0.5, 0.5,aux_text, ha='center', va='center',  fontdict=font)
    canvas.figure = fig_text
    canvas.draw()
    wg.create_button(main_frame, 'Exit', 5, 0, command = quit)

    root.protocol("WM_DELETE_WINDOW", quit)

    root.mainloop()

if __name__ == "__main__":
    create_main_menu()