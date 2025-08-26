import numpy as np
import os
import matplotlib.pyplot as plt
def Simulation(Object, Phase_Steps, noise_mean, error_steps_mean, error_dose_mean, Moire = False, axis=1):
    '''
    Create the Curve Intensity Modulation for a given Object, Background and Grating.
    I(x,y,k)= exp(-error_Dose)*[a_0(x,y)+a_1(x,y)*cos(Phi(x,y)+2*pi*k/M+error_steps)] + noise
    k: k-th Phase Step
    M: Total Phase Steps
    '''
    n = Object.n
    #Final_Images = []
    #Final_Images_reference = []
    Images =np.zeros((Phase_Steps,n,n))
    Images_reference =np.zeros((Phase_Steps,n,n))  
    a0 = Object.a0_Distribution()
    Phase = Object.Obtain_Phase_Distribuction()
    Diff_Phase = Object.Obtain_Phase_Gradient(axis = axis)
    plt.imshow(Diff_Phase)
    plt.show()
    a1 = a0/2
    filename = 'log.txt'
    try:
        os.remove(filename)
    except:
        pass
    file = open('log.txt', 'a')
    file.write('lambda lambda_reference phase_step phase_step_reference\n')
    if Moire:
        moire_fringes = np.ones((n,n))
        for i in range(n):
            # Pretends to simulate the Moire fringes
            moire_fringes[:,i] = i
        number_fringes = 10
        c = 2*np.pi/n*number_fringes
        moire_fringes *=c
    else:
        moire_fringes = np.zeros((n,n))
    for i,phase_step in enumerate(range(Phase_Steps)):
        lambda_k_1 = np.random.normal(0,error_dose_mean)
        lambda_k_2 = np.random.normal(0,error_dose_mean)
        phase_step_error = np.random.normal(0,error_steps_mean)
        phase_step_error_r = np.random.normal(0,error_steps_mean)
        file = open('log.txt', 'a')
        file.write(f'{lambda_k_1:.5g} {lambda_k_2:.5g} {phase_step_error:.5g} {phase_step_error_r:.5g}\n')
        
        noise1 = np.random.normal(0,noise_mean, (n,n))
        noise2 = np.random.normal(0,noise_mean, (n,n))
        Images[phase_step, :,:] = np.exp(lambda_k_1)*(a0+a1*np.cos(Diff_Phase+2*np.pi*phase_step/Phase_Steps+phase_step_error+moire_fringes))+noise1
        Images_reference[phase_step,:,:] =np.exp(lambda_k_2)*(1+0.5*np.cos(2*np.pi*phase_step/Phase_Steps+phase_step_error_r+moire_fringes))+noise2
        
    #Images += noise1
    #Images_reference += noise2
    return Images, Images_reference


