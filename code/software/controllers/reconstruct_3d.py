import subprocess
import os
import cv2
import pathlib
import pycolmap
from open_mvs import open_mvs


# Open images in folder as array with cv2
def open_images_in_folder(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        img = cv2.imread(os.path.join(folder_path, filename))
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)

    return images

def save_images_to_folder(images, folder_path: pathlib.Path):
    # save images to disk
    for i, img in enumerate(images):
        #print(f"Saving image {i}")
        path = folder_path / f"image_{i}.png"
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

def pre_process_images(project_path: pathlib.Path, scale_factor=1):
    images_path = project_path / "images"
    database_path = project_path / "database.db"

    if scale_factor != 1:

        # Reduce image size by half
        images = open_images_in_folder(images_path)

        images = [cv2.resize(img, (0,0), fx=scale_factor, fy=scale_factor) for img in images]
        # Delete images folder
        os.system(f"rm -r {images_path}")
        os.mkdir(images_path)
        save_images_to_folder(images, images_path)


    pycolmap.extract_features(database_path=database_path, image_path=images_path, camera_model="PINHOLE")

    pycolmap.match_exhaustive(database_path=database_path)

    os.mkdir(project_path / "sparse")
    subprocess.call(["colmap", "mapper", "--database_path", database_path, "--image_path", images_path, "--output_path", project_path / "sparse"])

    subprocess.call(["colmap", "model_converter", "--input_path", project_path / "sparse/0", "--output_path", project_path / "sparse", "--output_type", "TXT"])

def reconstruction_open_mvs(mvs_path: pathlib.Path, folder_path: pathlib.Path, low_poly=False): 
    open_mvs_obj = open_mvs(mvs_path, folder_path)
    open_mvs_obj.run_all(low_poly)

def reconstruction_3dgs(project_path: pathlib.Path):
    images_path = project_path / "images" 
    #Todo fix paths
    subprocess.run(["ns-process-data", "images", "--data", images_path, "--output-dir", project_path])
    subprocess.run(["ns-train", "splatfacto", "--data", project_path])


if __name__ == "__main__":

    pre_process_images(pathlib.Path("temp/broom"), scale_factor=0.5)
    reconstruction_open_mvs(pathlib.Path("../packages/openMVS/make/bin"), pathlib.Path("temp/broom"), low_poly=True)