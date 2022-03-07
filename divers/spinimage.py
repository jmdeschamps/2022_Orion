from PIL import Image
import math

# Create an Image object from an Image

colorImage = Image.open("./Vaisseau.png")

# Rotate it by 45 degrees
dico={}
for i in range(int(360/36)):
    print(i*36)
    im = colorImage.rotate(i*36)
    #im.show()
    dico[i]=im
for i in dico:
    dico[i].save('Vaisseau_'+str(10*i)+".png")
