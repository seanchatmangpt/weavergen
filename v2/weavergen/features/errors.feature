Feature: Rich Error Surfacing
  Scenario: Detect missing configuration
    Given a project has been initialized
    And the 'weaver-forge.yaml' is missing a required parameter
    When the user runs "weavergen generate python"
    Then a user-friendly error message should be displayed with the file and line number of the missing parameter
