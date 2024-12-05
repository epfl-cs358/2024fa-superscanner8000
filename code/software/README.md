# Superscanner8000 software

## Installation Guide

### Step 1: Install Miniconda

Miniconda is a minimal installer for conda. Follow the steps below to install Miniconda on your system.

1. **Download Miniconda:**

   - Go to the [Miniconda download page](https://docs.conda.io/en/latest/miniconda.html).
   - Download the installer for your operating system (Windows, macOS, or Linux).

2. **Install Miniconda:**

   - Run the installer and follow the prompt. Don't forget to check the "Add folder to your path".

3. **Verify the Installation:**
   - Open a new terminal or command prompt.
   - Run the following command to verify that Miniconda is installed correctly:
     ```sh
     conda --version
     ```

### Step 2: Install NVIDIA CUDA Toolkit

1. **Check NVIDIA CUDA requirements**

   - Check that your computer support NVIDIA CUDA here: [System requirements for NVIDIA CUDA](https://massedcompute.com/faq-answers/?question=What%20are%20the%20system%20requirements%20for%20NVIDIA%20CUDA?)

2. **Download the installer**

   - Download the installer here: [Download CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)

3. **Install NVIDIA CUDA**
   - Run the installer and follow the prompt. Don't forget to check the "Add folder to your path".

### Step 3: Set Up the Superscanner8000 Environment

1. **Create the Conda Environment:**

   - Run the following command to create the `superscanner8000env` environment using the [environment.yml](http://_vscodecontentref_/1) file:
     ```sh
     conda env create -f environment.yml
     ```

2. **Activate the Environment:**

   - Once the environment is created, activate it using the following command:
     ```sh
     conda activate superscanner8000env
     ```

. **Verify the Environment:**

- Ensure that the environment is set up correctly by checking the installed packages:
  ```sh
  conda list
  pip list
  ```
- If the pip list does not contain all the packages listed on the requirements.txt run:
  ```sh
  pip install -r requirements.txt
  ```

### Step 4: Install SAM2 from GitHub

1. **Go to the controllers folder**

   ```sh
   cd ./code/software/packages
   ```

2. **Clone the SAM2 Repository:**

   - Run the following command to clone the SAM2 repository from GitHub:
     ```sh
     git clone https://github.com/Gy920/segment-anything-2-real-time.git sam2
     ```

3. **Navigate to the SAM2 Directory:**

   - Change to the SAM2 directory:
     ```sh
     cd sam2
     ```

4. **Install SAM2:**

   - Run the following command to install SAM2:
     ```sh
     pip install -e .
     ```

5. **Go to the checkpoints folder**

   ```sh
   cd ../../config/sam2_checkpoints
   ```

6. **Run the bash script:**

   - Run the install the checkpoints
     ```sh
     ./download_ckpts
     ```

### Step 5: Start Using Superscanner8000

1. **Go to the app folder**

   ```sh
   cd ./code/software
   ```

2. **Run the main.py**
   ```sh
    python run main.py
   ```

### Additional Commands

- **Deactivate the Environment:**
  ```sh
  conda deactivate
  ```

## Software structure

### main.py

The file to start the app. It contains all the instance of the different pages and the instance of the high level controllers.

### /pages

Contains the different pages of the application, each implemented as a separate module.

### /widgets

Contains reusable UI components and widgets used across different pages of the application.

### /controllers

Contains the controller modules that handle the logic and interactions with the device.

### /assets

Contains static assets such as images, stylesheets, and other resources used by the application.
