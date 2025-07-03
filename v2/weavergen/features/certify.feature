Feature: Zero-Drift Certification
  Scenario: Run governance checks
    Given a project has been initialized
    When the user runs "weavergen certify"
    Then the governance checks defined in 'governance.yaml' should be executed
    And a summary of the results should be printed to the console
