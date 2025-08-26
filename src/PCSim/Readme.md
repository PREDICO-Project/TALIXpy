# NOT FINISHED

# PC Simulation
In this framework you can simulate the propagation of a wavefront and its detection.. The code is based on python libraries.

## Table Of Contents
* [Introduction](#Introduction)
* [Simulation Structure](#Simulation-Structure)
   * [X-Ray Beam](#X-Ray-Beam)
   * [Sample](#Sample)
   * [Propagation](#Propagation)
* [DPC Images](#DPC-Images)
* [Phase Image](#Phase-Image)
* [Data Folder](#Data-Folder)
* [Outputs](#Outputs)
* [How to run](#How-to-run)
* [Notebooks](#Notebooks)
* [Simple Numerical Simulation](#Simple-Numerical-Simulation)
* [Dependencies](#Dependencies)
* [References](#References)
* [Contact](#Contact)


## Introduction

X-ray Phase Contrast Imaging (PCI) has gained widespread popularity owing to its capacity to significantly enhance contrast in X-ray images of low atomic number (Z) materials. Multiple techniques exist for conducting PCI. In our study, we employ grating-based interferometry, specifically the Talbot-Lau interferometry technique, to achieve remarkable results in PCI.

## Simulation Structure
Here we summarize how the simulation is performed. The idea is to defined how the X-Ray beam interacts with the objects located between the source and the detector. All calculations are based on Fresnel diffraction (see Reference [1] for more information).

Reference [1]: Bartels, M. (2013). Cone-beam x-ray phase contrast tomography of biological samples. Göttingen Series in X-Ray Physics. https://doi.org/10.17875/gup2013-92

### X-Ray Beam
First, we need to define the X-Ray beam. Currently, we can only simulate either a Plane or Cone Beam. In the case of a Plane Beam, there will be no magnification. The beam's spectrum can be either monoenergetic or defined in a .txt file. This .txt file should be located in the 'Spectra' folder, with the first column representing energy in keV and the second column indicating intensity for each energy.

To facilitate this, we've created a class called **Beam** in [Spectra.py](PC/Spectra.py). This class precisely defines our X-Ray beam. In the following example, we will create a polychromatic spectrum using the file Mo_30kVp_spectrum.txt and shape it conically. For a monoenergetic beam, the energy value (in this case, 23 keV) must be explicitly specified.

```python
import Spectra
XRaySpectrum = Spectra.Beam('Mo_30kVp_spectrum', 23, 'Cone')
```

### Sample

The next thing is to create the object or objects located between the source and the detector. We have defined some classes for different objects in [Objects.py](PC/Objects.py). The way the object interacts with the X-Ray beam is with its transmission function, defined by its complex refractive index and by its geometry. 

The refractive index is defined as follows:

$$n = 1 - \delta + i\beta$$

We see that there is a real part of the refractive index and a imaginary part. The real part is related with the phase effects and the imaginary part is related with the attenuation effects. The transmission function is defined as:

$$T\left(x,y\right) = e^{-\mu\left(x,y\right)+i\Phi\left(x,y\right)}$$

We clearly see that there is a real and an imaginary part, the first will induce an attenuation and the second part will induce phase effects. We can relate this coefficients with the refractive index as:

$$\mu\left(x,y\right) = \frac{2\pi}{\lambda}\int{\beta\left(x,y\right)dl}$$

$$\Phi\left(x,y\right) = -\frac{2\pi}{\lambda}\int{\delta\left(x,y\right)dl}$$


In both equations, $\lambda$ is the wavelength of the X-Ray beam and the integral is the line integral along the optical path.  It's important to note that our simulation currently conducts this integral along the z-axis, rather than along the actual X-ray path. Nevertheless, it's worth mentioning that for X-ray projection, alternative libraries such as Astra can be utilized to achieve the desired results.

When multiple objects are introduced into the simulation, it's essential to understand that the transmission function of these objects is determined by the product of the transmission functions of the individual objects.

For example if you want to create a Sphere made of PMMA with a radius of 120 pixels and each pixel correspond to 1 $\mu m$:

```python
import Objects as obj
n = 1000 # Number of pixels in each direction
radius = 120 # Radius in pixels
pixels_size = 1 # um
material = 'PMMA'
x_shift = 0 # 0 == Centered
y_shift = 0 # 0 == Centered

Sphere = obj.Sphere(n,radius,pixel_size,material,x_shift, y_shift)

```

## Propagation

The most important thing is to apply the effects due to the propagation of the wavefront. We have defined the propagator as:

$$H\left(k\right)=e^{iz\sqrt{k^2-k^2_\perp}}$$

It is called free space propagator. Once the propagator is defined it's important to know how to apply this propagator to a wavefront. The way to do that is with the convolution. However, it is easier perform the propagation in the Fourier space as:

$$T_{prop} =F^{-1}\left[H\left(k\right)\cdot F\left[T\left(x,y\right)\right]\right]$$



## DPC Images

Once the sine function is retrieve, we can retrieve the DPC Images. Using the Talbot-Lau interferometer and the phase stepping method it is posible to obtain the Differential Phase Contrast Image, which contains the information about the Phase Gradient introduced by the object. It is also posible to obtain the Transmission image and the last Image is the Dark Field Image which is related to the scattering produced by microstructures. Here we have defined this images like:


$$ DPC = p_{obj}-p_r;\quad\quad
T = \frac{a_{0,obj}}{a_{0,r}};\quad\quad
DF = \frac{a_{1,obj}\cdot a_{{0,r}}}{a_{1,r}\cdot a_{0,obj}}$$

## Phase Image
In principle, it is possible to obtain the Phase Image from the DPC Image through a straightforward integration over the x-direction. However, certain artifacts, such as horizontal fringes, emerge due to noise and image imperfections. 

<p align="center">
 <img src="./Readme_Images/DPC.png" width="30%"></img>
 <img src="./Readme_Images/Phase_integration.png" width="30%"></img>
 <img src="./Readme_Images/Phase_wiener.png" width="30%"></img>
</p>



## Data Folder


## Outputs


## How to run

## Notebooks
There is a Jupyter Notebook into the [Notebooks Folder](Notebooks) with some useful examples.


## Dependencies

```
pip install -r requirements.txt
```

## References



## Contact
If there is any doubt please contact at the following e-mail: vicsan05@ucm.es


