# Ubuntu Core custom image

This image includes the TensorFlow Lite example for Ubuntu Frame.

Build the examples snap - on a Raspberry Pi or other arm64 host:
```
cd ../ubuntu-frame
snapcraft -v
```

## Build the gadget snap
Add contents of [additions-to-gadget.yaml](additions-to-gadget.yaml) to [gadget.yaml](pi-gadget/gadget.yaml).

In [Makefile](pi-gadget/Makefile) on line 150 change `fkms` to `kms`.

```
cd pi-gadget
snapcraft -v
```

Sign the model:
```
snap sign -k my-model-key model.json > model.model
```

Build the image:
```
ubuntu-image snap --snap pi-gadget/pi_24-1_arm64.snap --snap ../ubuntu-frame/tf-custom-examples_0.0.2_arm64.snap --validation=enforce model.model
```