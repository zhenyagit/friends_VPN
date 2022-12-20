import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from threading import Thread

class KafkaAdmin:
	def __init__(self, servers=None):
		if servers is None:
			self.servers = ['localhost:9092']
		else:
			self.servers = servers
		logging.info("Connect kafka admin to server : %s", str(self.servers))
		self.admin_client = KafkaAdminClient(
			bootstrap_servers=self.servers,
			client_id='admin_python')

	def topic_exist(self, topic):
		consumer = KafkaConsumer(group_id='checker', bootstrap_servers=self.servers)
		topics = consumer.topics()
		logging.info("Check topic exist %s", topic)
		for i in topics:
			logging.info("Topic exist %s", i)
		if topic in topics:
			return True
		else:
			return False

	def check_topic_exist(self, topic):
		if not self.topic_exist(topic):
			self.add_topic(topic)

	def add_topic(self, topic_name, num_partitions=1, replication_factor=1):
		logging.info("Create topic %s", topic_name)
		topic_list = [NewTopic(name=topic_name,
							   num_partitions=num_partitions,
							   replication_factor=replication_factor)]
		self.admin_client.create_topics(new_topics=topic_list, validate_only=False)


class KafkaReader:
	def __init__(self, topic, servers=None):
		if servers is None:
			self.servers = ['localhost:9092']
		else:
			self.servers = servers
		self.topic = topic
		self.subscribed = False
		self.reader = KafkaConsumer(topic,
									group_id='reader',
									bootstrap_servers=self.servers,
									value_deserializer=lambda m: json.loads(m.decode('ascii')),
									auto_offset_reset='earliest',
									enable_auto_commit=True)
		self.subscribe_thread = None

	def unsubscribe(self):
		if self.subscribe_thread is None:
			return None
		if self.subscribed:
			self.subscribed = False

	def subscribe(self, call_back):
		logging.info("Added thread with topic " + self.topic)
		self.subscribed = True
		self.subscribe_thread = Thread(target=self.subscribe_job, args=[call_back])
		self.subscribe_thread.start()


	def subscribe_job(self, call_back):
		for message in self.reader:
			message = message.value
			call_back(message)
			if not self.subscribed:
				break
		logging.info("Thread stop with topic " + self.topic)



class KafkaWriter:
	def __init__(self, topic, servers=None):
		super().__init__()
		if servers is None:
			self.servers = ['localhost:9092']
		else:
			self.servers = servers
		self.topic = topic
		logging.info("Create producer to topic %s", topic)

		self.producer = KafkaProducer(bootstrap_servers=self.servers,
									  value_serializer=lambda m: json.dumps(m).encode('ascii'))
		if self.producer.bootstrap_connected():
			logging.info("Producer connected")
		else:
			logging.info("Producer not connected")
		logging.debug("Check topic %s exist", topic)
		logging.error("Connect to server %s", self.servers[0])
		temp = KafkaAdmin(self.servers)
		temp.check_topic_exist(topic)

	def write(self, key, data: dict):
		logging.debug("Write to Kafka at %s to topic %s data: %s", str(self.servers), self.topic, str(data))
		try:
			self.producer.send(self.topic, key=key.encode("ascii"), value=data)
		except Exception as ex:
			logging.error("Kafka Error while write to %s topic", self.topic)

	def wait_done(self):
		self.producer.flush()


def demo():
	import time
	admin = KafkaAdmin()
	admin.check_topic_exist("test")

	test_dict = {"priv": "hello_man",
				 "name": "zhenya",
				 "age": 25}

	writer = KafkaWriter("test")
	writer.write("key", test_dict)

	def printer(data):
		print(data)

	reader = KafkaReader("test")
	reader.subscribe(printer)
	time.sleep(10)
	for i in range(10):
		test_dict["age"] = i
		print(i)
		writer.write("key", test_dict)
	time.sleep(10)
	reader.unsubscribe()
	time.sleep(10)



if __name__ == "__main__":
	demo()
