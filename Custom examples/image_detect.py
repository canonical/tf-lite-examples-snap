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
"""Run the object detection on a provided image."""
import argparse
import os
import time

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

import utils


def run(filename: str, model: str, num_threads: int,
        enable_edgetpu: bool, result_filename: str) -> None:
    """Continuously run inference on images acquired from the camera.

    Args:
    model: Name of the TFLite object detection model.
    camera_id: The camera id to be passed to OpenCV.
    width: The width of the frame captured from the camera.
    height: The height of the frame captured from the camera.
    num_threads: The number of CPU threads to run the model.
    enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
    detection_options = processor.DetectionOptions(
        max_results=3, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

    image = cv2.imread(filename)

    # Convert the image from BGR to RGB as required by the TFLite model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Create a TensorImage object from the RGB image.
    input_tensor = vision.TensorImage.create_from_array(rgb_image)

    # Run object detection estimation using the model.
    start_time = time.time()
    detection_result = detector.detect(input_tensor)
    stop_time = time.time()

    if result_filename != "":
        # Draw detections and bounding boxes on image
        image = utils.visualize(image, detection_result)
        cv2.imwrite(result_filename, image)

    for result in detection_result.detections:
        for category in result.categories:
            print('{:08.6f}: {} @ x1={} y1={} x2={} y2={}'.format(category.score, category.category_name,
                                                                  result.bounding_box.origin_x,
                                                                  result.bounding_box.origin_y,
                                                                  result.bounding_box.origin_x + result.bounding_box.width,
                                                                  result.bounding_box.origin_y + result.bounding_box.height))

    print('time: {:.3f}ms'.format((stop_time - start_time) * 1000))


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i',
        '--image',
        default=os.getenv('SNAP', '.') + '/grace_hopper.bmp',
        help='Input image to detect objects in')
    parser.add_argument(
        '-m',
        '--model',
        help='Path of the object detection model.',
        required=False,
        default=os.getenv('SNAP', '.') + '/efficientdet_lite0.tflite')
    parser.add_argument(
        '-t',
        '--numThreads',
        help='Number of CPU threads to run the model.',
        required=False,
        type=int,
        default=4)
    parser.add_argument(
        '-x',
        '--enableEdgeTPU',
        help='Whether to run the model on EdgeTPU.',
        action='store_true',
        required=False,
        default=False)
    parser.add_argument(
        '-o',
        '--output',
        default="",
        required=False,
        help='Output the result as an image to this file')
    args = parser.parse_args()

    run(args.image, args.model, int(args.numThreads), bool(args.enableEdgeTPU), args.output)


if __name__ == '__main__':
    main()
