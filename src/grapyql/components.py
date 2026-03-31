from typing import Type


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
        self._fields: set = set()

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
        string_fields = {Field(f) for f in args if isinstance(f, str)}
        field_objects = {f for f in args if isinstance(f, Field)}
        gql_objects = {f for f in args if isinstance(f, GqlObject)}
        self._fields.update(string_fields)
        self._fields.update(field_objects)
        self._fields.update(gql_objects)
        return self

    def remove_fields(self, *args):
        """
        Removes fields from the GQL object.
        """
        # TODO (jw): I don't like that this doesn't take advantage of set lookup, but
        #  the object would have to be recreated with all fields identical (not possible)
        #  to get the same hash or the hash/eq dunder methods would have to be changed to
        #  be more tolerant so we could re-create the object with just the name and look
        #  up the object from there. This is something to consider for the future.
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
