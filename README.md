# TensorFlow Lite Examples Snap

This is a snapped version of the examples for the Raspberry Pi which are available at https://www.tensorflow.org/lite/examples. This snap should work on a Raspberry Pi running Ubuntu Desktop or Ubuntu Frame, but will also work on an AMD64 device running Ubuntu Desktop.

## Build the snap

Clone this repo, then inside the cloned directory execute:

```
snapcraft -v
```

## Install the snap

Currently this snap is not available from the store, so you need to build it yourself. After building the snap according to the previous section, you should have a `.snap` file in your working directory. 

Install it by running:
```
sudo snap install --dangerous ./tf-lite-examples_*+snap_amd64.snap
```

## Connect interfaces

Most of the examples use the system camera. Please connect the `camera` interface to give the snap access to the camera:

```
sudo snap connect tf-lite-examples:camera
```

## Running the examples

### Image classification

```
tf-lite-examples.image-classification
```

### Object detection

```
tf-lite-examples.object-detection
```

### Pose estimation

```
tf-lite-examples.pose-estimation
```

The alternative models for pose estimation is also available. They can be selected by providing a command line argument with the model name:
```
$ tf-lite-examples.pose-estimation --model posenet
$ tf-lite-examples.pose-estimation --model movenet_lightning
$ tf-lite-examples.pose-estimation --model movenet_thunder
$ tf-lite-examples.pose-estimation --model movenet_multipose
```

Pose classification is possible by specifying the classifier and label file names:
```
$ tf-lite-examples.pose-estimation --classifier classifier --label_file tflite/pose_estimation/labels.txt
```

### Segmentation

```
tf-lite-examples.image-segmentation
```

### Audio classification

> Audio classification does not currently work due to a dependency issue between snap `core22` and `libportaudio2`.

Without `libpportaudio2` included:
```
$ tf-lite-examples.audio-classification 
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
Traceback (most recent call last):
  ...
OSError: cannot load library 'libportaudio.so.2': libportaudio.so.2: cannot open shared object file: No such file or directory
```

With `libpportaudio2` included:
```
$ tf-lite-examples.audio-classification
Aborted (core dumped)
```

### Video classification

```
tf-lite-examples.video-classification --label tflite/video_classification/kinetics600_label_map.txt
```

> Note: because the running directory is different than the one where the video classification example looks for the lable file, one needs to specify the path to it as an argument.
