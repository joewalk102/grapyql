"""
from grapyql import Field as F
from grapyql import GqlObject as O

useruser = O("user", filters={"active": True}).fields(
  F("active", bool),
  "f_name",
  "l_name",
  O("invoice").fields(
    "cost",
    O("address", filters={"loc_type": "Primary"}).fields(
      "street",
      "city",
      "state",
      F("zip_code", int, True),  # Mark field as integer and required.
    ),
    O("items").fields(
      "display_name",
      "sku",
    )
  )
)
"""

__all__ = ["Query", "Mutation"]


class RootOperation:
    _OP_TYPE = None

    def to_gql(self, minified=False):
        pass

    def verify_response(self, response):
        pass


class Query(RootOperation):
    """
    Single Query:
    query HeroNameAndFriends {
      hero {
        name
        friends {
          name
        }
      }
    }

    Multiple Queries:
    query {
      empireHero: hero(episode: EMPIRE) {
        name
      }
      jediHero: hero(episode: JEDI) {
        name
      }
    }
    """

    _OP_TYPE = "query"

    def __init__(self, **objects):
        self.objects: dict = objects


class Mutation(RootOperation):
    """
    Single Mutation:
    mutation DeleteStarship($id: ID!) {
      deleteStarship(id: $id)
    }

    Multiple Mutations:
    mutation {
      firstShip: deleteStarship(id: "3001")
      secondShip: deleteStarship(id: "3002")
    }
    """

    _OP_TYPE = "mutation"

    def __init__(self, **functions):
        self.functions: dict = functions
