from typing import Type

from grapyql.const import INDENT

__all__ = ["Field", "GqlObject", "Function"]


class Function:
    """
    Mutation Function. Similar to GqlObject.
    """

    def __init__(self, function_name, **kwargs):
        self.function_name = function_name
        self.variables = kwargs

    def fields(self, *args, **kwargs):
        pass


class Field:
    """
    Attributes inside an object.
    """

    def __repr__(self):
        return f"GqlField({self.field_name})"

    def __init__(
        self,
        field_name: str,
        field_type: Type | str | None = None,
        required=False,
    ):
        self.field_name: str = field_name
        self.field_type: Type | str | None = field_type
        self.required: bool = required
        self.value = None

    def __hash__(self):
        return hash((self.field_name, self.field_type, self.required))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.field_name == other
        if not isinstance(other, Field):
            return False
        return hash(self) == hash(other)


class GqlObject:
    """
    Base query object. Contains fields.
    """

    def __init__(
        self,
        obj_name: str,
        obj_type: Type | str | None = None,
        filters: dict | None = None,
        required=False,
    ):
        self.obj_name: str = obj_name
        self.obj_type: str | type | None = obj_type
        self.required: bool = required
        self.filters: dict = filters or dict()
        self._fields: list = list()

    def __repr__(self):
        return f"GqlObj({self.obj_name})"

    def __getitem__(self, item):
        """
        Add functionality to get fields through "obj['field']" notation.
        """
        for k in self._fields:
            if k == item:
                return k
        raise AttributeError(f"Field '{item}' not found in GqlObject '{self.obj_name}'")

    def __getattr__(self, item):
        """
        Add functionality to get fields through "obj.field" notation.
        """
        return self[item]

    def __hash__(self):
        return hash(
            (
                self.obj_name,
                self.obj_type,
                self.required,
                tuple(self.filters.keys()),
                tuple(self._fields),
            )
        )

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, str):
            return self.obj_name == other
        if isinstance(other, GqlObject):
            return hash(self) == hash(other)
        return False

    def fields(self, *args):
        """
        Adds fields that will be returned after the request to the GQL server is made.

        Fields are added to the GQL object. This does not take out existing fields
        that were already on the GQL object.
        """
        for f in args:
            field = f
            if isinstance(f, str):
                field = Field(f)
            self._fields.append(field)
        return self

    def remove_fields(self, *args):
        """
        Removes fields from the GQL object.
        """
        for f in args:
            for k in self._fields:
                if k == f:
                    self._fields.remove(k)
                    break

    def pop(self, field_name, **kwargs):
        """
        Removes a field from the GQL object and returns it.

        Args:
            field_name (str): Name of the field to remove.
            kwargs (dict): Include 'default' in kwargs to return if field is not found.
        """
        if field_name in self._fields:
            field = self[field_name]
            self.remove_fields(field)
            return field
        else:
            if "default" in kwargs:
                return kwargs["default"]
            raise KeyError(
                f"Field '{field_name}' not found in object '{self.obj_name}'"
            )

    @staticmethod
    def _json_type(value):
        """
        Convert the value to json type for the GQL query.

        Args:
            value: Value to convert to json type.

        Returns: JSON compatible value.
        """
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if value is None:
            return "null"
        return f'"{value}"'

    def to_gql(self, _curr_ind=0):
        """
        Translates the GQL object into a string.

        Args:
            _curr_ind: Internal use, tracks how much indent should be used.

        Returns: Translated string.
        """
        output = f"{INDENT * _curr_ind}{self.obj_name}"
        if self.filters:
            output += "("
            filters = list()
            for k, v in self.filters.items():
                filters.append(f"{k}: {self._json_type(v)}")
            output += ", ".join(filters) + "){\n"
        else:
            output += "{\n"
        for f in self._fields:
            if isinstance(f, GqlObject):
                obj_str = f.to_gql(_curr_ind=_curr_ind + 1)
                output += obj_str
            else:
                output += (INDENT * (_curr_ind + 1)) + f.field_name + "\n"
        output += INDENT * _curr_ind + "}"
        if _curr_ind != 0:
            output += "\n"
            return output
        return output
