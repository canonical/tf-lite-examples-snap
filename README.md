# TensorFlow Lite Examples Snap

This is a snapped version of the TensorFlow Lite examples for the Raspberry Pi which are available at [https://www.tensorflow.org/lite/examples](https://www.tensorflow.org/lite/examples).

## Supported platforms

This snap has been tested using a USB webcam on the following platforms.

| Platform       | OS                   | CPU               | [Edge TPU](#edge-tpu)        |
| -------------- | -------------------- | ----------------- | ---------------------------- |
| AMD64          | Ubuntu 24.04 Desktop | yes               | yes                          |
| Raspberry Pi 5 | Ubuntu 24.04 Desktop | yes               | yes (only in developer mode) |
| Raspberry Pi 4 | Ubuntu 24.04 Desktop | yes               | not tested                   |
| Raspberry Pi 3 | Ubuntu 24.04 Desktop | yes (slow, <1fps) | no (not enough resources)    |
| Raspberry Pi 3 | Raspberry Pi OS      | yes               | yes                          |

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

TensorFlow Lite supports Coral Edge TPUs. The snap has been tested with the [Coral USB Accelerator](https://coral.ai/products/accelerator). See [supported platforms](#supported-platforms).

The correct udev rules need to be installed. For the USB Accelerator you can add the rules with this command:

```
sudo sh -c "cat >>/etc/udev/rules.d/60-libedgetpu1-std.rules" <<-EOF
    SUBSYSTEM=="usb",ATTRS{idVendor}=="1a6e",ATTRS{idProduct}=="089a",GROUP="plugdev"
    SUBSYSTEM=="usb",ATTRS{idVendor}=="18d1",ATTRS{idProduct}=="9302",GROUP="plugdev"
EOF
```

And then trigger a udev rule update:

```
sudo udevadm trigger
```

On the Raspberry Pi 5 the `raw-usb` interface has a [bug](https://bugs.launchpad.net/snapd/+bug/2071319) that does not provide the required permissions to the snap to access `raw-usb` devices.
A workaround is to install the snap in [developer mode](https://snapcraft.io/docs/install-modes#heading--developer), which removes all confinement from the snap and disables automatic upgrades.
This is insecure and not recommended, but currently the only way to use a Coral USB Accelerator with this snap on a Raspberry Pi 5.
To install the snap in developer mode, do:

```
sudo snap install --dangerous ./tf-lite-examples_*+snap_amd64.snap --devmode
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

Audio classification does not currently work due to a dependency issue between snap and `libportaudio2`.
See [issue #6](https://github.com/canonical/tf-lite-examples-snap/issues/6).

### Video classification

```
tf-lite-examples.video-classification --label tflite/video_classification/kinetics600_label_map.txt
```

> Note: because the running directory is different than the one where the video classification example looks for the label file, one needs to specify the path to it as an argument.
> See [issue #7](https://github.com/canonical/tf-lite-examples-snap/issues/7).
