"""
Step definitions for site.feature
"""

from behave import given, when, then
import requests


@given('the API is running at "{url}"')
def step_api_base_url(context, url):
    context.base_url = url


@when('I send a POST request to "{endpoint}" with')
def step_post_with_table(context, endpoint):
    """Send POST request with a body built from the Gherkin table."""
    data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Convert numeric strings to int (table values are always strings)
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


@when('I send a POST request to "{endpoint}" with empty body')
def step_post_empty_body(context, endpoint):
    """
    Send a POST with no JSON payload.
    We explicitly set the Content-Type header so the API treats this as
    a malformed JSON request (and returns 400) rather than 415 Unsupported
    Media Type, which is what happens when no Content-Type is sent at all.
    """
    url = f"{context.base_url}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    context.response = requests.post(url, headers=headers, data='')

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@then('the response status code should be {status_code:d}')
def step_check_status_code(context, status_code):
    actual = context.response.status_code
    assert actual == status_code, \
        f"Expected status code {status_code}, got {actual}"


# Note: {field:w} restricts field names to word characters (letters, digits, _).
# Without it, the parser is greedy and these patterns become ambiguous,
# causing AmbiguousStep errors with newer Behave versions.
@then('the response should contain field "{field:w}"')
def step_check_field_exists(context, field):
    assert context.response_json is not None, "Response is not JSON"
    assert field in context.response_json, \
        f"'{field}' not found in response: {context.response_json}"


# Specific step for empty string values, since parse's {value} requires
# at least one character. This pattern matches the literal `""`.
@then('the response should contain field "{field:w}" with value ""')
def step_check_field_value_empty(context, field):
    actual = context.response_json.get(field)
    assert actual == '', \
        f"'{field}': expected empty string, got '{actual}'"


@then('the response should contain field "{field:w}" with value "{value}"')
def step_check_field_value_string(context, field, value):
    actual = context.response_json.get(field)
    assert actual == value, \
        f"'{field}': expected='{value}', got='{actual}'"


@then('the response should contain field "{field:w}" with value {value:d}')
def step_check_field_value_int(context, field, value):
    actual = context.response_json.get(field)
    assert actual == value, \
        f"'{field}': expected={value}, got={actual}"


@given('a site exists with')
def step_create_site_beforehand(context):
    """Precondition: create a site and remember its id for later steps."""
    row = context.table.rows[0]
    data = {
        'name': row['name'],
        'description': row['description']
    }

    url = f"{context.base_url}/api/sites"
    response = requests.post(url, json=data)

    assert response.status_code == 201, \
        f"Failed to create site: {response.status_code} - {response.text}"

    context.created_site_id = response.json()['id']


@when('I send a GET request for that site')
def step_get_created_site(context):
    site_id = context.created_site_id
    url = f"{context.base_url}/api/sites/{site_id}"
    context.response = requests.get(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a GET request to "{endpoint}"')
def step_get_request(context, endpoint):
    url = f"{context.base_url}{endpoint}"
    context.response = requests.get(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a DELETE request for that site')
def step_delete_created_site(context):
    site_id = context.created_site_id
    url = f"{context.base_url}/api/sites/{site_id}"
    context.response = requests.delete(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@when('I send a DELETE request to "{endpoint}"')
def step_delete_request(context, endpoint):
    url = f"{context.base_url}{endpoint}"
    context.response = requests.delete(url)

    try:
        context.response_json = context.response.json()
    except ValueError:
        context.response_json = None


@then('when I GET that site again I should receive {status_code:d}')
def step_get_deleted_site(context, status_code):
    """Verify the site is actually gone after a delete."""
    site_id = context.created_site_id
    url = f"{context.base_url}/api/sites/{site_id}"
    response = requests.get(url)

    assert response.status_code == status_code, \
        f"After delete: expected {status_code}, got {response.status_code}"
