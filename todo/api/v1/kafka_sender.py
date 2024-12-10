import logging
from todo.api.v1 import kafka_producer

logger = logging.getLogger(__name__)

class KafkaEventSender:
    @staticmethod
    def send_task_event(event_type, instance, user_id=None):
        producer = kafka_producer.KafkaProducer()
        producer.send_event(
            topic="tasks",
            key=event_type,
            value={
                "event_type": event_type,
                "task_id": instance.id,
                "task_data": {
                    "id": instance.id,
                    "status": instance.status,
                    "project_id": instance.project.id,
                    "user_id": user_id,
                    "updated_at": instance.updated_at.isoformat(),
                    "created_at": instance.created_at.isoformat(),
                },
            },
        )
        logger.info("Sending event to Kafka: %s", instance.user_id if user_id else instance.id)

    @staticmethod
    def send_attachment_event(event_type, instance):
        producer = kafka_producer.KafkaProducer()
        producer.send_event(
            topic="static",
            key=event_type,
            value={
                "event_type": event_type,
                "file_data": {
                    "file_name": instance.get("file_name"),
                    "file_type": instance.get("file_type"),
                    "file_url": instance.get("file_url"),
                },
            },
        )
        logger.info("Sending event to Kafka '%s' with url: %s", event_type, instance.get("file_url"))
