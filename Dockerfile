FROM python:3.9
RUN mkdir app
COPY ["coco.names","iWebLens_server.py","yolov3-tiny.cfg","yolov3-tiny.weights","requirements.txt","./app/"]
WORKDIR ./app/
RUN apt-get update -y 
RUN apt install ffmpeg libsm6 libxext6  -y
RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r requirements.txt
CMD ["python3", "iWebLens_server.py"]
EXPOSE 2020