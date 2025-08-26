import matplotlib.pyplot as plt
import numpy as np


def display_image(image, title=''):
    plt.imshow(image,"gray")
    plt.title(title)
    plt.colorbar()
    #plt.savefig(title+'.pdf', format='pdf', dpi=1200)
    plt.show()
    

def PlotProfile(image, title=''):
    x=np.linspace(0,len(image),len(image))
    plt.plot(x,image[len(image)//2,:])
    plt.title(title)
    plt.xlabel(u"\u03bcm")
    plt.ylabel("Intensty")
    plt.show()
    
