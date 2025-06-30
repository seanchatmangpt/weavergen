#!/usr/bin/env python3
"""
Scrum of Scrums Meeting Simulation using Roberts Rules
Combines Scrum at Scale practices with formal parliamentary procedure
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Since we're simulating, we'll create minimal implementations
# In a real system, these would come from the Roberts Rules runtime

# Scrum-specific enums
class TeamStatus(Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"

class ImpedimentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SprintProgress:
    """Sprint progress metrics"""
    team_name: str
    sprint_number: int
    stories_completed: int
    stories_total: int
    story_points_completed: int
    story_points_total: int
    velocity: float
    status: TeamStatus
    
    @property
    def completion_percentage(self) -> float:
        if self.story_points_total == 0:
            return 0.0
        return (self.story_points_completed / self.story_points_total) * 100

@dataclass
class Impediment:
    """Cross-team impediment or blocker"""
    id: str
    description: str
    severity: ImpedimentSeverity
    affecting_teams: List[str]
    owner_team: str
    raised_date: datetime
    resolution_needed_by: datetime

@dataclass
class Dependency:
    """Cross-team dependency"""
    id: str
    from_team: str
    to_team: str
    description: str
    needed_by: datetime
    status: str = "pending"

class ScrumMasterAgent:
    """Agent representing a Scrum Master from a specific team"""
    
    def __init__(self, name: str, team_name: str):
        self.name = name
        self.team_name = team_name
        self.sprint_progress = self._generate_sprint_progress()
        self.impediments = self._generate_impediments()
        self.dependencies = self._generate_dependencies()
        
    def _generate_sprint_progress(self) -> SprintProgress:
        """Generate realistic sprint progress"""
        total_points = random.randint(40, 80)
        completed_points = random.randint(20, total_points)
        total_stories = random.randint(8, 15)
        completed_stories = int(total_stories * (completed_points / total_points))
        
        # Determine status based on progress
        completion = (completed_points / total_points) * 100
        if completion >= 70:
            status = TeamStatus.ON_TRACK
        elif completion >= 50:
            status = TeamStatus.AT_RISK
        else:
            status = TeamStatus.BLOCKED
            
        return SprintProgress(
            team_name=self.team_name,
            sprint_number=42,  # Current sprint
            stories_completed=completed_stories,
            stories_total=total_stories,
            story_points_completed=completed_points,
            story_points_total=total_points,
            velocity=random.uniform(35, 65),
            status=status
        )
    
    def _generate_impediments(self) -> List[Impediment]:
        """Generate team impediments"""
        impediments = []
        
        # Common impediment scenarios
        scenarios = [
            ("API contract changes needed from Platform team", ImpedimentSeverity.HIGH),
            ("Database migration blocking deployment", ImpedimentSeverity.CRITICAL),
            ("Waiting on security review approval", ImpedimentSeverity.MEDIUM),
            ("Performance testing environment unavailable", ImpedimentSeverity.HIGH),
            ("Third-party service integration issues", ImpedimentSeverity.MEDIUM),
            ("Unclear requirements from Product team", ImpedimentSeverity.LOW),
        ]
        
        # Each team has 0-2 impediments
        num_impediments = random.randint(0, 2)
        for i in range(num_impediments):
            if scenarios:
                scenario = random.choice(scenarios)
                scenarios.remove(scenario)
                
                impediments.append(Impediment(
                    id=f"{self.team_name}-IMP-{i+1}",
                    description=scenario[0],
                    severity=scenario[1],
                    affecting_teams=[self.team_name] + random.sample(
                        ["Platform", "Mobile", "Web", "Backend", "Data"], 
                        k=random.randint(0, 2)
                    ),
                    owner_team=self.team_name,
                    raised_date=datetime.now() - timedelta(days=random.randint(1, 5)),
                    resolution_needed_by=datetime.now() + timedelta(days=random.randint(1, 7))
                ))
                
        return impediments
    
    def _generate_dependencies(self) -> List[Dependency]:
        """Generate cross-team dependencies"""
        dependencies = []
        
        # Common dependency scenarios
        scenarios = [
            ("Authentication service endpoints", "Platform"),
            ("Mobile API versioning", "Mobile"),
            ("Data pipeline output format", "Data"),
            ("Frontend component library update", "Web"),
            ("Microservice deployment coordination", "Backend"),
        ]
        
        # Each team has 0-3 dependencies
        num_deps = random.randint(0, 3)
        for i in range(num_deps):
            if scenarios:
                scenario = random.choice(scenarios)
                scenarios.remove(scenario)
                
                dependencies.append(Dependency(
                    id=f"{self.team_name}-DEP-{i+1}",
                    from_team=self.team_name,
                    to_team=scenario[1],
                    description=scenario[0],
                    needed_by=datetime.now() + timedelta(days=random.randint(3, 10))
                ))
                
        return dependencies
    
    def prepare_status_report(self) -> str:
        """Prepare formal status report for the meeting"""
        report = f"""Team {self.team_name} Status Report:

Sprint Progress:
- Sprint: #{self.sprint_progress.sprint_number}
- Stories: {self.sprint_progress.stories_completed}/{self.sprint_progress.stories_total} completed
- Story Points: {self.sprint_progress.story_points_completed}/{self.sprint_progress.story_points_total} ({self.sprint_progress.completion_percentage:.1f}%)
- Velocity: {self.sprint_progress.velocity:.1f} points/sprint
- Status: {self.sprint_progress.status.value.replace('_', ' ').upper()}

Key Accomplishments:
- Completed user authentication feature
- Fixed critical production bugs
- Improved API response time by 40%

Upcoming Work:
- Payment integration (20 points)
- Performance optimization (15 points)
- Security audit remediation (10 points)"""
        
        if self.impediments:
            report += "\n\nImpediments:"
            for imp in self.impediments:
                report += f"\n- [{imp.severity.value.upper()}] {imp.description}"
                if len(imp.affecting_teams) > 1:
                    report += f" (affects: {', '.join(imp.affecting_teams)})"
                    
        if self.dependencies:
            report += "\n\nDependencies:"
            for dep in self.dependencies:
                report += f"\n- Need from {dep.to_team}: {dep.description} by {dep.needed_by.strftime('%Y-%m-%d')}"
                
        return report

class ScrumOfScrumsSimulation:
    """Simulates a Scrum of Scrums meeting using Roberts Rules"""
    
    def __init__(self):
        # Create Scrum Master agents for different teams
        self.scrum_masters = [
            ScrumMasterAgent("Alice Chen", "Platform"),
            ScrumMasterAgent("Bob Kumar", "Mobile"),
            ScrumMasterAgent("Carol Smith", "Web"),
            ScrumMasterAgent("David Lee", "Backend"),
            ScrumMasterAgent("Emma Johnson", "Data"),
        ]
        
        # Chief Scrum Master facilitates
        self.chief_scrum_master = "Frank Wilson"
        
    async def run_meeting(self):
        """Run the Scrum of Scrums meeting"""
        print("```mermaid")
        print("sequenceDiagram")
        print("    participant CSM as Chief Scrum Master")
        for sm in self.scrum_masters:
            print(f"    participant {sm.team_name} as {sm.name}<br/>{sm.team_name} Team")
        print()
        
        # 1. Call to Order
        print("    CSM->>+All: Call to Order - Scrum of Scrums")
        print("    Note over All: Meeting begins at 9:00 AM")
        
        # 2. Verify Quorum
        print("    CSM->>All: Verify quorum for Scrum of Scrums")
        for sm in self.scrum_masters:
            print(f"    {sm.team_name}->>CSM: {sm.name} present for {sm.team_name} team")
        print("    CSM->>All: Quorum established - 5/5 teams represented")
        
        # 3. Approve Previous Meeting Minutes
        print("    CSM->>All: Motion to approve minutes from last week")
        print("    Platform->>CSM: So moved")
        print("    Mobile->>CSM: Second")
        print("    CSM->>All: All in favor? Motion carries")
        
        # 4. Team Status Reports (Round Robin)
        print("\n    rect rgb(200, 230, 255)")
        print("    Note over All: TEAM STATUS REPORTS")
        
        for sm in self.scrum_masters:
            print(f"\n    CSM->>{sm.team_name}: Please present {sm.team_name} team status")
            
            # Show sprint progress
            progress = sm.sprint_progress
            status_emoji = "🟢" if progress.status == TeamStatus.ON_TRACK else "🟡" if progress.status == TeamStatus.AT_RISK else "🔴"
            
            print(f"    {sm.team_name}->>All: Sprint #{progress.sprint_number} Progress:")
            print(f"    {sm.team_name}->>All: {status_emoji} {progress.completion_percentage:.0f}% complete ({progress.story_points_completed}/{progress.story_points_total} points)")
            
            # Report impediments if any
            if sm.impediments:
                for imp in sm.impediments:
                    severity_emoji = "🚨" if imp.severity == ImpedimentSeverity.CRITICAL else "⚠️"
                    print(f"    {sm.team_name}->>All: {severity_emoji} IMPEDIMENT: {imp.description}")
            
            # Acknowledge
            print(f"    CSM->>{sm.team_name}: Thank you, {sm.name}")
        
        print("    end")
        
        # 5. Address Critical Impediments
        print("\n    rect rgb(255, 200, 200)")
        print("    Note over All: IMPEDIMENT RESOLUTION")
        
        # Find critical impediments
        critical_impediments = []
        for sm in self.scrum_masters:
            critical_impediments.extend([
                (sm, imp) for imp in sm.impediments 
                if imp.severity in [ImpedimentSeverity.CRITICAL, ImpedimentSeverity.HIGH]
            ])
        
        if critical_impediments:
            # Address first critical impediment as a motion
            sm, imp = critical_impediments[0]
            print(f"\n    {sm.team_name}->>CSM: Motion to address critical impediment")
            print(f"    {sm.team_name}->>All: {imp.description}")
            
            # Find affected team to second
            affected_team = next((t for t in imp.affecting_teams if t != sm.team_name), "Web")
            print(f"    {affected_team}->>CSM: Second the motion")
            
            print("    CSM->>All: Discussion on impediment resolution")
            
            # Propose solution
            solution_team = "Platform" if "Platform" in imp.affecting_teams else "Backend"
            print(f"    {solution_team}->>All: We can provide temporary workaround by EOD")
            print(f"    {solution_team}->>All: Full resolution by {(datetime.now() + timedelta(days=2)).strftime('%A')}")
            
            print("    CSM->>All: All in favor of proposed solution?")
            print("    All->>CSM: Aye")
            print("    CSM->>All: Motion carries - impediment owner assigned")
        
        print("    end")
        
        # 6. Cross-team Dependencies
        print("\n    rect rgb(200, 255, 200)")
        print("    Note over All: DEPENDENCY COORDINATION")
        
        # Collect all dependencies
        all_deps = []
        for sm in self.scrum_masters:
            all_deps.extend([(sm, dep) for dep in sm.dependencies])
        
        if all_deps:
            # Address first few dependencies
            for sm, dep in all_deps[:3]:
                print(f"\n    {dep.from_team}->>{dep.to_team}: Dependency needed: {dep.description}")
                print(f"    {dep.to_team}->>{dep.from_team}: Can deliver by {dep.needed_by.strftime('%m/%d')}")
                print(f"    CSM->>Both: Dependency tracked in JIRA")
        
        print("    end")
        
        # 7. Action Items and Commitments
        print("\n    rect rgb(255, 255, 200)")
        print("    Note over All: ACTION ITEMS")
        
        print("    CSM->>All: Summary of action items:")
        print("    CSM->>Platform: Resolve authentication service blocker by EOD")
        print("    CSM->>Mobile: Coordinate with Web team on API versioning")
        print("    CSM->>Data: Provide pipeline documentation by Thursday")
        print("    CSM->>All: Next Scrum of Scrums: Same time next week")
        
        print("    end")
        
        # 8. Adjournment
        print("\n    CSM->>All: Motion to adjourn?")
        print("    Backend->>CSM: So moved")
        print("    Data->>CSM: Second")
        print("    CSM->>All: Meeting adjourned at 9:30 AM")
        print("    Note over All: Meeting Duration: 30 minutes")
        
        print("```")
        
        # Generate state diagram
        print("\n```mermaid")
        print("stateDiagram-v2")
        print("    [*] --> CallToOrder: Scrum of Scrums Begins")
        print("    CallToOrder --> QuorumCheck: Verify Attendance")
        print("    QuorumCheck --> MinutesApproval: 5/5 Teams Present")
        print("    MinutesApproval --> TeamReports: Previous Minutes Approved")
        print("    ")
        print("    TeamReports --> TeamReports: Each Team Reports Status")
        print("    note right of TeamReports")
        print("        Sprint Progress")
        print("        Impediments")
        print("        Dependencies")
        print("    end note")
        print("    ")
        print("    TeamReports --> ImpedimentResolution: All Teams Reported")
        print("    ImpedimentResolution --> DependencyCoordination: Critical Issues Addressed")
        print("    DependencyCoordination --> ActionItems: Dependencies Confirmed")
        print("    ActionItems --> Adjournment: Actions Assigned")
        print("    Adjournment --> [*]: Meeting Complete")
        print("```")
        
        # Generate team status overview
        print("\n```mermaid")
        print("graph TB")
        print("    subgraph Sprint 42 Status")
        for sm in self.scrum_masters:
            progress = sm.sprint_progress
            status_color = "green" if progress.status == TeamStatus.ON_TRACK else "yellow" if progress.status == TeamStatus.AT_RISK else "red"
            status_emoji = "✅" if progress.status == TeamStatus.ON_TRACK else "⚠️" if progress.status == TeamStatus.AT_RISK else "🚨"
            
            print(f"        {sm.team_name}[\"{sm.team_name} Team {status_emoji}<br/>{progress.completion_percentage:.0f}% Complete<br/>{progress.story_points_completed}/{progress.story_points_total} Points\"]")
            print(f"        style {sm.team_name} fill:#{status_color}f9,stroke:#333,stroke-width:2px")
        print("    end")
        
        # Show dependencies
        print("\n    subgraph Dependencies")
        for sm in self.scrum_masters:
            for dep in sm.dependencies[:1]:  # Show first dependency for each team
                print(f"        {dep.from_team} -.->|{dep.description}| {dep.to_team}")
        print("    end")
        print("```")
        
        # Generate impediment tracking
        print("\n```mermaid")
        print("gantt")
        print("    title Impediment Resolution Timeline")
        print("    dateFormat YYYY-MM-DD")
        print("    section Critical")
        
        # Show critical impediments on timeline
        for sm in self.scrum_masters:
            for imp in sm.impediments:
                if imp.severity in [ImpedimentSeverity.CRITICAL, ImpedimentSeverity.HIGH]:
                    days_to_resolve = (imp.resolution_needed_by - datetime.now()).days
                    print(f"    {imp.description[:30]}... :active, {datetime.now().strftime('%Y-%m-%d')}, {days_to_resolve}d")
        
        print("    section Dependencies")
        for sm in self.scrum_masters:
            for dep in sm.dependencies[:1]:
                days_needed = (dep.needed_by - datetime.now()).days
                print(f"    {dep.from_team} → {dep.to_team} :active, {datetime.now().strftime('%Y-%m-%d')}, {days_needed}d")
        print("```")
        
        # Generate meeting metrics
        print("\n```mermaid")
        print("pie title Team Status Distribution")
        on_track = sum(1 for sm in self.scrum_masters if sm.sprint_progress.status == TeamStatus.ON_TRACK)
        at_risk = sum(1 for sm in self.scrum_masters if sm.sprint_progress.status == TeamStatus.AT_RISK)
        blocked = sum(1 for sm in self.scrum_masters if sm.sprint_progress.status == TeamStatus.BLOCKED)
        
        print(f"    \"On Track\" : {on_track}")
        print(f"    \"At Risk\" : {at_risk}")
        print(f"    \"Blocked\" : {blocked}")
        print("```")
        
        # Roberts Rules compliance summary
        print("\n```mermaid")
        print("graph LR")
        print("    subgraph Roberts Rules Compliance")
        print("        A[Call to Order] --> B[Quorum Verified]")
        print("        B --> C[Minutes Approved]")
        print("        C --> D[Reports Presented]")
        print("        D --> E[Motions Processed]")
        print("        E --> F[Actions Recorded]")
        print("        F --> G[Proper Adjournment]")
        print("    end")
        print("    ")
        print("    style A fill:#90EE90")
        print("    style B fill:#90EE90")
        print("    style C fill:#90EE90")
        print("    style D fill:#90EE90")
        print("    style E fill:#90EE90")
        print("    style F fill:#90EE90")
        print("    style G fill:#90EE90")
        print("```")

async def main():
    """Run the Scrum of Scrums simulation"""
    # Run simulation
    simulation = ScrumOfScrumsSimulation()
    await simulation.run_meeting()

if __name__ == "__main__":
    asyncio.run(main())