Feature: Project Initialization
  Scenario: Scaffold a new project
    When the user runs "weavergen init"
    Then the following files should be created:
      | file                |
      | weaver-forge.yaml   |
      | cli_spec.yaml       |
      | governance.yaml     |
      | pyproject.toml      |
    And the following directories should be created:
      | directory |
      | processes |
      | templates |
