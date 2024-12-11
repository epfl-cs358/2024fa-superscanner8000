#Install sam2-realtime
git clone https://github.com/Gy920/segment-anything-2-real-time.git sam2
cd sam2
pip install -e .

cd ..

#clone VCG repo
git clone https://github.com/cnr-isti-vclab/vcglib.git

#Clone OpenMVS
git clone --recurse-submodules https://github.com/cdcseacave/openMVS.git

#Make build directory:
cd openMVS
mkdir make
cd make

#Run CMake:
cmake .. -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT=../../vcglib

#Build:
cmake --build . -j4

#Download sam2 checkpoints
cd ../../../config/sam2_checkpoints
./download_ckpts



