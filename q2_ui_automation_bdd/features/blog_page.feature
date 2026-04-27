Feature: Pointr Blog Analysis
  As a QA engineer
  I want to validate the Pointr blog page and analyze the latest articles
  So that I can verify the page works and extract insights from its content

  Background:
    Given I open the Pointr blog page

  Scenario: Blog page loads successfully
    Then the page title should contain "Blog"
    And the URL should contain "pointr.tech/blog"
    And the page should be fully loaded

  Scenario: All articles are visible on the blog page
    Then the page should display at least 9 articles
    And each article should have a title
    And each article should have a "Read more" link

  Scenario: Extract the latest 3 articles from the Latest section
    When I extract the latest 3 article URLs
    Then I should have exactly 3 article URLs
    And each URL should contain "pointr.tech/blog"

  Scenario: Analyze word frequency for latest 3 articles
    When I extract the latest 3 article URLs
    And I visit each article and extract its text
    Then each article should have its top 5 words identified
    And the results should be saved to "word_frequency_report.txt"
    And the output file should exist

  Scenario: Complete end-to-end blog analysis workflow
    Then the page should display at least 9 articles
    When I extract the latest 3 article URLs
    And I visit each article and extract its text
    Then each article should have its top 5 words identified
    And the results should be saved to "full_report.txt"
    And the output file should contain data for all 3 articles
