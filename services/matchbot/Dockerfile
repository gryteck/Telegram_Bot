FROM python:3.10
# set work directory
WORKDIR /matchbot
# copy project
COPY requirements.txt .
# install dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && pip3 install -r requirements.txt

COPY . .
# run app
CMD ["python3", "app.py"]