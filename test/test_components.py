from grapyql import GqlObject as O
from grapyql import Field as F


class TestGqlObject:
    @staticmethod
    def _make_test_obj():
        g_obj = O("user", filters={"active": True}).fields(
            F("active", bool),
            "f_name",
            "l_name",
            O("invoice").fields(
                "cost",
                O("address", filters={"loc_type": "Primary", "country": "USA"}).fields(
                    "street",
                    "city",
                    "state",
                    "country",
                    F("zip_code", int, True),
                ),
                O("items").fields(
                    "display_name",
                    "sku",
                ),
            ),
        )
        return g_obj


class TestGqlObjectFields(TestGqlObject):
    def test_add_fields(self):
        """
        Test that fields were attached to the object and nested objects correctly.
        """
        g_obj = self._make_test_obj()
        assert hasattr(g_obj, "f_name")
        assert isinstance(
            g_obj.f_name, F
        )  # f_name field was converted from str to Field object.
        assert hasattr(g_obj.invoice.address, "country")

    def test_add_more_fields(self):
        """
        Test that adding more fields doesn't take away existing fields and that the new fields are added correctly.
        """
        g_obj = self._make_test_obj()
        g_obj.fields("full_name")
        assert hasattr(g_obj, "full_name")
        assert hasattr(g_obj.invoice.items, "sku")

    def test_remove_fields(self):
        """
        Test that fields were removed from the object. Other fields are not affected.
        """
        g_obj = self._make_test_obj()
        g_obj.remove_fields("f_name", "l_name")
        assert not hasattr(g_obj, "f_name")
        assert not hasattr(g_obj, "l_name")
        assert hasattr(g_obj.invoice.address, "street")

    def test_pop_fields(self):
        """
        Test that pop action returns the correct field and is no longer in the object.
        """
        g_obj = self._make_test_obj()
        g_obj.l_name.value = "Smith"

        last_name = g_obj.pop("l_name")

        assert hasattr(g_obj, "f_name")
        assert not hasattr(g_obj, "l_name")
        assert hasattr(g_obj.invoice.address, "street")

        assert last_name.value == "Smith"  # Attached value is still on the object


class TestGqlObjectToGql(TestGqlObject):

    def test_to_gql(self):
        g_obj = self._make_test_obj()
        output = g_obj.to_gql()
        assert output == (
            "user(active: true){\n"
            "  active\n"
            "  f_name\n"
            "  l_name\n"
            "  invoice{\n"
            "    cost\n"
            '    address(loc_type: "Primary", country: "USA"){\n'
            "      street\n"
            "      city\n"
            "      state\n"
            "      country\n"
            "      zip_code\n"
            "    }\n"
            "    items{\n"
            "      display_name\n"
            "      sku\n"
            "    }\n"
            "  }\n"
            "}"
        )
