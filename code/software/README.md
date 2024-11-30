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

### Step 2: Set Up the Superscanner8000 Environment

2. **Create the Conda Environment:**

   - Run the following command to create the `superscanner8000env` environment using the [environment.yml](http://_vscodecontentref_/1) file:
     ```sh
     conda env create -f environment.yml
     ```

3. **Activate the Environment:**

   - Once the environment is created, activate it using the following command:
     ```sh
     conda activate superscanner8000env
     ```

4. **Verify the Environment:**
   - Ensure that the environment is set up correctly by checking the installed packages:
     ```sh
     conda list
     ```

### Step 3: Start Using Superscanner8000

- With the environment activated, you can now start using the Superscanner8000 project. Run your desired scripts or applications within this environment.

### Additional Commands

- **Deactivate the Environment:**
  ```sh
  conda deactivate
  ```
