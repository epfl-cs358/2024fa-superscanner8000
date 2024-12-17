import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog  # For save dialog

from PIL import Image, ImageTk
import trimesh
from pythreejs import *
from IPython.display import display
import numpy as np
import shutil
import rerun as rr 
import tkinter.messagebox as messagebox
import os




class EndPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a container frame to center the content
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Add a label to display "Scan is finished"
        label = ttk.Label(self.container, text="Scan is Done YUPI", font=("Arial", 20))
        label.pack(pady=10)

        
         # Download button
        self.download_button = ttk.Button(self.container, text="Download Model", command=self.download_model)
        self.download_button.pack(pady=10)


          # Load the animated GIF
        self.gif_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'mission-accomplished-penguins.gif')
        self.gif = Image.open(self.gif_path)

       
        self.model_path = "/tmp/model.obj"  # Replace with your actual 3D model file path
        

        # Create a label to display the GIF
        self.gif_label = tk.Label(self.container)
        self.gif_label.pack(pady=20)

        self.preview_button = ttk.Button(self.container, text="Preview Model", command=self.open_preview_window)
        self.preview_button.pack(pady=10)

        

        # Start the GIF animation
        self.update_gif()



    def update_gif(self):
        """Update the gif by showing each frame."""
        try:
            # Get the next frame in the GIF
            self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            # If we reach the end of the GIF, restart from the first frame
            self.gif.seek(0)

        # Convert the current frame to a Tkinter-compatible image
        frame = ImageTk.PhotoImage(self.gif.convert("RGBA"))

        # Update the label with the new frame
        self.gif_label.config(image=frame)
        self.gif_label.image = frame  # Keep a reference to prevent garbage collection

        # Call this function again after 100ms to show the next frame
        self.after(100, self.update_gif)

    

    def open_preview_window(self):
        """Open a new window to preview the 3D model with vertex colors using rerun viewer."""
        try:
            # Initialize the rerun viewer
            rr.init("3D_Model_Preview", spawn=True)

            # Load the 3D model using trimesh
            mesh_or_scene = trimesh.load_mesh(self.model_path)

            # Check if the object is a Scene or a single Trimesh
            if isinstance(mesh_or_scene, trimesh.Scene):
                # Scene: Combine all geometries into a single set of vertices, faces, and colors
                all_vertices = []
                all_faces = []
                all_colors = []
                vertex_offset = 0  # Offset for face indices

                for name, geometry in mesh_or_scene.geometry.items():
                    if isinstance(geometry, trimesh.Trimesh):
                        all_vertices.append(geometry.vertices)
                        all_faces.append(geometry.faces + vertex_offset)

                        # Check for vertex colors; default to white if absent
                        if hasattr(geometry.visual, "vertex_colors") and geometry.visual.vertex_colors is not None:
                            all_colors.append(geometry.visual.vertex_colors[:, :3])  # Ignore alpha channel if present
                        else:
                            all_colors.append(np.ones_like(geometry.vertices) * 255)  # Default to white

                        vertex_offset += len(geometry.vertices)

                # Combine vertices, faces, and colors
                vertices = np.vstack(all_vertices)
                faces = np.vstack(all_faces)
                colors = np.vstack(all_colors) / 255.0  # Normalize to [0, 1] range
            else:
                # Single Trimesh object
                vertices = mesh_or_scene.vertices
                faces = mesh_or_scene.faces

                # Check for vertex colors; default to white if absent
                if hasattr(mesh_or_scene.visual, "vertex_colors") and mesh_or_scene.visual.vertex_colors is not None:
                    colors = mesh_or_scene.visual.vertex_colors[:, :3] / 255.0  # Normalize and remove alpha
                else:
                    colors = np.ones_like(vertices) * 1.0  # Default to white

            # Log the 3D mesh with vertex colors to the rerun viewer
            rr.log(
                "model_mesh",
                rr.Mesh3D(
                    vertex_positions=vertices,
                    triangle_indices=faces,
                    vertex_colors=colors
                )
            )

            # Notify the user that the model is being displayed
            print("3D model with vertex colors sent to Rerun Viewer.")
        except Exception as e:
            print(f"Error while opening the 3D model: {e}")

    def download_model(self):
        """Allow the user to choose a location to save the 3D model, default to Desktop."""
        try:
            # Get the path to the user's Desktop directory
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # Open a save dialog, starting at the Desktop directory
            save_path = filedialog.asksaveasfilename(
                defaultextension=".obj",
                filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")],
                initialdir=desktop_path,  # Set default directory to Desktop
                title="Save 3D Model As"
            )

            # If the user selects a location, copy the file
            if save_path:
                shutil.copy(self.model_path, save_path)
                print(f"Model saved to: {save_path}")
                messagebox.showinfo("Success", f"Model saved successfully to:\n{save_path}")
        except Exception as e:
            print(f"Error while saving the model: {e}")
            messagebox.showerror("Error", "Failed to save the model.")