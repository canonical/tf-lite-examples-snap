# TensorFlow Lite Examples Snap

This is a snapped version of the TensorFlow Lite examples for the Raspberry Pi which are available at [https://www.tensorflow.org/lite/examples](https://www.tensorflow.org/lite/examples).

This snap should work on a Raspberry Pi 5 or an AMD64 device running Ubuntu Desktop.

## Build the snap

Clone this repo, then inside the cloned directory execute:

```
snapcraft -v
```

## Install the snap

Currently this snap is not available from the store, so you need to build it yourself.
After building the snap according to the previous section, you should have a `.snap` file in your working directory. 

Install it by running:
```
sudo snap install --dangerous ./tf-lite-examples_*+snap_amd64.snap
```

## Connect interfaces

Most of the examples use the system camera.
Please connect the `camera` interface to give the snap access to the camera:

```
sudo snap connect tf-lite-examples:camera
```

If you want to use a Coral USB Accelerator, also connect the raw-usb plug:

```
sudo snap connect tf-lite-examples:raw-usb
```

## Edge TPU
TensorFlow Lite supports Coral Edge TPUs. We have tested this snap with their [USB Accelerator](https://coral.ai/products/accelerator). 

On AMD64 computers this will work after the `raw-usb` interface is connected.

On a Raspberry Pi this interface has a bug that does not provide the required permissions to the snap to access `raw-usb` devices. A workaround is to install the snap in `devmode`, which removes all confinement from the snap. This is insecure and not recommended, but currently the only way to use a Coral USB Accelerator with this snap on a Raspberry Pi. To install the snap in `devmode`, do:

```
sudo snap install --dangerous ./tf-lite-examples_*+snap_amd64.snap --devmode
```

In addition to `devmode` one also need to run the examples with sudo. On the Raspberry Pi prefix all the example commands that use the USB Accelerator with sudo. Example:
```
sudo tf-lite-examples.object-detection --enableEdgeTPU --model efficientdet_lite0_edgetpu.tflite
```

## Running the examples

### Image classification

On the CPU:
```
tf-lite-examples.image-classification
```

With a Coral USB Accelerator:
```
tf-lite-examples.image-classification --enableEdgeTPU --model efficientnet_lite0_edgetpu.tflite
```

### Object detection

On the CPU:
```
tf-lite-examples.object-detection
```

With a Coral USB Accelerator:
```
tf-lite-examples.object-detection --enableEdgeTPU --model efficientdet_lite0_edgetpu.tflite
```

### Pose estimation

```
tf-lite-examples.pose-estimation
```

The alternative models for pose estimation is also available.
They can be selected by providing a command line argument with the model name:
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

On the CPU:
```
tf-lite-examples.image-segmentation
```

With a Coral USB Accelerator:
```
tf-lite-examples.image-segmentation --enableEdgeTPU --model deeplabv3_edgetpu.tflite
```

### ⚠️ Audio classification

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

> Note: because the running directory is different than the one where the video classification example looks for the label file, one needs to specify the path to it as an argument.
