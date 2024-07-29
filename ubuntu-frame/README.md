# TensorFlow Lite Examples snap for Ubuntu Core

This snap bundles example TensorFlow Lite applications with all their required dependencies to run on Ubuntu Core.
They are based on the
[TensorFlow Lite examples](https://github.com/tensorflow/examples/tree/master/lite/examples).

Core24, which is used for the base of this snap, ships with Python 3.12.
TensorFlow Lite does not currently work with Python 3.12 due to dependencies that are [not yet updated](https://github.com/tensorflow/tensorflow/issues/62003).
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
snap install --dangerous ./tf-custom-examples_*.snap
```

You also need to connect the camera plug for the camera examples to work:

```
sudo snap connect tf-custom-examples:camera
```

The snap includes a daemon process called `camera-detect-stream` that automatically starts when the snap is installed.
Stop it now until you read the rest of the readme.

```
sudo snap stop tf-custom-examples.camera-detect-stream
```

## How to use

### Detect objects in image

If the app is run without any arguments, it will use the included `EfficientDet` model and classify an image of [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) that is included in the snap.

```
$ tf-custom-examples.image-detect
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
0.964844: person @ x1=3 y1=19 x2=514 y2=607
0.457031: tie @ x1=222 y1=411 x2=299 y2=536
time: 37.557ms
```

The detected objects can be annotated on the image and stored in a file by providing the `-o` argument with a filename.

```
tf-custom-examples.image-detect -o grace-objects.png
```

![grace-objects](../media/grace-objects.png)

The input file can be specified with the `-i` argument. For a list of all possible application arguments, run:

```
tf-custom-examples.image-detect --help
```

### Detect objects from a camera

A more useful application is to detect objects in a video feed. The `camera-detect` app reads frames from an attached USB webcam, detects objects in the frames, and prints out the objects, their certainty, and their location to the console.

```
tf-custom-examples.camera-detect
$ tf-custom-examples.camera-detect
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
...
======
0.789062: person @ x1=42 y1=111 x2=562 y2=474
0.351562: chair @ x1=23 y1=382 x2=90 y2=477
FPS = 30.7
======
```

This example can modified to stream the detections to other destinations for example using MQTT.

Configurations like the camera ID and ML model can be passed via command line arguments.

### Daemon process

This snap includes a daemon process which automatically starts up, unless it's manually stopped.
This daemon runs the `camera-detect-stream` app as a system service.
By default it captures video frames from `/dev/video0`, does object detection on them, and streams it out to a webpage.

To start it up, run:

```
sudo snap start tf-custom-examples.camera-detect-stream
```

On another device go to `http://<IP Address>:8080`, using the IP address of the device on which the snap is running, to see a live feed of the camera annotated with detected objects.

See [Advanced Usage](#advanced-usage) to configure the service.

## Running the example on Ubuntu Core

Start from a clean Ubuntu Core 24 install.

Copy the built snap to the Pi:

```
scp tf-custom-examples_0.0.2_arm64.snap <username>@<address>:
```

Install snap:
```
sudo snap install --dangerous ./tf-custom-examples_0.0.2_arm64.snap
```

Check daemon logs: 
```
sudo snap logs -f tf-custom-examples.camera-detect-stream
```

You will likely see a camera index out of range error, even though `ls /dev/video*` shows `video0` exists.

Connect the camera plug:
```
sudo snap connect tf-custom-examples:camera
```

Restart snap daemon
```
sudo snap restart tf-custom-examples.camera-detect-stream
```

You can check logs again to confirm the camera error is gone, and the service is running.

On another computer go to the IP address of the device, port 8080.
For example: http://192.168.1.30:8080/

### Ubuntu Frame (experimental)

This web interface can also be displayed on the device itself using Ubuntu Frame.
It is however experimental, so your milage may vary.

Install Ubuntu Frame and the WPE Web Kiosk snaps:
```
snap install ubuntu-frame wpe-webkit-mir-kiosk
```

Set the URL for the web kiosk: 
```
snap set wpe-webkit-mir-kiosk url=http://localhost:8080
```

If you are running a Raspberry Pi 5, and nothing is displayed after the previous command, make sure you are using `kms` and not `fkms`.
See [this issue](https://github.com/canonical/ubuntu-frame/issues/192).

After a reboot, the kiosk browser starts up before the TensorFlow Lite example.
One needs to manually click refresh in the browser, as the browser loads before our snap.

After a refresh the webpage is displayed, albeit very buggy.
Updating to a newer version of `wpe-webkit-mir-kiosk` improves things a little bit:

```
snap refresh  wpe-webkit-mir-kiosk --candidate
```

## Advanced usage

The apps provide command line arguments to override their default behaviour.
Run them with the `--help` argument to see available options.

The daemon process can not directly be configured by command line arguments.
For that purpose we added a wrapper script which checks for the `camera-detect-stream.arguments` snap option.
If this option is set, its the value will be appended to the startup command of the daemon process.

Available arguments are:
```
optional arguments:
  -h, --help            show this help message and exit
  --model MODEL         Path of the object detection model. (default:
                        /snap/tf-custom-examples/x8/efficientdet_lite0.tflite)
  --cameraId CAMERAID   Id of camera. (default: 0)
  --frameWidth FRAMEWIDTH
                        Width of frame to capture from camera. (default: 640)
  --frameHeight FRAMEHEIGHT
                        Height of frame to capture from camera. (default: 480)
  --numThreads NUMTHREADS
                        Number of CPU threads to run the model. (default: 4)
  --enableEdgeTPU       Whether to run the model on EdgeTPU. (default: False)
  --ip IP               ip address of the device (default: 0.0.0.0)
  --port PORT           ephemeral port number of the server (1024 to 65535)
                        (default: 8080)
```

For example to change the port the service listens on to 8084, and then restarting it for the changes to take affect:
```
sudo snap set tf-custom-examples camera-detect-stream.arguments="--port 8084"
sudo snap restart tf-custom-examples.camera-detect-stream
```

To view the current configuration, you can run:
```
$ sudo snap get tf-custom-examples camera-detect-stream.arguments
--port 8084
```
