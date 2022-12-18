FROM linuxserver/wireguard:1.0.20210914
WORKDIR /app

RUN  apt-get update -y

ENV PYTHONUNBUFFERED=1
RUN apt-get install -y  python3 python3-pip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]

#sudo docker run --rm -it  --name=wireguard   --cap-add=NET_ADMIN   --cap-add=SYS_MODULE   -e PUID=1000   -e PGID=1000 -e PEERS=1  -
#e TZ=Europe/London  -v config:/config test_image:latest