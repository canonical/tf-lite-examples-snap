# Copyright 2019 Adrian Rosebrock
# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Part of this code is based on https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/ and
# the relevant companion repository https://github.com/pornpasok/opencv-stream-video-to-web
#
"""Obtain images from camera, detect objects, annotate image, stream to webpage."""
import argparse
import os
import sys
import threading
import time

import cv2
from flask import Flask
from flask import Response
from flask import render_template_string
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

import utils

# outputFrame is a variable to pass images between the object detection thread and the Flask server thread.
# It uses a lock to prevent race conditions.
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)


def detect_objects(model: str, camera_id: int, width: int, height: int, num_threads: int, enable_edgetpu: bool) -> None:
    """Continuously run inference on images acquired from the camera.

    Args:
      model: Name of the TFLite object detection model.
      camera_id: The camera id to be passed to OpenCV.
      width: The width of the frame captured from the camera.
      height: The height of the frame captured from the camera.
      num_threads: The number of CPU threads to run the model.
      enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """
    global outputFrame, lock

    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()

    # Start capturing video input from the camera
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Visualization parameters
    fps_avg_frame_count = 10

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
    detection_options = processor.DetectionOptions(
        max_results=3, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

    # Continuously capture images from the camera and run inference
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        counter += 1
        image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)

        # Run object detection estimation using the model.
        detection_result = detector.detect(input_tensor)

        # Draw rectangles and labels on image
        image = utils.visualize(image, detection_result)

        # Calculate the FPS
        if counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(fps)
        # Enable the next line to print FPS to the terminal
        # print(fps_text)

        # Make a copy of the image for the Flask thread
        with lock:
            outputFrame = image.copy()

    # Close the camera
    cap.release()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
    return render_template_string(
        """<!DOCTYPE html>
        <html lang=en>
          <head>
            <meta charset=utf-8>
            <title>TensorFlow Lite stream</title>
          </head>
          <body>
            <div style="width: 100vw; height: 100vh; text-align: center;">
              <img style="object-fit: contain; max-width: 100%; height: 100%;" 
                src="{{ url_for('video_feed') }}" alt="stream">
            </div>
          </body>
        </html>""")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model',
        help='Path of the object detection model.',
        required=False,
        default=os.getenv('SNAP', '.') + '/efficientdet_lite0.tflite')
    parser.add_argument(
        '--cameraId',
        help='Id of camera.',
        required=False,
        type=int,
        default=0)
    parser.add_argument(
        '--frameWidth',
        help='Width of frame to capture from camera.',
        required=False,
        type=int,
        default=640)
    parser.add_argument(
        '--frameHeight',
        help='Height of frame to capture from camera.',
        required=False,
        type=int,
        default=480)
    parser.add_argument(
        '--numThreads',
        help='Number of CPU threads to run the model.',
        required=False,
        type=int,
        default=4)
    parser.add_argument(
        '--enableEdgeTPU',
        help='Whether to run the model on EdgeTPU.',
        action='store_true',
        # type=boolean,
        required=False,
        default=False)
    parser.add_argument(
        "-i",
        "--ip",
        help="ip address of the device",
        type=str,
        default='0.0.0.0',
        required=False)
    parser.add_argument(
        "-o",
        "--port",
        help="ephemeral port number of the server (1024 to 65535)",
        type=int,
        default=8080,
        required=False)
    args = parser.parse_args()

    print("cwd", os.getcwd())
    print("model", args.model)

    # start a thread that will perform object detection
    t = threading.Thread(target=detect_objects,
                         args=(
                             args.model,
                             args.cameraId,
                             args.frameWidth,
                             args.frameHeight,
                             args.numThreads,
                             args.enableEdgeTPU,
                         ))
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host=args.ip,
            port=args.port,
            debug=True,
            threaded=True,
            use_reloader=False)


if __name__ == '__main__':
    main()
