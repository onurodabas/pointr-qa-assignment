Feature: Level Import Operations
  As a system administrator
  I want to import floor levels into buildings
  So that I can prepare data for indoor navigation

  Background:
    Given the API is running at "http://localhost:5000"

  Scenario: Import single level
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block A | 3      |
    When I send a POST request to "/api/levels" with that building's ID and single level:
      | name         | floor_number |
      | Ground Floor | 0            |
    Then the response status code should be 201
    And the response should have a "created" list
    And the "created" list should have 1 item
    And the first item in "created" should have "name" with value "Ground Floor"
    And the "errors" list should be empty

  Scenario: Import multiple levels
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block B | 5      |
    When I send a POST request to "/api/levels" with that building's ID and multiple levels:
      | name         | floor_number |
      | Ground Floor | 0            |
      | First Floor  | 1            |
      | Second Floor | 2            |
    Then the response status code should be 201
    And the "created" list should have 3 items
    And the "errors" list should be empty

  Scenario: Import level without floor_number (default value)
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block C | 2      |
    When I send a POST request to "/api/levels" with that building's ID and single level:
      | name     |
      | Basement |
    Then the response status code should be 201
    And the first item in "created" should have "floor_number" with value 0

  Scenario: Attempt to import level without name
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block D | 1      |
    When I send a POST request to "/api/levels" with that building's ID and invalid level:
      | floor_number |
      | 1            |
    Then the response status code should be 201
    And the "created" list should be empty
    And the "errors" list should have 1 item

  Scenario: Attempt to import level with invalid building_id
    When I send a POST request to "/api/levels" with:
      | field       | value                     |
      | name        | Test Floor                |
      | building_id | non-existent-building-123 |
    Then the response status code should be 201
    And the "created" list should be empty
    And the "errors" list should have 1 item

  Scenario: Mixed import - some valid some invalid
    Given a site exists with:
      | name      | description |
      | Test Site | Test        |
    And that site has a building:
      | name    | floors |
      | Block E | 4      |
    When I send a POST request to "/api/levels" with that building's ID and mixed levels:
      | name         | floor_number | status  |
      | Ground Floor | 0            | valid   |
      |              | 1            | invalid |
      | Second Floor | 2            | valid   |
    Then the response status code should be 201
    And the "created" list should have 2 items
    And the "errors" list should have 1 item
