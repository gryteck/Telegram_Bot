FROM python:3.10
# set work directory
WORKDIR /matchbot
# copy project
COPY requirements.txt .
# install dependencies
RUN pip3 install -r requirements.txt

COPY . .
# run app
CMD ["python3", "app.py"]