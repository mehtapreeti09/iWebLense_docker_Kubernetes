#Importing all the required libraries like flask, cv2, numpy
import flask
from flask import request
import cv2
import numpy as np
import json

#Importing ThreadPoolExecutor Library for Multithreading
from concurrent.futures import ThreadPoolExecutor

#Creating an instance of  ThreadPoolExecutor and setting 4 as maximum number of workers i.e
#this thread pool will only have 4 concurrent threads
executor = ThreadPoolExecutor(4)

#Creates the Flask application object, which contains data about the application
app = flask.Flask(__name__)

#Defining default route as GET request and mapping it to test() method for testing the application
@app.route('/')
def test():
    return "Hello, World!"

#Defining /api/object_detection route as POST request and mapping it to image_scan() method for recieving client request
@app.route('/api/object_detection', methods=['POST'])
def image_scan():

    #Reading file buffer from the request object sent by the client
    img_str = request.files["image"].read()

    #Executing image_scan_implimentation() as individual threads by ThreadPoolExecutor object and passing image data as argument
    exec = executor.submit(image_scan_implimentation, img_str)

    #Returning the python dict to the client which image_scan_implimentation() method is returning
    return exec.result()


#Method implimenting the business logic of the API by taking the buffer image and returning the dict having list of objects detected along
#with their accuracy
def image_scan_implimentation(img_str):

    #Loading trained model of YOLO along with its config file.
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")

    #Reading the objects names that YOLO can detect from coc.names file and storing them in list classes
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1]
                     for i in net.getUnconnectedOutLayers()]

    nparr = np.frombuffer(img_str, np.uint8)

    # cv2.IMREAD_COLOR in OpenCV 3.1
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img = cv2.resize(img_np, None, fx=0.4, fy=0.4)

    # Detecting objects by using Blob which is used to extract feature from the image and 
    # to resize them to 416x416 which gives both accuracy and speed
    blob = cv2.dnn.blobFromImage(
        img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)

    #object_info is an array that conains all the informations about objects detected, their position and the confidence about the detection.
    object_info = net.forward(output_layers)

    objects_list = []

    #Traversing the object_info array to find the objects detected and their confidence(position)
    for obj in object_info:
        for detection in obj:
            scores = detection[5:]
            class_id = np.argmax(scores)
            accuracy = scores[class_id]
            #Taking accuracy/confidence level 1% for detection of objects.
            if accuracy > 0.01:
                objects_dict = {}
                objects_dict["label"] = str(classes[class_id])
                objects_dict["accuracy"] = str(round(float(accuracy)*100, 2))
                objects_list.append(objects_dict)

    #Returning the python dict having all the info about the objects detected by the model
    return {"objects": objects_list}

if __name__ == "__main__":
    #Using flask object to runs the application server on Port 2020 in debug mode with host - 0.0.0.0
    app.run(host="0.0.0.0", port=2020, debug=True)
