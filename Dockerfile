FROM python:3.8
COPY requirements.txt main.py /
RUN apt update && \
    apt install dumb-init && \
    pip install -r /requirements.txt
ENTRYPOINT [ "dumb-init", "--" ]
CMD [ "python", "/main.py" ] 
