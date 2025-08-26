'''
Script to run the Graphical User Interface (GUI)
'''


import tkinter as tk
from tkinter import ttk
from GUI.PCSim_gui import PCSim_gui
from GUI.styles import Styles as stl


'''def launch_TLRec_GUI():
    new_window = tk.Toplevel()
    new_window.title("TLRec")
    app = TLRec_GUI(new_window)

def launch_PhaseContrast_Sim_GUI():
    new_window = tk.Toplevel()
    new_window.title("PC Sim")
    app = PCSim_gui(new_window)'''

def quit():
    root.quit()   # stops mainloop
    root.destroy()
        
def create_main_menu():
    
    global root
    root = tk.Tk()
    root.title("Talbot Lau Environment")
    #root.configure(background='gray20')
    #root.state('zoomed')

    main_frame = ttk.Frame(root, style='TFrame')

    main_frame.pack(fill=tk.BOTH, expand=True)
    stl.configure_style()
    PCSim_gui(main_frame)
    #wg.create_button(main_frame,"TLRec",0,1,padx=50, command=launch_TLRec_GUI )
    #wg.create_button(main_frame,"Phase Contrast Simulation",1,1,padx=50, command=launch_PhaseContrast_Sim_GUI)
    
    root.protocol("WM_DELETE_WINDOW", quit)

    root.mainloop()

if __name__ == "__main__":
    create_main_menu()