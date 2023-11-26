import os
import requests
from behave import given, when, then

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the server is started')
def step_impl(context):
    context.base_url = os.getenv(
        'BASE_URL',
        'http://localhost:8000'
    )
    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200
 
@given('the following products')
def step_impl(context):
    """ Delete all Products and load new ones """

    # List all of the products and delete them one by one
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for products in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{products['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new products
    for row in context.table:
        payload = {
            "name": row['name'],
            "description": row['description'],
            "price": row['price'],
            "available": row['available'] in ['True', 'true', '1'],
            "image_url": row['image_url'],
            "category": row['category']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert(context.resp.status_code == HTTP_201_CREATED)


@when('I visit the "home page"')
def step_impl(context):
    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200
   

@then('I should see "{message}"')
def step_impl(context, message):
   assert message in str(context.resp.text)

@then('I should not see "{message}"')
def step_impl(context, message):
   assert message not in str(context.resp.text)
