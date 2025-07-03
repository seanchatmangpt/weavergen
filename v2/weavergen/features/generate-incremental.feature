Feature: Incremental Code Generation
  Scenario: Regenerate only changed artifacts
    Given a project has been initialized
    When a template file is modified
    And the user runs "weavergen generate python --incremental"
    Then only the artifacts related to the modified template should be regenerated
