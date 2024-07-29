# TensorFlow Lite Examples snap for Ubuntu Core

This snap bundles example TensorFlow Lite applications with all their required dependencies to run on Ubuntu Core.
They are based on
the [TensorFlow Lite Python image classification demo](https://github.com/tensorflow/tensorflow/tree/master/tensorflow/lite/examples/python)
and the [TensorFlow Lite examples](https://github.com/tensorflow/examples/tree/master/lite/examples).

Core24, which is used for the base of this snap, ships with Python 3.12.
TensorFlow Lite does not currently work with Python 3.12 due to dependencies that
are [not yet updated](https://github.com/tensorflow/tensorflow/issues/62003).
The most reliable combination of dependencies that work on AMD64 and ARM64 are based on Python 3.8.
This snap includes Python 3.8 from the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

This snap was tested on the following platforms, but should work on any platform that runs SnapD:

- Ubuntu Desktop 24.04 on AMD64 workstation
- Ubuntu Server 24.04 on Raspberry Pi 5
- Ubuntu Core 24 on Raspberry Pi 5

## Build the snap

This snap is not available via the Snap Store.
You will need to build it from source yourself.
Clone this repository and then run the following command in the cloned directory:

```
snapcraft -v
```

We recommend building on Ubuntu Desktop 24.04 or Ubuntu Server 24.04.

## Install the snap

```
snap install --dangerous ./tf-label-image_*.snap
```

You also need to connect the camera plug for the camera examples to work:

```
sudo snap connect tf-label-image:camera
```

The snap includes a daemon process that automatically starts when the snap is installed.
Stop it now until you read the rest of the readme.

```
sudo snap stop tf-label-image.daemon
```

## How to use

### Label an image

If the app is run without any arguments, it will use the included `mobilenet v1-1.0-224` model and classify an image
of [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) that is included in the snap.

```
$ tf-label-image.image-label
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
0.919721: 653:military uniform
0.017762: 907:Windsor tie
0.007507: 668:mortarboard
0.005419: 466:bulletproof vest
0.003828: 458:bow tie, bow-tie, bowtie
time: 28.502ms
```

Any other image can be specified using the `-i` argument.
The snap has read access to the user's home directory, so any path under `$HOME` can be specified.
Example with [a parrot](https://commons.wikimedia.org/wiki/File:Parrot.red.macaw.1.arp.750pix.jpg):

```
$ tf-label-image.image-label -i ~/Downloads/Parrot.red.macaw.1.arp.750pix.jpg
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
0.939399: 89:macaw
0.060436: 91:lorikeet
0.000062: 90:sulphur-crested cockatoo, Kakatoe galerita, Cacatua galerita
0.000057: 24:vulture
0.000023: 88:African grey, African gray, Psittacus erithacus
time: 28.257ms
```

### Detect objects in image

```
tf-label-image.image-detect
```

### Detect objects from a camera

```
tf-label-image.camera-detect
```

### Detect objects from a camera and stream to web

This example captures video frames from `/dev/video0`, does object detection on them, and streams it out to a webpage.

Run the example like this:
```
tf-label-image.camera-detect-stream
```

Then on another device go to `http://<IP Address>:8080`, using the IP address of the device of the device on which the
snap is running.

You can override the camera by passing the `--cameraId` argument.
For example to use `/dev/video8` do:
```
tf-label-image.camera-detect-stream --cameraId 8
```

### Daemon process

As mentioned before, this snap includes a daemon process which automatically starts up, unless it's manually stopped.
This daemon runs the `camera-detect-stream` app as a system service.

To start it up, run:

```
sudo snap start tf-label-image.daemon
```

Currently this service can not be configured, so it will always try and use `/dev/video0`.

## Running the example on Ubuntu Core

Starting from a clean Ubuntu Core 24 install.

Copy over snap from another Pi 5 where it was built: 

`scp raspi-b.lan:tf-label-image-snap/tf-label-image_0.0.2_arm64.snap jpm@raspi-a.lan:`

Install snap: `sudo snap install --dangerous ./tf-label-image_0.0.2_arm64.snap`

Check daemon logs: `sudo snap logs -f tf-label-image.daemon`

See Camera index out of range but `ls /dev/video*` shows `video0` exists

Connect camera plug `sudo snap connect tf-label-image:camera`

Restart snap daemon `sudo snap restart tf-label-image.daemon`

You can check logs again to confirm, but it should run now.

On another computer go to the IP address of the device, port 8080, ex: http://192.168.86.31:8080/

### Ubuntu Frame (experimental)

This web interface can also be displayed on the device itself using Ubuntu Frame.
It is however buggy, so YMMV.

Install Ubuntu Frame and the WPE Web Kiosk snaps: `snap install ubuntu-frame wpe-webkit-mir-kiosk`

Set the URL for the web kiosk: `snap set wpe-webkit-mir-kiosk url=http://localhost:8080`

If you are running a Raspberry Pi 5, and nothing is displayed after the previous command, make sure you are using kms and not fkms.
See [this issue](https://github.com/canonical/ubuntu-frame/issues/192).

After a reboot, the kiosk browser starts up before the TensorFlow Lite example.
One needs to manually click refresh in the browser, as the browser loads before our snap.

After a refresh the webpage is displayed, albeit very buggy.
Updating to a newer version of `wpe-webkit-mir-kiosk` improves things a little bit: 

```
snap refresh  wpe-webkit-mir-kiosk --candidate
```


## Advanced usage

These apps provide command line arguments to override their default behaviour.
Run them with the `--help` argument to see available options.

```
$ tf-label-image.image-label --help
usage: label_image_lite.py [-h] [-i IMAGE] [-m MODEL_FILE] [-l LABEL_FILE]
                           [--input_mean INPUT_MEAN] [--input_std INPUT_STD]
                           [--num_threads NUM_THREADS] [-e EXT_DELEGATE]
                           [-o EXT_DELEGATE_OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        image to be classified
  -m MODEL_FILE, --model_file MODEL_FILE
                        .tflite model to be executed
  -l LABEL_FILE, --label_file LABEL_FILE
                        name of file containing labels
  --input_mean INPUT_MEAN
                        input_mean
  --input_std INPUT_STD
                        input standard deviation
  --num_threads NUM_THREADS
                        number of threads
  -e EXT_DELEGATE, --ext_delegate EXT_DELEGATE
                        external_delegate_library path
  -o EXT_DELEGATE_OPTIONS, --ext_delegate_options EXT_DELEGATE_OPTIONS
                        external delegate options, format: "option1: value1;
                        option2: value2"
```

## Debugging

Python 3.8 and the bundled dependencies are exposed by the snap under the `tf-label-image.python` app.
This can be used to run custom Python scripts, or get an interactive Python shell.

```
$ tf-label-image.python
Python 3.8.19 (default, Apr 27 2024, 21:20:48)
[GCC 13.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import tflite_runtime
>>> tflite_runtime.__version__
'2.14.0'
>>>
```

## Further examples

More advanced TensorFlow Lite snap examples can be found [here](https://github.com/canonical/tf-lite-examples-snap).
