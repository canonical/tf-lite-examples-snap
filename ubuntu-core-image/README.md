# Ubuntu Core custom image

This image includes the TensorFlow Lite example for Ubuntu Frame.
The snap is installed from the Snap Store.

## Build the gadget snap

Add the contents of [additions-to-gadget.yaml](additions-to-gadget.yaml) to [gadget.yaml](pi-gadget/gadget.yaml).
If you want to preconfigure WiFI, change the SSID and password in `gadget.yaml`.

In [Makefile](pi-gadget/Makefile) on line 150 change `fkms` to `kms`.

Then build the gadget snap:

```
cd pi-gadget
snapcraft -v
```

## Create the image

Sign the model:

```
snap sign -k my-model-key model.json > model.model
```

Build the image:

```
ubuntu-image snap --snap pi-gadget/pi_24-1_arm64.snap --snap ../ubuntu-frame/tf-custom-examples_0.0.2_arm64.snap --validation=enforce model.model
```
