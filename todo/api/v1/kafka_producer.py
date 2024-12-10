import logging
import json

from confluent_kafka import Producer
from confluent_kafka import KafkaException
from todo import exceptions as kafka_exceptions

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
                callback=self.delivery_report,
            )
            self.producer.flush()

        except KafkaException as e:
            logger.error("Error while sending event to Kafka: %s", e)

            if "connection" in str(e).lower():
                raise kafka_exceptions.KafkaConnectionError()

            if "timed out" in str(e).lower():
                raise kafka_exceptions.KafkaTimeoutError()

            raise kafka_exceptions.KafkaError()

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"Failed to deliver message: {err}")
            raise kafka_exceptions.KafkaError()
        logger.info(
            "Message successfully sent to %s [%s]", msg.topic(), msg.partition()
        )
