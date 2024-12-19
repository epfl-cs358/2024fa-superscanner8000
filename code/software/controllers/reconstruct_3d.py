import subprocess
import os
import cv2
import pathlib
import pycolmap
from controllers.open_mvs import open_mvs

class Reconstruct:

    def __init__(self, folder_path: pathlib.Path):
        self.folder_path = folder_path
        self.status = "Not started"

    # Open images in folder as array with cv2
    def open_images_in_folder(self):
        images = []
        for filename in os.listdir(self.folder_path):
            img = cv2.imread(os.path.join(self.folder_path, filename))
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                images.append(img)

        return images

    def save_images_to_folder(self, images):
        # save images to disk
        for i, img in enumerate(images):
            #print(f"Saving image {i}")
            path = self.folder_path / f"image_{i}.png"
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    def pre_process_images(self, scale_factor=1):
        images_path = self.folder_path / "images"
        database_path = self.folder_path / "database.db"
        
        if scale_factor != 1:
            self.status = "Resizing images"
            # Reduce image size by half
            images = self.open_images_in_folder()

            images = [cv2.resize(img, (0,0), fx=scale_factor, fy=scale_factor) for img in images]
            # Delete images folder
            os.system(f"rm -r {images_path}")
            os.mkdir(images_path)
            self.save_images_to_folder(images)

        self.status = "Extracting features"
        pycolmap.extract_features(database_path=database_path, image_path=images_path, camera_model="PINHOLE")
        self.status = "Matching features"
        pycolmap.match_exhaustive(database_path=database_path)

        if not os.path.exists(self.folder_path / "sparse"):
            os.mkdir(self.folder_path / "sparse")
        self.status = "Mapping"
        subprocess.call(["colmap", "mapper", "--database_path", database_path, "--image_path", images_path, "--output_path", self.folder_path / "sparse"])
        self.status = "Converting openMVS"
        subprocess.call(["colmap", "model_converter", "--input_path", self.folder_path / "sparse/0", "--output_path", self.folder_path / "sparse", "--output_type", "TXT"])

    def reconstruction_open_mvs(self, mvs_path: pathlib.Path, low_poly=False): 
        open_mvs_obj = open_mvs(mvs_path, self.folder_path)
        self.status="Interface COLMAP"
        open_mvs_obj.interface_colmap()
        self.status="Densifying Point Cloud"
        open_mvs_obj.densify_point_cloud()
        self.status="Reconstructing Mesh"
        open_mvs_obj.reconstruct_mesh()
        if low_poly:
            self.status="Refining Mesh"
            open_mvs_obj.refine_mesh()
        self.status="Texturing Mesh"
        open_mvs_obj.texture_mesh()
        self.status="Done"


if __name__ == "__main__":
    reconstructor = Reconstruct(pathlib.Path("temp/broom"))
    reconstructor.pre_process_images(scale_factor=0.5)
    reconstructor.reconstruction_open_mvs(pathlib.Path("../packages/openMVS/make/bin"), low_poly=True)