import tkinter
from tkinter import PhotoImage
import requests
import pandas
from PIL import Image, ImageTk
# lets create a tkinter window with a title "Kansas State University"
root = tkinter.Tk()
root.title("Kansas State University")
root.minsize(1200, 800)

# Load the logo image using Pillow for the icon
icon_image = Image.open("assets\logo.png")  # Update with the path to your logo file
icon_image = icon_image.resize((100, 100), Image.LANCZOS)  # Resize to a suitable icon size
icon_image = ImageTk.PhotoImage(icon_image)

# Load the logo image using Pillow
logo_image = Image.open("assets\logo.png")  # Update with the path to your logo file

# Resize the logo image to custom dimensions (e.g., 150x150 pixels)
logo_image = logo_image.resize((300, 150), Image.LANCZOS)  # Resize to desired dimensions
logo_image = ImageTk.PhotoImage(logo_image)
# Create a label to display the logo
logo_label = tkinter.Label(root, image=logo_image)
logo_label.pack()
# lets create a label with the text "Kansas State University"
label = tkinter.Label(root, text="Kansas State University")

# lets create a button with the text "Get Data"
button = tkinter.Button(root, text="Get Data")

# lets create a text box to display the data
text_box = tkinter.Text(root)

label = tkinter.Label(root, text="Kansas State University", font=("Helvetica", 24, "bold"), fg="purple")
label.pack()

label = tkinter.Label(root, text="Soil Micobial Agroecology Lab", font=("Helvetica", 18, "bold"))
label.pack()

root.mainloop()


