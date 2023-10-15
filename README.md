# guns_n_bottles
Automating the guns and bottles game

<p align="center">
  <img src="https://github.com/subhajit-dubey/guns_n_bottles/blob/main/img/img1.JPG" />
</p>

## Pre-requisites
- [scrcpy](https://github.com/Genymobile/scrcpy) - A very useful package to github project helping in projecting mobile screen on PC
- [labelimg](https://github.com/qaprosoft/labelImg) - Another useful application that helped in tagging the coordinates of captured image for model training

## Modeling Steps
<b><i>Step 1:</i></b> The game was played in mobile and the video of the gameplay was captured

<b><i>Step 2:</i></b> The video was played on mobile and the images\frames were captured as array of images in the PC connected via USB cable, running the `Screen_Capture.py` script
and `scrcpy`

<b><i>Step 3:</i></b> Those screenshots were used in `labelimg` app to tag the objects and their coordinates in the image was captured. 2 examples are provided in the `screenshots` folder. The coordinates of the repective screenshots are provided in the respective text file in the same folder (produced by the app)

<b><i>Step 4:</i></b> Used the `YOLOv4_Training_Tutorial.ipynb` in `Google Colab` to train the model with GPU support. Performance of the model was tracked by splitting the images into `train` and `test` sets. Yolov4 configuration and weights file was downloaded from the environment for light-weight model implementation.

<font color='aqua'><i>The file with weights, downloaded from the `Colab` environment could not be uploaded to this GitHub repo due to its size of around 245 MB</i></font>

## Implementation

- Concepts of `Coordinate Geometry` used to find out the intersection of the bullet trajectory and the edges of the bottles
- Mouse click was triggered in Windows PC machine only, but  `scrcpy` was used to trigger `touche-screen tap` on the mobile leading to gunshots

## Challenges

- A latency issue was identified when running the application for which the bottle's bisector trajectory was extended to intersect the bullet trajectory before the head-edge of the bottle actually intesects
- In the actual gameplay the bottle when hit gets shattered and even in pieces it was regarded as a hit situation leading to further bullet loss and hence, `splattered` class was introduced to minimize bullet loss
