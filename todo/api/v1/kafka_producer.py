from confluent_kafka import Producer
import json
from confluent_kafka import KafkaException
from tasks import exceptions
import logging

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers="kafka:9092"):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send_event(self, topic, key, value):
        try:
            self.producer.produce(
                topic,
                key=key,
                value=json.dumps(value),
                callback=self.delivery_report
            )
            self.producer.flush()
        except KafkaException as e:
            logger.error("Error while sending event to Kafka: %s", e)
            raise

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            raise exceptions.KafkaException
        else:
            logger.error(f"Message was successfully sent to {msg.topic()} [{msg.partition()}]")