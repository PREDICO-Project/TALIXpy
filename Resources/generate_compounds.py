import numpy as np
import os
import csv



def generate_refrative_index_compound(compound, density, name = None):
    Na = 6.02214129*10**(23)
    re = 2.8179403*10**(-15) * 100 # cm
    current_path = os.path.dirname(__file__)
    path_index = os.path.join(current_path,'form_factors')
    final_energies = np.linspace(1, 150, 500)
    elements_count = parse_compound_formula(compound)
    f1 = 0
    f2 = 0
    mu = 0
    Ma = 0
    
    for key, value in elements_count.items():
        
        element = np.loadtxt(os.path.join(path_index,key+'.txt'))
        
        f1_element =  element[:,1]
        f2_element =  element[:,2]
        mu_element = element[:,5]
        
        original_energies = element[:,0]

        f1_elements_interpolated = interpolate_f(original_energies, f1_element, final_energies)
        f2_elements_interpolated = interpolate_f(original_energies, f2_element, final_energies)
        mu_element_interpolated = interpolate_f(original_energies, mu_element, final_energies)

        with open(os.path.join(current_path,'Elements.csv')) as element_csv:
            csvFile = csv.reader(element_csv)
            for row in csvFile:
                try:
                    if row[2] == key:
                        density_element = float(row[4])
                        Ma_element = float(row[3])                    
                except:
                    continue
        
        f1 += value * f1_elements_interpolated
        f2 += value * f2_elements_interpolated
        mu += value * Ma_element* mu_element_interpolated 
        Ma += value * Ma_element

    wavelength = 1.23984193/(final_energies * 1000) / 10000

    compound_delta = f1 * density * Na * wavelength**2 * re / (Ma * 2 * np.pi)
    compound_delta = compound_delta.reshape(-1, 1)
    compound_beta = mu * density* wavelength / (Ma*4 *np.pi)
    compound_beta = compound_beta.reshape(-1, 1)
    final_energies = final_energies.reshape(-1, 1)
    xy=np.concatenate((final_energies,compound_delta, compound_beta),axis=1)

    if name is None:
        name = compound
    #print(os.path.join(current_path,'complex_refractive_index',name+'.txt'))

    return xy, name

def save_file(file, filename):
    current_path = os.path.dirname(__file__)
    np.savetxt(os.path.join(current_path,'complex_refractive_index',filename+'.txt'), file)

def parse_compound_formula(compound):
    mp = {}
 
    i = 0
    while i < len(compound):
        count = 0
        c = compound[i]
        if c.isupper():
            a = ""
            a += c
            j = i + 1
            while j < len(compound):
                d = compound[j]
                if d.islower():
                    a += d
 
                    if a not in mp:
                        mp[a] = 1
                    else:
                        mp[a] += 1
                    count = 1
                elif d.isdigit():
                    k = int(d)
                    mp[a] = k
                    count = 1
                else:
                    i = j - 1
                    break
                j += 1
            if count == 0:
                if a not in mp:
                    mp[a] = 1
                else:
                    mp[a] += 1
        i += 1
    return mp

def interpolate_f(original_energies, f_element, final_energies):

    f_element_interpolated = []

    for energy in final_energies:

        pos = closest_to(original_energies, energy)
        initial_energy = original_energies[pos]

        if initial_energy == energy:
            f_energy = f_element[pos]
            
        if initial_energy < energy:
            f_energy = linear_interpolation(energy, initial_energy, original_energies[pos+1], f_element[pos], f_element[pos+1])
            
        if initial_energy > energy:
            f_energy = linear_interpolation(energy, initial_energy, original_energies[pos-1], f_element[pos], f_element[pos-1])
        
        f_element_interpolated.append(f_energy)
    
    f_element_interpolated = np.asarray(f_element_interpolated)

    return f_element_interpolated


def closest_to(list, value):
    # It returns the position of the closest value in a list to the reference value
    list = np.asarray(list)
    position = (np.abs(list-value)).argmin()
    return position

def linear_interpolation(x,x0,x1,y0,y1):
    # Linear interpolation to obtain delta and beta values from the txt file
    y = y0+(y1-y0)*(x-x0)/(x1-x0)
    return y

if __name__ == '__main__':
    compound = 'C8H8'
    density = 1.06 # hay que meterlo como input
    file, filename = generate_refrative_index_compound(compound, density)
    save_file(file, filename)
