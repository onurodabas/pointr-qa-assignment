"""
Step definitions for building.feature
"""

from behave import given, when, then
import requests


@given('that site has a building')
def step_create_building_beforehand(context):
    """Precondition: create a building under the previously created site."""
    assert hasattr(context, 'created_site_id'), \
        "A site must be created first"

    row = context.table.rows[0]
    data = {
        'name': row['name'],
        'site_id': context.created_site_id,
        'floors': int(row['floors'])
    }

    url = f"{context.base_url}/api/buildings"
    response = requests.post(url, json=data)

    assert response.status_code == 201, \
        f"Failed to create building: {response.status_code} - {response.text}"

    context.created_building_id = response.json()['id']


@when('I send a POST request to "{endpoint}" with that site\'s ID and')
def step_post_building_with_site_id(context, endpoint):
    """Send a building creation request, auto-injecting the site_id from context."""
    assert hasattr(context, 'created_site_id'), \
        "A site must be created first"

    data = {'site_id': context.created_site_id}
    for row in context.table:
        field = row['field']
        value = row['value']
        try:
            value = int(value)
        except ValueError:
            pass
        data[field] = value

    url = f"{context.base_url}{endpoint}"
    context.response = requests.post(url, json=data)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a GET request for that building')
def step_get_created_building(context):
    building_id = context.created_building_id
    url = f"{context.base_url}/api/buildings/{building_id}"
    context.response = requests.get(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a DELETE request for that building')
def step_delete_created_building(context):
    building_id = context.created_building_id
    url = f"{context.base_url}/api/buildings/{building_id}"
    context.response = requests.delete(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@then('when I GET that building again I should receive {status_code:d}')
def step_get_deleted_building(context, status_code):
    building_id = context.created_building_id
    url = f"{context.base_url}/api/buildings/{building_id}"
    response = requests.get(url)

    assert response.status_code == status_code, \
        f"After delete: expected {status_code}, got {response.status_code}"
