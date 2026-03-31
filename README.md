# grapyql
A Pythonic GraphQL Client

## Purpose
The purpose of this project is to provide a simple and efficient GraphQL 
client for Python developers. It allows developers to easily interact with 
GraphQL APIs in a Pythonic way, making it easier to fetch and manipulate data.

## Example Usage
Python with grapyql:
```python
from grapyql import GqlClient
from grapyql import GqlObject as O

client = GqlClient("https://api.example.com/graphql")

user = O("user", filters={"active": True}).fields(
    "id",
    "name",
    "email",
)

results = client.execute(user)
```
This produces a GQL Query like:
```graphql
query ($active: Boolean) {
  user(active: $active) {
    id
    name
    email
  }
}
```
with variables:
```json
{
  "active": true
}
```
