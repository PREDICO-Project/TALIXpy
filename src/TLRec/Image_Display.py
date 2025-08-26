import src.TLRec.utils as utils
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize, fftpack
import src.TLRec.Correction as Correction

def Pixel_intensity(images, G2period, Phase_Step, x_position, y_position,rec_type):
  #% Returns the pixel intensity in a determined position (*x_position*, *y_position*) for all the images recorded
  # In our case, each step is formed by 10 minor steps with a value of 20nm.
  (z,y,x) = images.shape
  step = 1
  number_data = int(z/step)
  #x_data = np.linspace(0,z,num= number_data, endpoint = True)/G2period*2*np.pi*spacing
  x_data = np.linspace(0,z,num= number_data, endpoint = True)/G2period*2*np.pi*Phase_Step
  y_data=images[:,y_position,x_position]
  x = np.linspace(0,x_data[-1],1000)
  
  if rec_type == 'FFT':
    xfreq = np.fft.fftfreq(z,1)*G2period/2/np.pi/Phase_Step
    spectrum = fftpack.fft(images[:,y_position,x_position])/z
    peaks = np.argmax(abs(spectrum[1:]))+1
    print(peaks)
    phase, module = utils.calculate_sine_parameters(spectrum)
    offset = np.amax(spectrum, axis=0).real
    y = (offset+module*np.cos(x*xfreq[peaks]*2*np.pi+phase))
  
  if rec_type == 'Fast_FFT':
    xfreq = np.fft.fftfreq(z,1)*G2period/2/np.pi/Phase_Step
    spectrum = fftpack.fft(y_data, axis=0)
    p = np.angle(spectrum[1])
    A = np.abs(spectrum[1]*2/z)
    c = np.sum(images[:,y_position,x_position])/z
    y = (c+A*np.cos(x*xfreq[1]*2*np.pi+p))

  if rec_type == 'least_squares':
    x_data = np.linspace(0,z,num= number_data, endpoint = True)*2*np.pi/z
    y_data=images[:,y_position,x_position]
    x = np.linspace(0,x_data[-1],1000)
    Matrix_A = np.vstack([np.ones(len(x_data)), np.cos(x_data), np.sin(x_data)]).T
    o, a, b = np.linalg.lstsq(Matrix_A, y_data,rcond=None)[0]
    y = o+a*np.cos(x)+b*np.sin(x)
    
  if rec_type == 'fast_lstsq':
    x_data = np.linspace(0,z,num= number_data, endpoint = True)*2*np.pi/z
    y_data=images[:,y_position,x_position]
    x = np.linspace(0,x_data[-1],1000)
    Matrix_A = np.vstack([np.ones(len(x_data)), np.cos(x_data), np.sin(x_data)]).T
    B = np.linalg.inv(Matrix_A.T@Matrix_A)
    C = B @ Matrix_A.T
    o, a, b = C@y_data
    y = o+a*np.cos(x)+b*np.sin(x)
  
  if rec_type == 'Step_correction':
    steps = np.arange(0,z,1)*2*np.pi/z
    error = np.zeros((1, z))
    new_errors = optimize.minimize(Correction.Improve_reconstruction_minimization_steps, error, Correction.calculate_C_matrix(images[:,y_position,x_position]))
    new_errors = new_errors.x
    step_errors = new_errors[0:z]
    
    A = np.ones((z, 3))
    new_steps = steps+step_errors
    A[:,1] = np.cos(new_steps)
    A[:,2] = np.sin(new_steps)
    o, a, b = np.linalg.lstsq(A, y_data,rcond=None)[0]
    y = o+a*np.cos(x)+b*np.sin(x)  
  return x_data, y_data, x, y

def Pixel_intensity_one_period(images, x_position, y_position,rec_type,Fourier=False):
  #% Returns the pixel intensity in a determined position (*x_position*, *y_position*) for all the images recorded
  # In our case, each step is formed by 10 minor steps with a value of 20nm.
  (z,y,x) = images.shape
  step = 1
  number_data = int(z/step)
  x_data = np.linspace(0,z,num= number_data, endpoint = True)*2*np.pi/z
  y_data=images[:,y_position,x_position]
  if rec_type == 'Fast_FFT':
    xfreq = np.fft.fftfreq(z,1)*z/2/np.pi
    spectrum = fftpack.fft(y_data, axis=0)
    p = np.angle(spectrum[1])
    A = np.abs(spectrum[1]*2/z)
    c = np.abs(spectrum[0]/z)
    x = np.linspace(0,x_data[-1],1000)
    y = (c+A*np.cos(x*xfreq[1]*2*np.pi+p))
  if rec_type == 'FFT':

    xfreq = np.fft.fftfreq(z,1)*z/2/np.pi
    spectrum = fftpack.fft(images[:,y_position,x_position])/z
    peaks = np.argmax(abs(spectrum[1:]))+1
    a = 2*spectrum[peaks].real
    b = 2*spectrum[peaks].imag
    # We set the values of the phase between -pi and +pi.
    if (a>0) and (b>0): 
      p = np.arctan(b/a)
    if (a<0) and (b>0): 
      p =np.arctan(b/a)-np.pi 
    if (a<0) and (b<0):
      p =np.arctan(b/a)+np.pi  
    if (a>0) and (b<0):
      p =np.arctan(b/a)
    A = np.sqrt(a**2+b**2)
    c = spectrum[0].real
    x = np.linspace(0,x_data[-1],1000)
    y = (spectrum[0].real+A*np.cos(x*xfreq[peaks]*2*np.pi+p))
    
    if Fourier:
        #If you want to check the Fourier Spectrum and see if there is just one intense frequency.
      plt.plot(xfreq,abs(spectrum.real),'o')
      plt.show()

  if rec_type == 'least_squares':
    
    Matrix_A = np.vstack([np.ones(len(x_data)), np.cos(x_data), np.sin(x_data)]).T
    o, a, b = np.linalg.lstsq(Matrix_A, y_data,rcond=None)[0]
    x=np.linspace(0,z,1000)*2*np.pi/z
    y = o+a*np.cos(x)+b*np.sin(x)
    
  if rec_type == 'fast_lstsq':
    x=np.linspace(0,z,1000)*2*np.pi/z
    Matrix_A = np.vstack([np.ones(len(x_data)), np.cos(x_data), np.sin(x_data)]).T
    B = np.linalg.inv(Matrix_A.T@Matrix_A)
    C = B @ Matrix_A.T
    o, a, b = C@y_data
    y = o+a*np.cos(x)+b*np.sin(x)
    
  if rec_type == 'Step_correction':
    steps = np.arange(0,images.shape[0],1)*2*np.pi/images.shape[0]
    error = np.zeros((images.shape[0]))
    new_errors = optimize.minimize(Correction.Improve_reconstruction_minimization_steps, error, Correction.calculate_C_matrix(images[:, y_position, x_position]))
    new_errors = new_errors.x
    step_errors = new_errors[0:images.shape[0]]
    A = np.ones((images.shape[0], 3))
    new_steps = steps+step_errors
    Matrix_A = np.vstack([np.ones(len(x_data)), np.cos(new_steps), np.sin(new_steps)]).T
    o, a, b = np.linalg.lstsq(Matrix_A, y_data,rcond=None)[0]
    x=np.linspace(0,z,1000)*2*np.pi/z
    y = o+a*np.cos(x)+b*np.sin(x)
    x_data = new_steps


  return x_data, y_data, x, y
