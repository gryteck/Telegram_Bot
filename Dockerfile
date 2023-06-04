FROM python:3.10
# set work directory
WORKDIR /Telegram_Bot
# copy project
COPY . .
# install dependencies
RUN pip3 install -r requirements.txt
# run app
CMD ["python3", "main.py"]