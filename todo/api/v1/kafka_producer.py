from confluent_kafka import Producer
import json
from confluent_kafka import KafkaException
from tasks import exceptions
from todo import exceptions as kafka_exceptions
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
            logger.error(f"Error while sending event to Kafka: {e}")

            if 'connection' in str(e).lower():
                raise kafka_exceptions.KafkaConnectionError()

            elif 'timed out' in str(e).lower():
                raise kafka_exceptions.KafkaTimeoutError()

            else:
                raise kafka_exceptions.KafkaError()

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"Failed to deliver message: {err}")
            raise kafka_exceptions.KafkaError()
        else:
            logger.info(
                f"Message successfully sent to {msg.topic()} [{msg.partition()}]")
