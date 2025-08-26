
# PCI Simulation
In this framework you can simulate the propagation of a wavefront and its detection.. The code is based on python libraries.

## Table Of Contents
* [Introduction](#Introduction)
* [Simulation Structure](#Simulation-Structure)
   * [X-Ray Source](#X-Ray-Source)
   * [Sample](#Sample)
   * [Propagation](#Propagation)
   * [Experiments](#Experiments)
   * [Detector](#Detector)
* [Contact](#Contact)


## Introduction

X-ray Phase Contrast Imaging (PCI) has gained widespread popularity owing to its capacity to significantly enhance contrast in X-ray images of low atomic number (Z) materials. Multiple techniques exist for conducting PCI. In our study, we employ grating-based interferometry, specifically the Talbot-Lau interferometry technique, to achieve remarkable results in PCI.

## Simulation Structure
Here we summarize how the simulation is performed. The idea is to defined how the X-Ray beam interacts with the objects located between the source and the detector. All calculations are based on Fresnel diffraction (see Reference [1] for more information).

Reference [1]: Bartels, M. (2013). Cone-beam x-ray phase contrast tomography of biological samples. Göttingen Series in X-Ray Physics. https://doi.org/10.17875/gup2013-92

### X-Ray Source
The class **Source** manages all properties of the X-ray source.  
This includes defining its geometry (point, extended, microfocus), spatial distribution (plane or cone beam), and spectrum (monoenergetic or polychromatic).  


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
Sample = obj.Cylinder(n, outer_radius=300, inner_radius=50,Orientation='Vertical',pixel_size=pixel_size, material='PMMA', DSO = 10, x_shift_px=0, y_shift_px=0)

```

## Propagation

The most important thing is to apply the effects due to the propagation of the wavefront. We have defined the propagator as:

$$H\left(k\right)=e^{iz\sqrt{k^2-k^2_\perp}}$$

It is called free space propagator. Once the propagator is defined it's important to know how to apply this propagator to a wavefront. The way to do that is with the convolution. However, it is easier perform the propagation in the Fourier space as:

$$T_{prop} =F^{-1}\left[H\left(k\right)\cdot F\left[T\left(x,y\right)\right]\right]$$

## Experiments

The framework allows choosing between two experimental setups:

- **Inline (Propagation-Based Imaging, PBI)**  
  In this setup, the object is placed directly in the beam path, and the phase effects are revealed by free-space propagation before reaching the detector. No gratings are required, but the setup is highly sensitive to source coherence and distances. 

- **Phase Stepping (Talbot-Lau Interferometry)**  
  This setup uses a combination of gratings (G1, G2) to convert phase shifts into intensity modulations that can be retrieved by scanning one of the gratings (typically G2). Spatial coherence is assumed and G0 is not simulated.
  The phase stepping procedure allows separating **absorption**, **differential phase**, and **dark-field** signals.

Users can select the desired experiment through the **Experiments** module.

## Detector

The detector is responsible for recording the propagated intensity and downsampling the image to the physical detector pixel size,. In our framework, two main options are implemented:

- **Ideal Detector**  
  The detector directly samples the propagated intensity at the given pixel size, without convolution with the PSF of the detector or noise. This is useful for purely theoretical studies.

- **Realistic Detector**  
  Includes the effects of the point spread function (PSF) and optionally noise models (Poisson, Gaussian, etc.). This makes the simulation closer to experimental conditions.

The detector parameters (pixel size, PSF width, noise type) can be adjusted in the **Detector** class, allowing users to explore how detector performance influences image quality.

## Contact
If there is any doubt please contact at the following e-mail: vicsan05@ucm.es


