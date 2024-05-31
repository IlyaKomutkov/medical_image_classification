FROM ubuntu

RUN apt-get update

RUN apt-get install -y python3 python3-pip

COPY . ./

RUN chmod 777 entrypoint.sh

RUN mkdir -p media/images

RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r requirements.txt --break-system-packages