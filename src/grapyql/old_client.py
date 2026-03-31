"""

SOON TO BE DISCARDED. Kept for reference only.

"""


from typing import Union, Optional

import requests
from requests import JSONDecodeError

from grapyql.errors import GraphQLResponseError


class GqlClient:
    """
    Args:
      host: The host of the GraphQL server.
      force_typing: If True, the client will force the typing of the values to the correct type. (only
        works for dictionary query input, not string queries)
      raise_on_error: If there is an error in the request, either raise an error
        if this value is True, or return None if the value is False.
    """

    def __init__(self, host, force_typing: bool = False, raise_on_error: bool = True):
        self.host: str = host
        self.force_typing = force_typing
        self.raise_on_error = raise_on_error

    @staticmethod
    def _value_py_to_js(value):
        """
        Convert a Python value to a JavaScript value (None -> null).
        """
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return f"{str(value).lower()}"
        elif value is None:
            return "null"
        raise ValueError(f"Value not supported: `{value}`")

    def dict_to_query(self, query_struct: dict, _start: bool = True) -> str:
        """
        Convert a dictionary structure to a GraphQL Query

        Args:
          query_struct: Structure of the graphql query, expressed in dictionary form.
          _start: If this is the first call to the function, this should be True. (used for recursion)

        Returns: GraphQL query string is returned that can be sent to the GraphQL server.

        Example query_var:
        {"$user_id": "130897273"}

        Example query_struct:
        {
          "user": {
            Gql.args: {"user_id", "$user_id"}
            "active": bool,
            "fname": str,
            "invoice": {
              "cost": str,
              "address":{
                "street1": str,
                "street2": str,
                "city": str,
                "state": str,
                "zipcode": int
              },
              "items": {
                "display_name": str,
                "sku": str,
              }
            }
          }
        }
        """
        # first new line needs to have an outer dictionary to encapsulate the query.
        output = "{\n" if _start else ""
        for k, v in query_struct.items():
            if k == "__args__" or k == GQL.args:
                # args are not to be included in the query as a normal field.
                continue
            if isinstance(v, dict):
                # If the value is a dictionary, then it is a nested field. But first check if it has
                # query variables that need to be added to the current field.
                if "__args__" in v or GQL.args in v:
                    # Add query variables to first row.
                    output += f"{k}("
                    qv_args = list()
                    for qv_k, qv_v in v["__args__"].items():
                        # add every query_var
                        qv_args.append(f"{qv_k}: {self._value_py_to_js(qv_v)}")
                    output += ", ".join(qv_args) + ") {\n  "
                    # continue with nested fields in `v`
                    output += self.dict_to_query(v, _start=False)
                    break
                # Add any other nested fields to the next level.
                output += f"{k} {self.dict_to_query(v)}"
            else:
                # If the value is not a dictionary, then the key can just be added to the query.
                output += k
            output += "\n"
        output = "\n  ".join(output.split("\n"))
        # remove the last two characters from the output so the closing bracket is lined up.
        output = output[:-2]
        output += "}" if _start else "}\n"
        return output

    def _request_to_mutation(self, mutation: str, variables: dict = None):
        """
        Args:
          mutation: The mutation that will be sent to the GraphQL server.
          variables: The variables that will be used in the mutation.

        Example mutation:
        mutation {
          createUser(
            fname: "John",
            lname: "Doe",
            email: "john.doe@someone.com",
          ):
          {
                user_id
                fname
                lname
                email
          }
        }

        Example Mutation Structure:
        {
          "createUser": {
            "fname": "John",
            "lname": "Doe",
            "email": "john.doe@someone.com",
          }
          "__response_vars__": {
            "user_id": int,
            "fname": str,
            "lname": str,
            "email": str,
          }
        }
        """
        pass

    def def _request(self, payload: str, variables: dict = None):
        """
        Args:
          payload: The query or mutation that will be sent to the GraphQL server.
          variables: The variables that will be used in the query or mutation
        """
        json_payload = {"query": payload}
        if variables:
            json_payload["variables"] = variables
        try:
            r = requests.post(self.host, json=json_payload)
        except requests.exceptions.RequestException as e:
            if self.raise_on_error:
                raise e
            else:
                return None
        return r

    def _verify_response(self, response: requests.Response):
        """
        Verify that the response code is valid.

        Args:
          response: The response from the GraphQL server.
        """
        if response.status_code != 200:
            if self.raise_on_error:
                raise ValueError(f"Error in response: {response.text}")
            return None
        return response

    def _verify_json_response(self, response: requests.Response):
        """
        Verify that the response is a valid JSON response and does not contain any errors.

        Args:
            response: The response from the GraphQL server.
        """
        response = self._verify_response(response)
        if response is None:
            return None
        try:
            json_response = response.json()
        except JSONDecodeError as e:
            if self.raise_on_error:
                raise e
            return
        if "errors" in json_response:
            if self.raise_on_error:
                raise GraphQLResponseError(
                    f"Error in response:",
                    json_response["errors"],
                )
            return response.text
        return json_response

    def query(
        self,
        query: Union[str, dict],
        variables: Optional[dict] = None,
        return_dict: Optional[bool] = True,
    ):
        """
        Perform the specified query.

        Args:
            query: The query text that will be sent to the GraphQL server.
            variables: The variables that will be used in the query.
            return_dict: If true, a dictionary of the results will be returned. Otherwise,
              the raw text of the response will be returned. Option is True by default.
        """
        if isinstance(query, dict):
            query = self.dict_to_query(query)
        r = self._request(query, variables)
        if return_dict:
            return r.json()["data"]
        return r.text

    def mutation(
        self,
        mutation: str,
        variables: Optional[dict],
        return_dict: Optional[bool] = True,
    ):
        """
        Perform the specified mutation.

        Args:
          mutation: The mutation text that will be sent to the GraphQL server.
          variables: The variables that will be used in the mutation.
          return_dict: If true, a dictionary of the results will be returned. Otherwise,
            the raw text of the response will be returned. Option is True by default.
        """
        r = self._request(mutation, variables)
        if return_dict:
            try:
                return r.json()["data"]
            except JSONDecodeError as e:
                if self.raise_on_error:
                    raise e
                return None
        else:
            return r.text
