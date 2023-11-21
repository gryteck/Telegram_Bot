FROM python:3.10
# set work directory
WORKDIR /matchbot
# copy project
COPY . .
# install dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && pip3 install -r requirements.txt
# run app
CMD ["python3", "app.py"]