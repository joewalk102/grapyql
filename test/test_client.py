from grapyql.client import GqlClient


class TestGqlClientDictToQuery:
    def test_single_query_var(self):
        client = GqlClient("localhost")
        query = client.dict_to_query(
            query_struct={
                "user": {
                    "active": bool,
                    "fname": str,
                    "invoice": {
                        "cost": str,
                        "address": {
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
            },
            query_var={"user_id": "130897273"}
        )
        assert '(user_id: "130897273")' in query

    def test_multiple_query_var(self):
        client = GqlClient("localhost")
        query = client.dict_to_query(
            query_struct={
                "user": {
                    "active": bool,
                    "fname": str,
                    "invoice": {
                        "cost": str,
                        "address": {
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
            },
            query_var={"user_id": "130897273", "active": True}
        )
        assert '(user_id: "130897273", active: true)' in query

    def test_output_structure_matches_query_struct(self):
        client = GqlClient("localhost")
        query = client.dict_to_query(
            query_struct={
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
            },
            query_var={"user_id": "130897273"}
        )
        assert query ==(
            '{\n'
            '  user(user_id: "130897273") {\n'
            '    active\n'
            '    fname\n'
            '    invoice {\n'
            '      cost\n'
            '      address {\n'
            '        street1\n'
            '        street2\n'
            '        city\n'
            '        state\n'
            '        zipcode\n'
            '        }\n'
            '      items {\n'
            '        display_name\n'
            '        sku\n'
            '        }\n'
            '      }\n'
            '    }\n'
            '}'
        )
