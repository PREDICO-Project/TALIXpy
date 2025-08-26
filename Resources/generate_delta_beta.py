import numpy as np
import csv
# delta = na*re*wavelength**2/2pi * f1
# beta = na*re*wavelength**2/2pi * f2

# na = density * Na / Ma
# re = 2.8179403x10−15 m
import os

current_path = os.path.dirname(__file__)
path_form_factors = os.path.join(current_path,'form_factors')
Na = 6.02214129*10**(23)
re = 2.8179403*10**(-15) * 100 # cm

for file in os.listdir(path_form_factors):
    try:

        # Find Elemnt or Compound name
        filename = os.path.basename(file)
        element_name = os.path.splitext(filename)[0]

        # Search the Element or Compound name in Elements.csv
        with open(os.path.join(current_path,'Elements.csv')) as element_csv:
            csvFile = csv.reader(element_csv)
            
            for row in csvFile:
                #print(row[2])
                try:
                    if row[2] == element_name:
                        # Retrieve density of the element in g/cm3
                        density = float(row[4])
                        # Retrieve molar mass 
                        Ma = float(row[3])
                                
                except:
                    continue
        # Open element text file to search form factors (f1 and f2) and energies
        data = np.loadtxt(os.path.join(path_form_factors, file))

        energy = data[:,0]
        
        print(Ma, density) 
        #wavelength =data[:, 7]/(1E7) #cm
        wavelength = 1.23984193/(energy * 1000) / 10000 # cm
        #wavelength = np.reshape(wavelength, (1,energy_shape[0]))

        delta = data[:,1] * density * Na * wavelength**2 * re / (Ma * 2 * np.pi)
        delta = delta.reshape(-1, 1)

        #beta = data[:,2] * density * Na * wavelength**2 * re / (Ma * 2 * np.pi)
        beta = data[:,5] * density* wavelength / (4 *np.pi)
        beta = beta.reshape(-1, 1)
        
        energy = energy.reshape(-1, 1)
        xy=np.concatenate((energy,delta, beta),axis=1)
        
        np.savetxt(os.path.join(current_path,'complex_refractive_index',filename), xy)
    except:
        continue


