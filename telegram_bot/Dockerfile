FROM python:3.7-slim
WORKDIR /app

RUN  apt-get update -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY configurer/* ./configurer/
COPY ../same_files/* ./same_files/
CMD ["/bin/python3", "main.py"]

#sudo docker run --rm --name=wireguard   --cap-add=NET_ADMIN   --cap-add=SYS_MODULE   -e PUID=1000   -e PGID=1000 -e PEERS=1  -e TZ=Europe/London  -v config:/config new_wireguard