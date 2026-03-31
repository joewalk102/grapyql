class GraphQLResponseError(Exception):
    def __init__(self, message, response):
        self.message = message
        self.response = response

    def __str__(self):
        return f"{self.message} - {self.response}"


class PayloadVerificationError(Exception):
    def __init__(self, message, response):
        self.message = message
        self.response = response

    def __str__(self):
        return f"{self.message} - {self.response}"
