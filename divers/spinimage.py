from PIL import Image

# Create an Image object from an Image

colorImage = Image.open("./Vaisseau.png")

# Rotate it by 45 degrees
dico={}
for i in range(int(360/10)):
    dico[i] = colorImage.rotate(i)
for i in dico:
    dico[i].save('Vaisseau_'+str(i)+".png")
