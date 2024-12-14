# Superscanner8000

** photo of finished SuperScanner8000 **
## Authors
   - Noa Emien Ette
   - Kevan Lam Hopyang
   - Louis Léonard Marie Larcher
   - Antoin Baptiste Gauthier
   - Mateo Tiedra
   - Ugo Novello
      
## Project Description 

The core of this project idea is to make a mobile robot capable of identifying the object of interest and taking pictures of it from all (possible) angles. This would be paired with a desktop application that would receive the images and apply the user-selected 3D reconstruction algorithm.

From this description, we can identify several key components the project needs:

1. **The Robot**:
   - 1.1: Navigate and plan routes around the object.
   - 1.2: Segment view and recognize the object of interest.
   - 1.3: Translate camera on the Z-axis whilst tracking the object of interest.

2. **The Desktop Application**:
   - 2.1: User can choose the object of interest.
   - 2.2: Process images sent by the robot using 3D reconstruction algorithms (NeRF, 2DGS, Multi-view stereo).

Nowadays, one does not need specialized high-end equipment to 3D scan objects. Most of us already have the necessary equipment—a smartphone, as long as it has a functioning camera and adequate software. For this project, we will not be using a smartphone, as having an integrated camera gives the robot higher usefulness without drastically increasing complexity.

In order to move the camera, we will use an arm with two segments, each powered by a stepper motor (like the Pixar lamp), fixed on top of the robot and oriented perpendicular to the wheels. In addition, the camera will be fixed to the arm using two servos offering roll and pitch control.

Most currently existing 3D object scanners are catered to small objects, rotating the object and photographing it from a fixed camera. We decided to take a different approach with the goal of providing more flexibility while keeping the complexity as low as possible.

## Project Structure

Below is a brief explanation of this repository's structure to provide context and aid readers' comprehension in the following sections of this document.
- `code` directory: contains all the code for the different parts of the project.
    - `hardware`: directory: contains all the code related to the hardware (motor movement, camera setup, connection to webserver) 
    - `software`: directory: contains all the code related to the software (webapp, navigation, reconstruction of 3d model...)
- `design` directory: contains all the 3D modeling files and exports along with the laser cut sheets.
- `diagrams` directory: contains all diagrams relate to the project
- `documentation` directory: contains all the pictures and schematics to be able to reproduce this project.
- `proposal` directory: the original document used to write the initial project proposal.

## Make your own SuperScanner8000

This section is dedicated to explaining how to build this project yourself! (All the printing/cutting part are available)

### Hardware

#### Main Body

###### Base

###### Wheels

###### Structures for electronics

#### Arm

##### Arm

##### Motor Housings

##### Gearbox

### Software


