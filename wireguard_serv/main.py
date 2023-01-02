from configurer.server import WireguardServ, KafkaManager
from same_files.repository import Repository
from same_files.kafka_master import KafkaReader, KafkaWriter
import os


def main():
	db_name = os.getenv("DB_NAME")
	db_user = os.getenv("DB_USER")
	db_pass = os.getenv("DB_PASS")
	db_host = os.getenv("DB_HOST")
	kafka_servers = os.getenv("KAFKA_SEVERS")
	kafka_jobs_topic = os.getenv("KAFKA_JOBS_TOPIC")
	kafka_done_topic = os.getenv("KAFKA_DONE_TOPIC")

	repo = Repository(db_name, db_user, db_pass, db_host)
	wg_serv = WireguardServ("./config/wg0.conf", repo)

	kafka_reader = KafkaReader(kafka_jobs_topic, kafka_servers)
	kafka_writer = KafkaWriter(kafka_done_topic, kafka_servers)
	kafka_mgr = KafkaManager(kafka_reader, kafka_writer, wg_serv)

	kafka_mgr.setup_handler()
