"""
Step definitions for level.feature
"""

from behave import when, then
import requests


@when('I send a POST request to "{endpoint}" with that building\'s ID and single level')
def step_post_single_level(context, endpoint):
    """Import a single level (sent as a JSON object, not a list)."""
    assert hasattr(context, 'created_building_id'), \
        "A building must be created first"

    row = context.table.rows[0]
    data = {
        'name': row['name'],
        'building_id': context.created_building_id
    }

    if 'floor_number' in row.headings:
        data['floor_number'] = int(row['floor_number'])

    url = f"{context.base_url}{endpoint}"
    context.response = requests.post(url, json=data)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a POST request to "{endpoint}" with that building\'s ID and multiple levels')
def step_post_multiple_levels(context, endpoint):
    """Import several levels at once (sent as a JSON list)."""
    assert hasattr(context, 'created_building_id'), \
        "A building must be created first"

    levels = []
    for row in context.table:
        level_data = {
            'name': row['name'],
            'building_id': context.created_building_id
        }
        if 'floor_number' in row.headings:
            level_data['floor_number'] = int(row['floor_number'])
        levels.append(level_data)

    url = f"{context.base_url}{endpoint}"
    context.response = requests.post(url, json=levels)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a POST request to "{endpoint}" with that building\'s ID and invalid level')
def step_post_invalid_level(context, endpoint):
    """Send a level missing the required 'name' field."""
    assert hasattr(context, 'created_building_id'), \
        "A building must be created first"

    row = context.table.rows[0]
    data = {'building_id': context.created_building_id}

    if 'floor_number' in row.headings:
        data['floor_number'] = int(row['floor_number'])

    url = f"{context.base_url}{endpoint}"
    context.response = requests.post(url, json=data)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a POST request to "{endpoint}" with that building\'s ID and mixed levels')
def step_post_mixed_levels(context, endpoint):
    """
    Send a list with a mix of valid and invalid level entries to verify
    the API's partial-success behavior. The 'status' column in the table
    is documentation only and is not sent to the API.
    """
    assert hasattr(context, 'created_building_id'), \
        "A building must be created first"

    levels = []
    for row in context.table:
        level_data = {'building_id': context.created_building_id}

        if row['name']:
            level_data['name'] = row['name']
        if 'floor_number' in row.headings:
            level_data['floor_number'] = int(row['floor_number'])

        levels.append(level_data)

    url = f"{context.base_url}{endpoint}"
    context.response = requests.post(url, json=levels)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


# {field:w} restricts to word characters to avoid pattern ambiguity
@then('the response should have a "{field:w}" list')
def step_check_list_exists(context, field):
    assert context.response_json is not None, "Response is not JSON"
    assert field in context.response_json, \
        f"'{field}' list not found in response: {context.response_json}"
    assert isinstance(context.response_json[field], list), \
        f"'{field}' is not a list"


@then('the "{field:w}" list should have {count:d} item')
def step_check_list_count_singular(context, field, count):
    actual = len(context.response_json[field])
    assert actual == count, \
        f"'{field}' list: expected {count} item, got {actual}"


@then('the "{field:w}" list should have {count:d} items')
def step_check_list_count_plural(context, field, count):
    actual = len(context.response_json[field])
    assert actual == count, \
        f"'{field}' list: expected {count} items, got {actual}"


@then('the "{field:w}" list should be empty')
def step_check_list_empty(context, field):
    actual = len(context.response_json[field])
    assert actual == 0, \
        f"'{field}' list should be empty, but has {actual} items"


@then('the first item in "{field:w}" should have "{subfield:w}" with value "{value}"')
def step_check_first_element_field_string(context, field, subfield, value):
    items = context.response_json[field]
    assert len(items) > 0, f"'{field}' list is empty"

    actual = items[0].get(subfield)
    assert actual == value, \
        f"'{field}[0].{subfield}': expected='{value}', got='{actual}'"


@then('the first item in "{field:w}" should have "{subfield:w}" with value {value:d}')
def step_check_first_element_field_int(context, field, subfield, value):
    items = context.response_json[field]
    assert len(items) > 0, f"'{field}' list is empty"

    actual = items[0].get(subfield)
    assert actual == value, \
        f"'{field}[0].{subfield}': expected={value}, got={actual}"
