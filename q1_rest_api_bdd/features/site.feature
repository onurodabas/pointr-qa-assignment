Feature: Site Management
  As a system administrator
  I want to manage hospital sites
  So that I can organize different locations

  Background:
    Given the API is running at "http://localhost:5000"

  Scenario: Create site with valid data
    When I send a POST request to "/api/sites" with:
      | field       | value                |
      | name        | Test Hospital        |
      | description | Main campus for test |
    Then the response status code should be 201
    And the response should contain field "id"
    And the response should contain field "name" with value "Test Hospital"
    And the response should contain field "description" with value "Main campus for test"

  Scenario: Create site with only required field
    When I send a POST request to "/api/sites" with:
      | field | value        |
      | name  | Minimal Site |
    Then the response status code should be 201
    And the response should contain field "id"
    And the response should contain field "name" with value "Minimal Site"
    And the response should contain field "description" with value ""

  Scenario: Attempt to create site without name field
    When I send a POST request to "/api/sites" with:
      | field       | value            |
      | description | Only description |
    Then the response status code should be 400
    And the response should contain field "error"

  Scenario: Attempt to create site with empty body
    When I send a POST request to "/api/sites" with empty body
    Then the response status code should be 400
    And the response should contain field "error"

  Scenario: Retrieve existing site by ID
    Given a site exists with:
      | name         | description      |
      | Main Campus  | Central location |
    When I send a GET request for that site
    Then the response status code should be 200
    And the response should contain field "id"
    And the response should contain field "name" with value "Main Campus"
    And the response should contain field "description" with value "Central location"

  Scenario: Attempt to retrieve non-existent site
    When I send a GET request to "/api/sites/non-existent-uuid-123"
    Then the response status code should be 404
    And the response should contain field "error"

  Scenario: Delete existing site
    Given a site exists with:
      | name              | description |
      | Site To Delete    | For testing |
    When I send a DELETE request for that site
    Then the response status code should be 200
    And the response should contain field "message"
    And when I GET that site again I should receive 404

  Scenario: Attempt to delete non-existent site
    When I send a DELETE request to "/api/sites/non-existent-uuid-999"
    Then the response status code should be 404
