from copy import deepcopy

from grapyql.client import GqlClient


class TestGqlClientDictToQuery:
    client = GqlClient("localhost")
    default_struct = {
        "user": {
            "__args__": {"user_id": "$user_id"},
            "active": bool,
            "fname": str,
            "invoices": {
                "__args__": {"limit": "$limit"},
                "cost": str,
                "address": {
                    "street1": str,
                    "street2": str,
                    "city": str,
                    "state": str,
                    "zipcode": int,
                },
                "items": {
                    "display_name": str,
                    "sku": str,
                },
            },
        }
    }

    def test_single_query_var(self):
        struct = deepcopy(self.default_struct)
        struct["user"]["__args__"] = {"user_id": "130897273"}
        query = self.client.dict_to_query(query_struct=struct)
        assert '(user_id: "130897273")' in query

    def test_multiple_query_var(self):
        struct = deepcopy(self.default_struct)
        struct["user"]["__args__"] = {"user_id": "130897273", "active": True}
        query = self.client.dict_to_query(query_struct=struct)
        assert '(user_id: "130897273", active: true)' in query

    def test_output_structure_matches_query_struct(self):
        query = self.client.dict_to_query(query_struct=self.default_struct)
        assert query == (
            "{\n"
            '  user(user_id: "$user_id") {\n'
            "    active\n"
            "    fname\n"
            '    invoices(limit: "$limit") {\n'
            "      cost\n"
            "      address {\n"
            "        street1\n"
            "        street2\n"
            "        city\n"
            "        state\n"
            "        zipcode\n"
            "      }\n"
            "      items {\n"
            "        display_name\n"
            "        sku\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}"
        )
