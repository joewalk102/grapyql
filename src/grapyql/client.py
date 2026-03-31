import logging

import requests

from grapyql import Query, Mutation
from grapyql.errors import PayloadVerificationError


log = logging.getLogger("grapyql.client")


class Client:
    def __init__(self, host, port, user, password, raise_on_error=True):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.raise_on_error = raise_on_error

    def request(self, payload: Query | Mutation | str, variables: dict = None):
        """
        Args:
          payload: The query or mutation that will be sent to the GraphQL server.
          variables: The variables that will be used in the query or mutation
        """
        # Check for gql object or string and set payload correctly.
        is_gql_obj_payload = isinstance(payload, (Query, Mutation))
        if is_gql_obj_payload:
            _payload = payload.to_gql(minified=True)
        else:
            _payload = payload

        # Setup and perform request.
        json_payload = {"query": _payload}
        if variables:
            json_payload["variables"] = variables
        try:
            r = requests.post(self.host, json=json_payload)
            response_json = r.json()
        except requests.exceptions.RequestException as e:
            if self.raise_on_error:
                raise e
            else:
                log.warning(f"GraphQL request failed: {e}")
                return None

        # Check response for errors returned.
        if is_gql_obj_payload:
            try:
                self._verify_response(response_json)
            except PayloadVerificationError as e:
                if self.raise_on_error:
                    raise
                else:
                    log.warning(
                        f"GraphQL query or mutation failed payload verification: {e.message}"
                    )
                    return response_json

        # If types were included in the payload, check that the types of the response match the types in the payload.
        typed_response = self._check_types(payload, response_json)

        return typed_response

    @staticmethod
    def _verify_response(response: dict):
        """
        Verify that the response is a valid JSON response and does not contain any errors.
        Args:
            response (dict): The response from the GraphQL server.
        """
        if response.get("errors"):
            raise PayloadVerificationError(response["errors"], response)

        if not response.get("data"):
            raise PayloadVerificationError("Response does not contain data.", response)

    def _check_types(self, payload, response_json) -> dict:
        """
        Args:
          payload: The query or mutation that will be sent to the GraphQL server.
          response_json: The response from the GraphQL server.
        """
        pass
