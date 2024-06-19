from typing import Union

import requests


class GqlClient:
    def __init__(self, host, force_typing: bool = False):
        self.host: str = host
        self.force_typing = force_typing

    @staticmethod
    def _value_py_to_js(value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return f"{str(value).lower()}"
        elif value is None:
            return "null"
        raise ValueError(f"Value not supported: `{value}`")

    def dict_to_query(
        self, query_struct: dict, force_typing: bool = False, _start: bool = True
    ) -> str:
        """
        Convert a dictionary structure to a GraphQL Query

        Args:
            query_struct: Structure of the graphql query, expressed in dictionary form.
            force_typing: Force the results to conform to the types provided. If they don't
              raise an error. If this option is disabled, the values are ignored.
            _start: If this is the first call to the function, this should be True. (used for recursion)

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
            if k == "__args__":
                # args are not to be included in the query as a normal field.
                continue
            if isinstance(v, dict):
                # If the value is a dictionary, then it is a nested field. But first check if it has
                # query variables that need to be added to the current field.
                if "__args__" in v:
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

    def query(
        self,
        query: Union[str, dict] = "",
        return_dict: bool = True,
        raise_on_error: bool = True,
    ):
        """
        Perform the specified query.

        Args:
            query: The query text that will be sent to the GraphQL server.
            return_dict: If true, a dictionary of the results will be returned. Otherwise,
              the raw text of the response will be returned. Option is True by default.
            raise_on_error: If there is an error in the request, either raise an error
              if this value is True, or return None if the value is False.
        """
        if isinstance(query, dict):
            query = self.dict_to_query(query)
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
