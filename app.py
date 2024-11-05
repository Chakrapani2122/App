import tkinter
from tkinter import PhotoImage
import requests
import pandas
from PIL import Image, ImageTk
import re
def validate_login():
    email = email_entry.get()
    password = password_entry.get()

    # Email validation using regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        return

    # Password validation
    if len(password) < 10:
        messagebox.showerror("Invalid Password", "Password must be at least 10 characters long.")
        return
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        messagebox.showerror("Invalid Password", "Password must contain letters, numbers, and special characters.")
        return

    # If validation passes
    messagebox.showinfo("Login Successful", "You have logged in successfully!")


# lets create a tkinter window with a title "Kansas State University"
root = tkinter.Tk()
root.title("Kansas State University")
root.minsize(1000, 800)

# Load the logo image using Pillow for the icon
icon_image = Image.open(r"assets\logo.png")  # Update with the path to your logo file
icon_image = icon_image.resize((300, 150), Image.LANCZOS)  # Resize to a suitable icon size
icon_image = ImageTk.PhotoImage(icon_image)
root.iconphoto(False, icon_image)

# Load the logo image using Pillow
logo_image = Image.open(r"assets\logo.png")  # Update with the path to your logo file

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


email_label = tkinter.Label(root, text="Email ID:", font=("Helvetica", 12))
email_label.place(relx=0.5, y=350, anchor='center')  # Center the email label
email_entry = tkinter.Entry(root, width=30)
email_entry.place(relx=0.5, y=370, anchor='center')  # Center the email entry

# Create a label and entry for Password
password_label = tkinter.Label(root, text="Password:", font=("Helvetica", 12))
password_label.place(relx=0.5, y=400, anchor='center')  # Center the password label
password_entry = tkinter.Entry(root, show="*", width=30)
password_entry.place(relx=0.5, y=420, anchor='center')  # Center the password entry

# Create a login button
login_button = tkinter.Button(root, text="Login", command=validate_login)
login_button.place(relx=0.5, y=450, anchor='center')
root.mainloop()


