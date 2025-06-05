#!/usr/bin/env python3
"""
Polaroid Photo App
A simple GUI application that transforms regular photos into polaroid-style images.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os

class PolaroidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Polaroid Photo Creator")
        self.root.geometry("800x600")
        
        # Variables
        self.original_image = None
        self.polaroid_image = None
        self.preview_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="Select Photo", command=self.select_photo).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Create Polaroid", command=self.create_polaroid).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(control_frame, text="Save Image", command=self.save_image).grid(row=0, column=2, padx=(0, 10))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Polaroid Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Border size
        ttk.Label(settings_frame, text="Border Size:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.border_size = tk.IntVar(value=50)
        ttk.Scale(settings_frame, from_=20, to=100, variable=self.border_size, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Bottom border multiplier
        ttk.Label(settings_frame, text="Bottom Border:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.bottom_multiplier = tk.DoubleVar(value=2.5)
        ttk.Scale(settings_frame, from_=1.5, to=4.0, variable=self.bottom_multiplier, orient=tk.HORIZONTAL).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Vintage effect intensity
        ttk.Label(settings_frame, text="Vintage Effect:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.vintage_intensity = tk.DoubleVar(value=0.3)
        ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=self.vintage_intensity, orient=tk.HORIZONTAL).grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Add shadow effect
        self.add_shadow = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Add Shadow", variable=self.add_shadow).grid(row=6, column=0, sticky=tk.W)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Canvas for image preview
        self.canvas = tk.Canvas(preview_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars for canvas
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
    
    def select_photo(self):
        """Open file dialog to select a photo"""
        filetypes = [
            ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif *.tiff'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select a photo",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.original_image = Image.open(filename)
                self.show_preview(self.original_image)
                messagebox.showinfo("Success", "Photo loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def create_polaroid(self):
        """Transform the image into a polaroid style"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please select a photo first!")
            return
        
        try:
            # Create polaroid effect
            self.polaroid_image = self.apply_polaroid_effect(self.original_image)
            self.show_preview(self.polaroid_image)
            messagebox.showinfo("Success", "Polaroid effect applied!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create polaroid: {str(e)}")
    
    def apply_polaroid_effect(self, image):
        """Apply polaroid-style border and vintage effects"""
        # Resize image to reasonable size while maintaining aspect ratio
        max_size = 800
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Get settings
        border = self.border_size.get()
        bottom_mult = self.bottom_multiplier.get()
        vintage = self.vintage_intensity.get()
        
        # Calculate dimensions
        img_width, img_height = image.size
        bottom_border = int(border * bottom_mult)
        
        # Create new image with borders (white background)
        polaroid_width = img_width + (border * 2)
        polaroid_height = img_height + border + bottom_border
        polaroid = Image.new('RGB', (polaroid_width, polaroid_height), 'white')
        
        # Apply vintage effect to original image
        vintage_image = self.apply_vintage_effect(image, vintage)
        
        # Paste the image centered horizontally, with border at top
        x_offset = border
        y_offset = border
        polaroid.paste(vintage_image, (x_offset, y_offset))
        
        # Add shadow effect if enabled
        if self.add_shadow.get():
            polaroid = self.add_shadow_effect(polaroid)
        
        return polaroid
    
    def apply_vintage_effect(self, image, intensity):
        """Apply vintage color effect"""
        if intensity == 0:
            return image
        
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Reduce saturation for vintage look
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1 - intensity * 0.3)
        
        # Slightly reduce contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1 - intensity * 0.2)
        
        # Add slight yellow tint
        if intensity > 0.2:
            # Create yellow overlay
            overlay = Image.new('RGB', image.size, (255, 255, 200))
            image = Image.blend(image, overlay, intensity * 0.1)
        
        # Add slight blur for softer look
        if intensity > 0.5:
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def add_shadow_effect(self, image):
        """Add a subtle drop shadow"""
        # Create shadow
        shadow_offset = 10
        shadow_blur = 15
        
        # Create shadow image
        shadow = Image.new('RGBA', 
                          (image.width + shadow_offset * 2, 
                           image.height + shadow_offset * 2), 
                          (0, 0, 0, 0))
        
        # Create shadow shape
        shadow_img = Image.new('RGBA', image.size, (0, 0, 0, 100))
        shadow.paste(shadow_img, (shadow_offset, shadow_offset))
        
        # Blur shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
        
        # Create final image
        final = Image.new('RGB', shadow.size, 'white')
        final.paste(shadow, (0, 0), shadow)
        final.paste(image, (0, 0))
        
        return final
    
    def show_preview(self, image):
        """Display image in the canvas"""
        # Calculate preview size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # Canvas not initialized yet
            self.root.after(100, lambda: self.show_preview(image))
            return
        
        # Scale image to fit canvas while maintaining aspect ratio
        img_copy = image.copy()
        img_copy.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.preview_image = ImageTk.PhotoImage(img_copy)
        
        # Clear canvas and add image
        self.canvas.delete("all")
        img_width, img_height = img_copy.size
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def save_image(self):
        """Save the polaroid image"""
        if not self.polaroid_image:
            messagebox.showwarning("Warning", "Please create a polaroid first!")
            return
        
        filetypes = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Save polaroid image",
            defaultextension=".png",
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Convert to RGB if saving as JPEG
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    rgb_image = Image.new('RGB', self.polaroid_image.size, 'white')
                    rgb_image.paste(self.polaroid_image, mask=self.polaroid_image if self.polaroid_image.mode == 'RGBA' else None)
                    rgb_image.save(filename, 'JPEG', quality=95)
                else:
                    self.polaroid_image.save(filename)
                
                messagebox.showinfo("Success", f"Image saved as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")

def main():
    root = tk.Tk()
    app = PolaroidApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()