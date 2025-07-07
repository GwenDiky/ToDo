class KafkaConnectionError(Exception):
    def __init__(self) -> None:
        self.status_code = 417
        self.detail = "Kafka connection error"
        super().__init__(self.detail)


class KafkaTimeoutError(Exception):
    def __init__(self) -> None:
        self.status_code = 417
        self.detail = "Kafka timeout error"
        super().__init__(self.detail)


class KafkaError(Exception):
    def __init__(self) -> None:
        self.status_code = 417
        self.detail = "Unexpected Kafka error"
        super().__init__(self.detail)
