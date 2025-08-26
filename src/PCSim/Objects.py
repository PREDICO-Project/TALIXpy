import numpy as np
from src.PCSim.material import make_material
from scipy.ndimage import rotate
import warnings
import matplotlib.pyplot as plt

class GeometricObject():
    def __init__(self, n, pixel_size, material, DSO,
                 x_shift_px=0, y_shift_px=0):
        self.n = int(n)
        self.pixel_size_init = float(pixel_size)
        self.material = material
        self.DSO = DSO
        self.x_shift_px = int(x_shift_px)
        self.y_shift_px = int(y_shift_px)

    

    def transmission_function(self, energy, pixel_size):
        """
        Compute complex transmission at the current plane sampling.

        Parameters
        ----------
        energy : float
            Photon energy (keV).
        pixel_size : float
            Current pixel size (same distance units as geometry; typically µm).

        Returns
        -------
        transmission : (n, n) complex ndarray
        """
        wavelength = 1.23984193 / (1000 * energy)  # µm
        k = 2.0 * np.pi / wavelength  # 1/µm

        refr_index_term = self.set_refr_index(energy)

        proj = self.make_geometry(self.n, pixel_size)

        refractive_index_projection = proj * refr_index_term
        transmission = np.exp(-1j * k * refractive_index_projection)
        return transmission

    def set_refr_index(self, energy):
        return make_material(self.material, energy)

    def make_geometry(self, n, pixel_size):
        raise NotImplementedError("Subclasses must implement make_geometry().")
        
class Sphere(GeometricObject):
    def __init__(self, n, radius, pixel_size, material, DSO, x_shift_px=0, y_shift_px=0):
        super().__init__(n, pixel_size, material, DSO, x_shift_px=x_shift_px, y_shift_px=y_shift_px)
        
        self.radius = float(radius)

    def make_geometry(self, n, pixel_size):

        y,x = np.mgrid[(-n-self.y_shift_px)//2 : (n-self.y_shift_px)//2, (-n-self.x_shift_px)//2 : (n-self.x_shift_px)//2]

        x = (x+0.5)*pixel_size 
        y = (y+0.5)*pixel_size

        r2 = x**2 + y**2
        R2 = self.radius ** 2
        thickness = np.zeros((n, n), dtype=float)
        inside = r2 < R2
        thickness[inside] = 2.0 * np.sqrt(np.maximum(R2 - r2[inside], 0.0))
        return thickness
       
class Wedge(GeometricObject):
    def __init__(self, n, width, thickness, pixel_size, material, DSO, x_shift_px=0, y_shift_px=0):
        super().__init__(n, pixel_size, material, DSO, x_shift_px=x_shift_px, y_shift_px=y_shift_px)
        
        self.width = width
        self.thickness = thickness
        
    def make_geometry(self, n, pixel_size):
        width = self.width
        thickness = self.thickness
        x_shift = self.x_shift_px
        y_shift = self.y_shift_px
        #It returns the thickness of the sphere in any point (valid with a parallel beam).
        y,x = np.mgrid[(-n-y_shift)//2 : (n-y_shift)//2, (-n-x_shift)//2 : (n-x_shift)//2]
        x = (x+0.5)*pixel_size 
        y = (y+0.5)*pixel_size
        image = np.zeros((n,n))

        half_width = width / 2
        wedge_mask = np.abs(x) < half_width
        image[wedge_mask] = (half_width-np.abs(x[wedge_mask]) / half_width * thickness)
        
        return image
        
               
class Cylinder(GeometricObject):
    def __init__(self, n, outer_radius, inner_radius,Orientation,pixel_size, material, DSO, x_shift_px=0, y_shift_px=0):
        super().__init__(n, pixel_size, material, DSO, x_shift_px=x_shift_px, y_shift_px=y_shift_px)
  
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.Orientation = Orientation

    def make_geometry(self, n, pixel_size):
        #It returns the thickness of the sphere in any point (valid with a parallel beam).
    
        x_shift = self.x_shift_px
        y_shift = self.y_shift_px
        outer_radius = self.outer_radius
        inner_radius = self.inner_radius
        Orientation = self.Orientation
        
        y,x = np.mgrid[(-n-y_shift)//2 : (n-y_shift)//2, (-n-x_shift)//2 : (n-x_shift)//2]
        x = (x+0.5)*pixel_size 
        y = (y+0.5)*pixel_size
        image = np.zeros((n,n))

        if Orientation == 'Vertical':
            r_sq = x**2
        elif Orientation == 'Horizontal':
            r_sq = y**2
        else:
            raise ValueError("Orientation must be 'Vertical' or 'Horizontal'.")
        
        mask_ext = r_sq < outer_radius**2

        if inner_radius == 0.:
            # Solid Cylinder
            image[mask_ext] = 2*np.sqrt(outer_radius**2 - r_sq[mask_ext])
        else:
            "Hollow cylinder"
            mask_int = r_sq < inner_radius**2
            mask_hollow = mask_ext & mask_int

            # Outer region
            image[mask_ext] = 2*np.sqrt(outer_radius**2 - r_sq[mask_ext])

            # Substract inner hollow region
            image[mask_hollow] -= 2*np.sqrt(inner_radius**2 - r_sq[mask_hollow])

            # Ensure no negative thickness
            image[image < 0 ] = 0

        return image
         
        
class Substrate():
    def __init__(self, n, pixel_size, thickness,material):
        self.n = n 
        self.pixel_size = pixel_size
        self.thickness = thickness
        self.material=material
        self.energy = 0
        self.refr_index = 0 # Refractive Index $n = \delta-i\beta$            
        self.object = self.make_substrate()
        
    def make_substrate(self):
            substrate = np.ones((self.n,self.n))
            return substrate*self.thickness        
        
class Grating(GeometricObject):
    def __init__(self, n, period, DC, pixel_size, material, DSO, thickness_um=None, grating_type='custom', angle = 0,x_shift_px=0, y_shift_px=0, step =0, design_energy=None):
        super().__init__(n, pixel_size, material, DSO, x_shift_px=x_shift_px, y_shift_px=y_shift_px)

        self.period = period
        self.DC = DC
        self.step = step
        self.grating_type = grating_type
        self.angle = angle
        self.design_energy = design_energy
        
        if thickness_um is not None:
            self.thickness = thickness_um
        else:
            self.thickness = self.calculate_thickness()

        self.check_grating_sampling()
        #self.projection = self.make_geometry()

        #self.object = self.movable_Grating()   

    def calculate_thickness(self):
        if self.grating_type in ['phase_pi', 'phase_pi_2']:
            if self.design_energy is None:
                raise ValueError("Design Energy must be specified for phase gratings.")
            
            wavelength = 1.23984193/(1000*self.design_energy) # in um
            refr_index = self.set_refr_index(self.design_energy)
            delta_phi_target = np.pi if self.grating_type == 'phase_pi' else np.pi/2
            k = 2*np.pi/wavelength
            thickness = delta_phi_target / (k * refr_index)
            return thickness
        else:
            raise ValueError("Unknown grating type")
        
    def make_geometry(self, n, pixel_size):
    
        period = self.period
        step = self.step
        DC = self.DC
        thickness = self.thickness
        # If you want a non-movable grating just 'step'=0.
        #% It returns the thickness of a grating which moves whith a determined step. 
        #% The step should be an integer, it is a step in the "pixel space".
        out_original = np.zeros((n, n))
        out = np.zeros((n, n))
        periodo = int(np.round(period / pixel_size)) #In pixels
        N=int(step/pixel_size) # step in pixels
        m=N/periodo
        not_zeros = int(DC * periodo)
        zeros = int((1-DC) * periodo)
        
        for i in range(-not_zeros,zeros):
            if i<0:
                i=i+periodo
                out_original[:,(i)::periodo] = 1
        for i in range(-not_zeros,zeros):
            if i<0:
                i=i+periodo
                out[:,(i+N)::periodo] = 1        
        for i in range(0,N):
            #out[:,N-i]=out_original[:,-(i+periodo//2)]
            out[:,i] = out_original[:,-i]

        thickness_gr = out*thickness
        if self.angle != 0:
            
            pad_pixels = int(np.ceil(np.sqrt(2) * n - n) / 2)
            thickness_gr = np.pad(thickness_gr, ((pad_pixels,pad_pixels),(pad_pixels,pad_pixels)), 'wrap')
            thickness_gr = rotate(thickness_gr, self.angle, reshape=False)
            #plt.imshow(thickness_gr)
            #plt.show()
            thickness_gr = thickness_gr[pad_pixels:pad_pixels+n, pad_pixels:pad_pixels+n]

        return  thickness_gr

    def update_step(self, new_step):
        self.step = new_step
        self.projection = self.make_geometry(self.n, self.pixel_size_init)

    def get_Talbot_distance(self):
        wavelength = 1.23984193/(1000*self.design_energy)
        Talbot_distance = (2*self.period**2/ wavelength) * 10**(-4) #cm
        return Talbot_distance

    def check_grating_sampling(self):
        """
        Sampling condition for gratings. To avoid aliasing, 5-6 pixel per period are recommended, but not strictly necessary.
        """
        if self.pixel_size_init > self.period/6:
            warnings.warn(f"[Grating sampling warning] Pixel size ({self.period:.3g}) may be too large compared to grating period ({self.period:.3g}). Please consider to reduce the pixel size or increase the grating period.")


        