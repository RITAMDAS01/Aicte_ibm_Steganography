import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Encoding function
def encode_message(img, msg, password):
    d = {chr(i): i for i in range(255)}
    m, n, z = 0, 0, 0

    # Store message length in first 10 pixels
    msg_length = len(msg)
    for i in range(10):
        img[n, m, z] = (msg_length >> (i * 8)) & 255  # Store length byte-by-byte
        z = (z + 1) % 3
        if z == 0:
            m += 1
            if m >= img.shape[1]:
                m = 0
                n += 1

    # Encode message
    for char in msg:
        if n >= img.shape[0] or m >= img.shape[1]:  
            messagebox.showerror("Error", "Message too long for this image!")
            return None

        img[n, m, z] = d[char]
        z = (z + 1) % 3
        if z == 0:
            m += 1
            if m >= img.shape[1]:
                m = 0
                n += 1

    return img


# Decoding function
def decode_message(img, password, input_pass):
    if password != input_pass:
        messagebox.showerror("Error", "Incorrect Passcode!")
        return "Unauthorized Access"

    c = {i: chr(i) for i in range(255)}
    message = ""
    m, n, z = 0, 0, 0

    # Read message length from first 10 pixels
    msg_length = 0
    for i in range(10):
        msg_length |= (img[n, m, z] << (i * 8))
        z = (z + 1) % 3
        if z == 0:
            m += 1
            if m >= img.shape[1]:
                m = 0
                n += 1

    # Decode message
    for _ in range(msg_length):
        message += c[img[n, m, z]]
        z = (z + 1) % 3
        if z == 0:
            m += 1
            if m >= img.shape[1]:
                m = 0
                n += 1

    return message


# GUI Application
class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography")
        self.root.geometry("600x500")
        self.image_path = None
        self.password = ""

        # UI Components
        tk.Label(root, text="Image Steganography", font=("Arial", 16, "bold")).pack(pady=10)

        self.img_label = tk.Label(root, text="No Image Selected", bg="gray", width=50, height=10)
        self.img_label.pack(pady=10)

        tk.Button(root, text="Select Image", command=self.load_image).pack(pady=5)

        tk.Label(root, text="Secret Message:").pack()
        self.msg_entry = tk.Entry(root, width=50)
        self.msg_entry.pack()

        tk.Label(root, text="Passcode:").pack()
        self.pass_entry = tk.Entry(root, width=20, show="*")
        self.pass_entry.pack()

        tk.Button(root, text="Encrypt & Save", command=self.encrypt).pack(pady=5)
        tk.Button(root, text="Decrypt", command=self.decrypt).pack(pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.bmp")])
        if file_path:
            self.image_path = file_path
            img = Image.open(self.image_path)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img, text="")
            self.img_label.image = img

    def encrypt(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return
        
        img = cv2.imread(self.image_path)
        msg = self.msg_entry.get()
        self.password = self.pass_entry.get()

        if not msg or not self.password:
            messagebox.showerror("Error", "Message and passcode cannot be empty!")
            return

        encrypted_img = encode_message(img, msg, self.password)
        if encrypted_img is not None:
            output_path = "encryptedImage.png"
            cv2.imwrite(output_path, encrypted_img)
            messagebox.showinfo("Success", f"Message encrypted! Image saved as {output_path}")
            os.system(output_path)

    def decrypt(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return

        img = cv2.imread(self.image_path)
        input_pass = self.pass_entry.get()
        msg_length = len(self.msg_entry.get())  

        message = decode_message(img, self.password, input_pass)
        messagebox.showinfo("Decryption", f"Decrypted Message: {message}")

# Run the application
root = tk.Tk()
app = SteganographyApp(root)
root.mainloop()
