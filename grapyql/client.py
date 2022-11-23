import requests


class GqlClient:
    def __init__(self, host, force_typing: bool = False):
        self.host: str = host
        self.force_typing = force_typing

    def _value_py_to_js(self, value):
        if isinstance(value, str):
            return f"\"{value}\""
        elif isinstance(value, bool):
            return f"{str(value).lower()}"
        elif value is None:
            return "null"
        raise ValueError(f"Value not supported: `{value}`")

    def dict_to_query(self, query_struct: dict, query_var: dict = None, force_typing: bool = False) -> str:
        """
        Convert a dictionary structure to a GraphQL Query

        Args:
            query_struct: Structure of the graphql query, expressed in dictionary form.
            query_var: Search parameters for the graphql query.
            force_typing: Force the results to conform to the types provided. If they don't
              raise an error. If this option is disabled, the values are ignored.

        Returns: GraphQL query string is returned that can be sent to the GraphQL server.

        Example query_var:
        {"user_id": "130897273"}

        Example query_struct:
        {
          "user": {
            "active": bool,
            "fname": str,
            "invoice": {
              "cost": str,
              "address"{
                "street1": str,
                "street2": str,
                "city": str,
                "state": str,
                "zipcode": int
              }
              "items": {
                "display_name": str,
                "sku": str,
              }
            }
          }
        }
        """
        output = "{\n"
        for k, v in query_struct.items():
            if isinstance(v, dict):
                if query_var is not None:
                    # Add query variables to first row.
                    output += f"{k}("
                    for qv_k, qv_v in query_var.items():
                        # add every query_var
                        output += f"{qv_k}: {self._value_py_to_js(qv_v)}"
                        output += ", "
                    # Remove space and comma from last one and continue with nested
                    # fields in `v`
                    output = output[:-2] + f") {self.dict_to_query(v)}"
                    break
                # else: if no query_var (must be nested call)
                output += f"{k} {self.dict_to_query(v)}"
            else:
                output += k
            output += "\n"
        output = "\n  ".join(output.split("\n"))
        output += "}"
        if query_var is not None:
            output = output[:-1] + "\n}"
        return output

    def query(self, query: str = "", return_dict: bool = True, raise_on_error: bool = True):
        """
        Perform the specified query.

        Args:
            query: The query text that will be sent to the GraphQL server.
            return_dict: If true, a dictionary of the results will be returned. Otherwise,
              the raw text of the response will be returned. Option is True by default.
            raise_on_error: If there is an error in the request, either raise an error
              if this value is True, or return None if the value is False.
        """
        try:
            r = requests.post(self.host, json={"query": query})
        except requests.exceptions.RequestException as e:
            if raise_on_error:
                raise e
            else:
                return None
        if return_dict:
            return r.json()["data"]
        return r.text
