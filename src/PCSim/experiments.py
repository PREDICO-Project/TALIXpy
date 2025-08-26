import numpy as np
import matplotlib.pyplot as plt
import src.PCSim.Objects as obj
import src.PCSim.propagation as prop
import src.PCSim.utils as utils
import src.PCSim.material as mat
import cv2
from scipy.ndimage.interpolation import rotate
from tqdm import tqdm

#import threading

def Experiment_Inline(n, Geometry, Source, Detector,Objects, padding = 0):
    
    energies = Source.energies
    energy_weights = Source.intensities
    
    # First Check the Magnification of the object at the detector plane
    if Source.Beam_distribution == "Conical":
        conical = True
        #M = Geometry.calculate_magnification(distance1, distance2, conical)
    elif Source.Beam_distribution == "Plane": 
        conical = False
        #M =1
    else:
        print("Error in Beam_distribution definition: use 'Plane' or 'Conical'")

    
    z_det = Geometry.DSD

    if z_det <= 0:
        raise ValueError("Source-Detector distance must be > 0.")
    
    Objects_sorted = sorted(Objects, key=lambda x: float(getattr(x, "DSO", 0.0)))

    if len(Objects_sorted) > 0:
        z_ref = Objects_sorted[0].DSO  
    else:
        raise ValueError("No object is defined.")

    px_ref = Source.pixel_size  # Pixel size at the beginning (source plane)
 

    Intensity = np.zeros((n,n), dtype = float)
    
    
    for i, energy in enumerate(tqdm(energies, desc="Energies")):
        w = energy_weights[i]
        u = np.ones((n, n), dtype=np.complex128)

        
        z_prev = Objects_sorted[0].DSO
        px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_prev, conical)

        # Apply transmission function
        T0 = Objects_sorted[0].transmission_function(energy, px)
        u *= T0

        #plt.imshow(np.abs(u))
        #plt.show()
        for obj in Objects_sorted[1:]:
            z_next = obj.DSO
            dz = z_next - z_prev
            M = Geometry.calculate_magnification(z_prev, z_next, conical)
            if dz > 0:
                # Propagate 
                u = prop.propagate(u, px, dz/M, energy, padding= padding)
                # Update sampling
                px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_next, conical)

            # Apply transmission at z_next
            Tn = obj.transmission_function(energy, px)
            u *= Tn
            z_prev = z_next

       
        dz = z_det - z_prev
    
        M = Geometry.calculate_magnification(z_prev, z_det, conical)
        if dz > 0:
            # Propagate with sampling of the last object plane
            u = prop.propagate(u, px, dz/M, energy, padding= padding)
            px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_det, conical)

        # Intensity on detector
        I = np.abs(u) ** 2

        Intensity += I * (energy_weights[i])
    px_det = Geometry.pixel_size_at_distance(px_ref, z_ref, z_det, conical)
    M_global = Geometry.calculate_magnification(z_ref, z_det, conical)

    if M == 1:
        M_source = 1
    else:
        M_source = M_global-1
    Intensity = Source.PSF_blurr(Intensity, current_pixel_size=px_det, Magnification=M_source)


    if Detector.Image_option == 'Realistic':
        Intensity = Detector.applyDetector(Intensity, current_pixel_size=px_det)

    return Intensity    

def Experiment_Phase_Stepping(n, Detector, Source, Geometry, Objects, G1, G2, TL_CONFIG, padding = 0):

    Energies = Source.energies
    energy_weights = Source.intensities

    Objects.append(G1)

    steps = TL_CONFIG.Number_steps
    Movable_Grating = TL_CONFIG.Movable_Grating # 'G1' or 'G2'
    pixel_size = TL_CONFIG.pixel_size
    step_length = TL_CONFIG.Step_length 

    z_G1 = G1.DSO
    
    if Source.Beam_distribution == "Conical":
        conical = True
    elif Source.Beam_distribution == "Plane":
        conical = False
    else:
        print("Error in Beam_distribution definition: use 'Conical' o 'Plane'.")

    z_det = Geometry.DSD
    if z_det <= 0:
        raise ValueError("Source-Detector distance must be > 0.")
    
    Objects_sorted = sorted(Objects, key=lambda x: float(getattr(x, "DSO", 0.0)))

    if len(Objects_sorted) > 0:
        z_ref = Objects_sorted[0].DSO  
    else:
        raise ValueError("No object is defined.")
    
    z_ref = min(z_G1, Objects_sorted[0].DSO) # reference plane, G1 or the first Object

    px_ref = Source.pixel_size  # Pixel size at the beginning (source plane)
 
    images = []
    images_reference = []

    for N in tqdm(range(0,steps), desc='phase steps'):
        if Movable_Grating == 'G2':
            G2_step = N*step_length
            G1_step = 0
        if Movable_Grating == 'G1':
            G1_step = N*step_length
            G2_step = 0
        #print(G1_step, G2_step)
        G1.update_step(G1_step)
        G2.update_step(G2_step)

        I_obj = np.zeros((n, n), dtype=float)
        I_ref = np.zeros((n, n), dtype=float)
             
        for ie, energy in enumerate(Energies):
            w = energy_weights[ie]

            u = np.ones((n, n), dtype=np.complex128)
            z_prev = z_ref
            px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_prev, conical)

            u,z_prev, px, = Propagate_Objects(Objects_sorted, Geometry, energy, padding, px_ref, z_ref, conical) 

            if z_det > z_prev:
                dz = z_det - z_prev
                
                M = Geometry.calculate_magnification(z_prev, z_det, conical)
                u = prop.propagate(u, px, dz / M, energy, padding=padding)
                px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_det, conical)

            T_g2 = G2.transmission_function(energy, px)
            u *= T_g2

            I_obj += np.abs(u) ** 2 * w

            uR = np.ones((n, n), dtype=np.complex128)
            z_prev = z_ref
            pxR = Geometry.pixel_size_at_distance(px_ref, z_ref, z_prev, conical)
           
            dz = z_G1 - z_prev
            
            M = Geometry.calculate_magnification(z_prev, z_G1, conical)
            uR = prop.propagate(uR, pxR, dz / M, energy, padding=padding)
            pxR = Geometry.pixel_size_at_distance(px_ref, z_ref, z_G1, conical)
            z_prev = z_G1

            T_g1_R = G1.transmission_function(energy, pxR)
            
            uR *= T_g1_R

            if z_det > z_prev:
                dz = z_det - z_prev
                #print(dz)
                M = Geometry.calculate_magnification(z_prev, z_det, conical)
                uR = prop.propagate(uR, pxR, dz / M, energy, padding=padding)
                pxR = Geometry.pixel_size_at_distance(px_ref, z_ref, z_det, conical)
            T_g2_R = G2.transmission_function(energy, pxR)

            uR *= T_g2_R

            I_ref += np.abs(uR) ** 2 * w

        I_obj = Source.PSF_blurr(I_obj, current_pixel_size=px, Magnification=Geometry.calculate_magnification(z_ref, z_det, conical))
        I_ref = Source.PSF_blurr(I_ref, current_pixel_size=pxR, Magnification=Geometry.calculate_magnification(z_ref, z_det, conical))

        if Detector.Image_option == 'Realistic':
            print('Applying detector effects')
            px_det = Geometry.pixel_size_at_distance(px_ref, z_ref, z_det, conical)
            I_obj = Detector.applyDetector(I_obj, current_pixel_size=px_det)
            I_ref = Detector.applyDetector(I_ref, current_pixel_size=px_det)

        images.append(I_obj)
        images_reference.append(I_ref)

    images = np.asarray(images)
    images_reference = np.asarray(images_reference)
    return images, images_reference

def Propagate_Objects(Objects_sorted, Geometry, energy, padding,px_ref, z_ref, conical):

    u = np.ones((Objects_sorted[0].n, Objects_sorted[0].n), dtype=np.complex128)
    z_prev = float(z_ref)
    px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_prev, conical)

    for obj in Objects_sorted:
        z_obj = float(obj.DSO)

        if z_obj > z_prev:
            dz = z_obj - z_prev
            M  = Geometry.calculate_magnification(z_prev, z_obj, conical)
            u  = prop.propagate(u, px, dz / M, energy, padding=padding)
            px = Geometry.pixel_size_at_distance(px_ref, z_ref, z_obj, conical)
            z_prev = z_obj

        T = obj.transmission_function(energy, px)
        u *= T

    return u, z_prev, px


def Experiment_Phase_Stepping_test(n, Detector, Source, Geometry, Objects, G1, G2, TL_CONFIG, padding = 0):

    Energies = Source.energies
    energy_weights = Source.intensities


    steps = TL_CONFIG.Number_steps
    Movable_Grating = TL_CONFIG.Movable_Grating # 'G1' or 'G2'
    pixel_size = TL_CONFIG.pixel_size
    step_length = TL_CONFIG.Step_length 

    
    if Source.Beam_distribution == "Conical":
        conical = True
    elif Source.Beam_distribution == "Plane":
        conical = False
    else:
        print("Error in Beam_distribution definition: use 'Conical' o 'Plane'.")

    z_det = Geometry.DSD
    if z_det <= 0:
        raise ValueError("Source-Detector distance must be > 0.")
    
 
    images = []
    images_reference = []

    for N in tqdm(range(0,steps), desc='phase steps'):
        if Movable_Grating == 'G2':
            G2_step = N*step_length
            G1_step = 0
        if Movable_Grating == 'G1':
            G1_step = N*step_length
            G2_step = 0
        print(G1_step, G2_step)
        G1.update_step(G1_step)
        G2.update_step(G2_step)

        I_obj = np.zeros((n, n), dtype=float)
        I_ref = np.zeros((n, n), dtype=float)
               
        for energy in Energies: 
            transmission = np.ones((n,n), dtype=complex)
            
            for object in Objects:
                T = object.transmission_function(energy, pixel_size)
                transmission *= T
    
            
            trans_G1 = G1.transmission_function(energy,pixel_size)
            #plt.imshow(np.abs(trans_G1))
            #plt.colorbar()
            #plt.show()
            #G2 = obj.Grating(n, G2.period, G2.DC, G2.pixel_size, G2.thickness, G2.material, G2.step)

            trans_G2 = G2.transmission_function(energy,pixel_size)
        
            # Fresnel propagator
            #print('Propagation distance: '+str(distance/M))
            #g1 = prop.propagate(trans_G1, pixel_size, distance/M, energy)
            z_prev = G1.DSO
            dz = z_det - z_prev
            #print(dz)
            u = prop.propagate(trans_G1*transmission, pixel_size, dz, energy, padding=0)
            uG = prop.propagate(trans_G1, pixel_size, dz, energy, padding=0)

            #plt.imshow(uG.real)
            #plt.colorbar()
            #plt.show()   
            # G2 Transmission
            UObjG2 = (trans_G2*u)
            UG1G2 = (trans_G2*uG)

   
            # Detection
            I_obj += np.abs(UObjG2)**2     
            I_ref += np.abs(UG1G2)**2

            

        #intensity_reference_blur = utils.convolve(psf_detector, intensity_reference_blur)
        

        # Append the images for each phase step
        images.append(I_obj)
        images_reference.append(I_ref)

    images = np.asarray(images)
    images_reference = np.asarray(images_reference)

    return images, images_reference

    