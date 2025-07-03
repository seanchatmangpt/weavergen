Feature: Watch Mode and Hot-Reload
  Scenario: Automatically regenerate on file changes
    Given a project has been initialized
    When the user runs "weavergen generate python --watch --hot-reload"
    And a spec file is modified
    Then the corresponding code should be regenerated automatically
    And the running development server should be notified of the changes
