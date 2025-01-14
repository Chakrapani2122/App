import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import requests
import re
import xml.etree.ElementTree as ET
from base64 import b64encode
from PIL import Image, ImageTk
from datetime import datetime
import pytz

# Load users from users.xml
def load_users():
    tree = ET.parse('users.xml')
    root = tree.getroot()
    users = {}
    for user in root.findall('user'):
        username = user.find('username').text
        first_name = user.find('first_name').text
        last_name = user.find('last_name').text
        password = user.find('password').text
        role = user.find('role').text
        university = user.find('university').text
        users[username] = {
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'university': university
        }
    return users

users = load_users()

def validate_login():
    username = username_entry.get()
    password = password_entry.get()

    # Check if user exists in users.xml
    if username not in users or users[username]['password'] != password:
        messagebox.showerror("Invalid Login", "Invalid username or password.")
        return

    # If validation passes
    messagebox.showinfo("Login Successful", f"Welcome {users[username]['first_name']} {users[username]['last_name']}!")
    show_user_page(username)

def show_user_page(username):
    # Clear the login widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Add image and text
    image = Image.open("assets/logo.png")  # Replace with the path to your image
    image = image.resize((200, 100), Image.LANCZOS)  # Resize the image to medium size
    photo = ImageTk.PhotoImage(image)

    image_label = tk.Label(root, image=photo, bg="#f0f0f0")
    image_label.image = photo  # Keep a reference to avoid garbage collection
    image_label.pack(pady=(20, 5))

    title_label = tk.Label(root, text="Kansas State University", font=("Helvetica", 16), fg="purple", bg="#f0f0f0")
    title_label.pack(pady=(5, 20))

    welcome_label = tk.Label(root, text=f"Welcome {users[username]['first_name']} {users[username]['last_name']}!", font=("Helvetica", 16), bg="#f0f0f0")
    welcome_label.pack(pady=20)

    role_label = tk.Label(root, text=f"Role: {users[username]['role']}", font=("Helvetica", 12), bg="#f0f0f0")
    role_label.pack(pady=5)

    university_label = tk.Label(root, text=f"University: {users[username]['university']}", font=("Helvetica", 12), bg="#f0f0f0")
    university_label.pack(pady=5)

    folder_label = tk.Label(root, text="Select a folder:", font=("Helvetica", 12), bg="#f0f0f0")
    folder_label.pack(pady=10)

    folder_var = tk.StringVar(root)
    folder_var.set("Select Folder")  # default value

    folder_dropdown = tk.OptionMenu(root, folder_var, "Forage", "Soil Fertility", "Soil Moisture", "Soil health", "Summer Crops")
    folder_dropdown.config(font=("Helvetica", 12))
    folder_dropdown.pack(pady=10)

    description_label = tk.Label(root, text="File Description:", font=("Helvetica", 12), bg="#f0f0f0")
    description_label.pack(pady=10)
    description_entry = tk.Text(root, font=("Helvetica", 12), bd=2, relief="groove", height=5, width=40)
    description_entry.pack(pady=10)

    upload_button = tk.Button(root, text="Upload Files", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=lambda: upload_files(folder_var.get(), description_entry.get("1.0", tk.END).strip(), username))
    upload_button.pack(pady=20)

def upload_files(selected_folder, description, username):
    files = filedialog.askopenfilenames()
    if not files:
        return

    if not description:
        messagebox.showerror("Error", "File description is required.")
        return

    token = simpledialog.askstring("GitHub Token", "Please enter your GitHub personal access token:", show='*')
    if not token:
        messagebox.showerror("Error", "GitHub personal access token is required.")
        return

    repo_owner = 'Chakrapani2122'
    repo_name = 'Data'

    # Get current time in CST
    cst = pytz.timezone('US/Central')
    current_time = datetime.now(cst).strftime('%Y-%m-%d %H:%M:%S %Z')

    for file_path in files:
        with open(file_path, 'rb') as file:
            content = b64encode(file.read()).decode('utf-8')
            file_name = file_path.split('/')[-1]
            file_path = f"{selected_folder}/{file_name}"
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

            commit_message = f"Uploaded by {username} on {current_time}\n\n{description}"

            data = {
                "message": commit_message,
                "content": content
            }

            try:
                # Check if the file already exists
                get_response = requests.get(api_url, headers={
                    'Authorization': f'token {token}',
                    'Content-Type': 'application/json'
                })

                if get_response.status_code == 200:
                    file_data = get_response.json()
                    data['sha'] = file_data['sha']  # Include the sha value if the file exists

                response = requests.put(api_url, json=data, headers={
                    'Authorization': f'token {token}',
                    'Content-Type': 'application/json'
                })

                if response.status_code in [200, 201]:
                    messagebox.showinfo("Success", f"File {file_name} uploaded successfully to GitHub repository in folder {selected_folder}!")
                else:
                    error_data = response.json()
                    messagebox.showerror("Error", f"There was an error uploading your file: {error_data.get('message', 'Unknown error')}")
            except Exception as e:
                messagebox.showerror("Error", f"There was an error uploading your file: {str(e)}")

root = tk.Tk()
root.title("Login")

# Adjust window size to display size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.4)
window_height = int(screen_height * 0.5)
root.geometry(f"{window_width}x{window_height}+{int(screen_width * 0.3)}+{int(screen_height * 0.3)}")

# Set background color
root.configure(bg="#f0f0f0")

# Add image and text
image = Image.open("assets/logo.png")  # Replace with the path to your image
image = image.resize((200, 100), Image.LANCZOS)  # Resize the image to medium size
photo = ImageTk.PhotoImage(image)

image_label = tk.Label(root, image=photo, bg="#f0f0f0")
image_label.pack(pady=(20, 5))

title_label = tk.Label(root, text="Kansas State University", font=("Helvetica", 16), fg="purple", bg="#f0f0f0")
title_label.pack(pady=(5, 20))

# Create login card
card_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
card_frame.pack(pady=20, padx=20, fill="both", expand=True)

username_label = tk.Label(card_frame, text="Username:", font=("Helvetica", 12), bg="white")
username_label.pack(pady=10)
username_entry = tk.Entry(card_frame, font=("Helvetica", 12), bd=2, relief="groove")
username_entry.pack(pady=10)

password_label = tk.Label(card_frame, text="Password:", font=("Helvetica", 12), bg="white")
password_label.pack(pady=10)
password_entry = tk.Entry(card_frame, show='*', font=("Helvetica", 12), bd=2, relief="groove")
password_entry.pack(pady=10)

login_button = tk.Button(card_frame, text="Login", font=("Helvetica", 12), bg="#4CAF50", fg="white", bd=2, relief="groove", command=validate_login)
login_button.pack(pady=20)

root.mainloop()