from tkinter import ttk
import tkinter as tk
import os

class Widget:

    @staticmethod
    def create_frame(master, text, row, column, padx=10, pady=5, sticky="ew", font=("Arial", 12), background="#ffffff"):
        # Crear un estilo personalizado
        style_name = "Custom.TLabelframe"
        style = ttk.Style()
        style.configure(style_name, font=font, background=background)

     
        frame = ttk.LabelFrame(master, text=text, style=style_name)
        frame.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        return frame

    @staticmethod
    def create_label_entry(master, label_text, row, column, padx=10, pady=5, textvariable=None, width_entry=10, state='normal'):
       
        label = ttk.Label(master, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")

        entry = ttk.Entry(master, textvariable=textvariable, width=width_entry,state=state)
        entry.grid(row=row, column=column+1, padx=padx, pady=pady, sticky="w")

        return label, entry
    
    @staticmethod
    def create_entry(master, row, column, padx=10, pady=5,columnspan=1):
    
        entry = ttk.Entry(master, justify='center')
        entry.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady)

        return entry
    
    @staticmethod
    def create_button(master, button_text, row, column, padx=10, pady=5,columnspan=1, state = "normal", command=None):
       
        button = ttk.Button(master, text=button_text ,state = state, command=command)
        button.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady)

        return button
    
    @staticmethod
    def create_label(master, text, row, column, sticky="w", padx=10, pady=5, columnspan=1):
       
        label = ttk.Label(master, text=text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky, columnspan=columnspan)
        return label

    @staticmethod
    def create_checkbox(master, text, row, column, variable=False, sticky="w", padx=10, pady=5, command=None):
     
        checkbox = ttk.Checkbutton(master, text=text, variable=variable, command = command)
        checkbox.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        return checkbox

    
    @staticmethod
    def create_label_combobox(master, label_text, names, row, column, textvariable=None,state="readonly"):
        
        # Label
        label = ttk.Label(master, text=label_text)
        label.grid(row=row, column=column, padx=10, pady=5, sticky="w")

        # Combobox
        combobox = ttk.Combobox(master, values=names, textvariable=textvariable,state=state)
        combobox.grid(row=row, column=column+1, padx=10, pady=5, sticky="ew")

        return label, combobox

    @staticmethod
    def create_text_area(master, row, column, height=10, width=50, padx=20, pady=20, wrap=tk.WORD):
     
        
        text_area = tk.Text(master, height=height, width=width, wrap=wrap, padx=padx, pady=pady,
                            background="gray12", foreground="white", font=('Comic Sans', 10), borderwidth=1)
        text_area.grid(row=row, column=column, sticky="nsew")
        text_area.configure(state="disabled")
        
        return text_area

    @staticmethod
    def create_label_file_combobox(master, label_text, directory_path, row, column, combobox_textvariable=None, state="readonly", file_extension="all", distribution='horizontal'):
        """
        Create a combobox and its label. The values of the combobox will be the files inside directory_path.
        """
        label = ttk.Label(master, text=label_text)
        label.grid(row=row, column=column, padx=10, pady=5, sticky="w")

        if combobox_textvariable is None:
            combobox_textvariable = tk.StringVar(master)

      
        if file_extension == "all":
            file_names = sorted([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])
        else:
            file_names = sorted([f for f in os.listdir(directory_path) if f.endswith('.' + file_extension) and os.path.isfile(os.path.join(directory_path, f))])
        file_names.insert(0,'None')
    
        
        combobox = ttk.Combobox(master, textvariable=combobox_textvariable, values=file_names, state=state)
        combobox.grid(row=row, column=column+1, padx=10, pady=5, sticky="ew")

        return label, combobox