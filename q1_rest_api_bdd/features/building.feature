Feature: Building Management
  As a system administrator
  I want to manage buildings within sites
  So that I can organize campus structure

  Background:
    Given the API is running at "http://localhost:5000"

  Scenario: Create building with valid data
    Given a site exists with:
      | name         | description  |
      | Main Campus  | Test campus  |
    When I send a POST request to "/api/buildings" with that site's ID and:
      | field  | value  |
      | name   | Block A|
      | floors | 5      |
    Then the response status code should be 201
    And the response should contain field "id"
    And the response should contain field "name" with value "Block A"
    And the response should contain field "site_id"
    And the response should contain field "floors" with value 5

  Scenario: Create building without floors (default value)
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    When I send a POST request to "/api/buildings" with that site's ID and:
      | field | value   |
      | name  | Block B |
    Then the response status code should be 201
    And the response should contain field "floors" with value 1

  Scenario: Attempt to create building without name
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    When I send a POST request to "/api/buildings" with that site's ID and:
      | field  | value |
      | floors | 3     |
    Then the response status code should be 400
    And the response should contain field "error"

  Scenario: Attempt to create building without site_id
    When I send a POST request to "/api/buildings" with:
      | field | value   |
      | name  | Block C |
    Then the response status code should be 400
    And the response should contain field "error"

  Scenario: Attempt to create building with invalid site_id
    When I send a POST request to "/api/buildings" with:
      | field   | value                |
      | name    | Block D              |
      | site_id | non-existent-site-id |
    Then the response status code should be 404
    And the response should contain field "error"

  Scenario: Retrieve building by ID
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block E | 7      |
    When I send a GET request for that building
    Then the response status code should be 200
    And the response should contain field "name" with value "Block E"
    And the response should contain field "floors" with value 7

  Scenario: Attempt to retrieve non-existent building
    When I send a GET request to "/api/buildings/non-existent-building-123"
    Then the response status code should be 404

  Scenario: Delete building
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block F | 2      |
    When I send a DELETE request for that building
    Then the response status code should be 200
    And when I GET that building again I should receive 404
