This Python file defines Pydantic models for the Design for Lean Six Sigma (DMEDI) methodology.
It structures data for all five DMEDI phases: Define, Measure, Explore, Develop, and Implement.
Enums like `ProjectStatus`, `RiskLevel`, and `PhaseStatus` provide controlled vocabularies.
Define phase models include `ProjectCharter`, `MGPPAssessment`, `RiskManagementPlan`, and `CommunicationPlan`.
Measure phase models encompass `VOCAnalysis`, `QFDMatrix`, `TargetCost`, `BalancedScorecard`, `StatisticalTest`, and `ProcessCapabilityStudy`.
Explore phase models cover `ConceptGenerationSession`, `TRIZAnalysis`, `PughMatrix`, and `DOEDesign`.
Develop phase models define `DetailedDesignSpecification` and `RobustDesignAnalysis`.
Implement phase models include `PrototypeSpecification`, `PilotStudy`, `ControlPlan`, and `ImplementationPlan`.
The `DMEDICapstoneProject` model aggregates all phase-specific models into a comprehensive project structure.
Models utilize `uuid` for unique identifiers and `datetime` for date fields.
Pydantic `Field` and `validator` are used for data validation and metadata.
This module serves as the foundational data schema for DMEDI training and project management within the WeaverGen system.