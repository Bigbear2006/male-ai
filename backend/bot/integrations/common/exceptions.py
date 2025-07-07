class APIClientException(Exception):
    def __init__(self, message: str, data: dict | None = None):
        self.message = message
        self.data = data

    def __str__(self):
        if not self.data:
            return self.message
        return f'{self.message}: {self.data}'
