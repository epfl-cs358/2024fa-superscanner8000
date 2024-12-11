import os
import subprocess
import pathlib

class open_mvs:
    def __init__(self, mvs_bin_dir: pathlib.Path, working_dir: pathlib.Path):
        #Colmap directory
        self.mvs_bin_dir = mvs_bin_dir
        self.working_dir = pathlib.Path.cwd() / working_dir

    def interface_colmap(self):
        cmd_path = self.mvs_bin_dir / "InterfaceCOLMAP"
        output_path = self.working_dir / pathlib.Path("model_colmap.mvs")

        command = [
            cmd_path,
            "--working-folder", self.working_dir,
            "--input-file", self.working_dir,
            "--output-file", output_path
        ]
        
        return_code = subprocess.call(command)
        return return_code
    
    def densify_point_cloud(self):
        cmd_path = self.mvs_bin_dir / "DensifyPointCloud"
        input_file = self.working_dir / pathlib.Path("model_colmap.mvs")
        output_path = self.working_dir / "model_dense.mvs"
        
        command = [
            cmd_path,
            "--working-folder", self.working_dir,
            "--input-file", input_file,
            "--output-file", output_path,
            "--archive-type", "-1"
        ]
        
        return_code = subprocess.call(command)
        return return_code
    
    def reconstruct_mesh(self):
        cmd_path = self.mvs_bin_dir / "ReconstructMesh"
        input_file = self.working_dir / "model_dense.mvs"
        output_path = self.working_dir / "model_dense_mesh.mvs"

        
        command = [
            cmd_path,
            "--working-folder", self.working_dir,
            "--input-file", input_file,
            "--output-file", output_path
        ]
        
        return_code = subprocess.call(command)
        return return_code
    
    def refine_mesh(self):
        cmd_path = self.mvs_bin_dir / "RefineMesh"

        # Check if model_dense_mesh.mvs exists
        if os.path.exists(self.working_dir / "model_dense_mesh.mvs" ):
            input_file = self.working_dir / "model_dense_mesh.mvs"
        else:
            input_file = self.working_dir / "model_dense.mvs"


        output_path = self.working_dir / "model_dense_mesh_refine.mvs"
        mesh_file = self.working_dir / "model_dense_mesh.ply"

        command = [
            cmd_path,
            "--working-folder", self.working_dir,
            "--input-file", input_file,
            "--output-file", output_path,
            "--resolution-level", "1",
            "--mesh-file", mesh_file
        ]
        
        return_code = subprocess.call(command)
        return return_code
    
    def texture_mesh(self, output_path="model.obj"):
        cmd_path = self.mvs_bin_dir / "TextureMesh"

        # Check if model_dense_mesh_refine.mvs exists
        if os.path.exists(self.working_dir / "model_dense_mesh_refine.mvs"):
            input_file = self.working_dir / "model_dense_mesh_refine.mvs"
        elif os.path.exists(self.working_dir / "model_dense_mesh.mvs"):
            input_file = self.working_dir / "model_dense_mesh.mvs"
        else:
            input_file = self.working_dir / "model_dense.mvs"

        if output_path == "model.obj":
            output_path = self.working_dir / "model.obj"
        
        if os.path.exists(self.working_dir / "model_dense_mesh_refine.ply"):
            mesh_file = self.working_dir / "model_dense_mesh_refine.ply"
        mesh_file = self.working_dir / "model_dense_mesh.ply"

        command = [
            cmd_path,
            "--working-folder", self.working_dir,
            "--input-file", input_file,
            "--output-file", output_path,
            "--export-type", "obj",
            "--mesh-file", mesh_file
        ]
        
        return_code = subprocess.call(command)
        return return_code
    
    def run_all(self, lowpoly=False):
        self.interface_colmap()
        self.densify_point_cloud()
        self.reconstruct_mesh()
        if lowpoly:
            self.refine_mesh()
        self.texture_mesh()
        return 0