FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=nontinteractive

RUN apt-get update && apt-get install python3 python3-pip i2c-tools -y

RUN mkdir -p /opt/fancontrol
COPY . /opt/fancontrol
WORKDIR /opt/fancontrol

RUN pip install -Ur requirements.txt
ENTRYPOINT ["python3", "main.py"]
