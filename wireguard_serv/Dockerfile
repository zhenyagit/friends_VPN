FROM ubuntu

RUN apt-get update && \
 apt-get install -y --no-install-recommends wireguard-tools iptables nano net-tools procps openresolv inotify-tools && \
 apt install -y iproute2 &&\
 apt-get clean

ENV PYTHONUNBUFFERED=1
RUN apt-get install -y --no-install-recommends build-essential libpq-dev python3 python3-pip python3-dev &&\
 apt-get clean
RUN pip3 install --no-cache --upgrade pip setuptools

WORKDIR /app
ENV PATH="/app:${PATH}"
VOLUME /etc/wireguard

COPY wireguard_serv/requirements.txt .
RUN pip install -r requirements.txt

COPY wireguard_serv/configurer/* ./configurer/
COPY same_files/* ./same_files/
COPY wireguard_serv/main.py ./main.py
COPY wireguard_serv/init.sh ./init.sh
CMD ["/bin/bash", "init.sh"]

#sudo docker run --rm --name=wireguard   --cap-add=NET_ADMIN   --cap-add=SYS_MODULE   -e PUID=1000   -e PGID=1000 -e PEERS=1  -e TZ=Europe/London  -v config:/config new_wireguard