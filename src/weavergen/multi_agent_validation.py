"""
Multi-Agent Validation System - Parallel code review using agent patterns

This module implements multi-specialist validation inspired by the
agent-guides multi-mind pattern.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import ast
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re


@dataclass
class ValidationFeedback:
    """Feedback from a validation specialist."""
    specialist: str
    severity: str  # error, warning, suggestion
    category: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        location = f" (line {self.line_number})" if self.line_number else ""
        return f"[{self.severity.upper()}] {self.specialist}: {self.message}{location}"


class ValidationSpecialist:
    """Base class for validation specialists."""
    
    def __init__(self, name: str, focus_areas: List[str]):
        self.name = name
        self.focus_areas = focus_areas
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        """Validate code and return feedback."""
        raise NotImplementedError
    
    def _parse_code(self, code: str) -> Optional[ast.AST]:
        """Safely parse Python code."""
        try:
            return ast.parse(code)
        except SyntaxError:
            return None


class OTELComplianceSpecialist(ValidationSpecialist):
    """Validates OpenTelemetry compliance."""
    
    def __init__(self):
        super().__init__(
            "OTEL Compliance Checker",
            ["naming conventions", "attribute types", "semantic compliance"]
        )
        self.otel_patterns = {
            'attribute_naming': re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$'),
            'metric_naming': re.compile(r'^[a-z][a-z0-9]*(\.[a-z0-9]+)*$'),
            'span_naming': re.compile(r'^[A-Z][a-zA-Z0-9]*$')
        }
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        feedback = []
        tree = self._parse_code(code)
        
        if not tree:
            return [ValidationFeedback(
                self.name, "error", "syntax", 
                "Failed to parse code - syntax errors present"
            )]
        
        # Check class names for conventions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if 'Convention' not in node.name and 'Span' in code:
                    feedback.append(ValidationFeedback(
                        self.name, "warning", "naming",
                        f"Class '{node.name}' should follow Convention naming pattern",
                        node.lineno,
                        f"Consider renaming to '{node.name}Convention'"
                    ))
                
                # Check for required OTEL attributes
                self._check_otel_attributes(node, feedback)
        
        # Check for proper attribute definitions
        attribute_pattern = re.compile(r'(\w+):\s*(?:Optional\[)?(\w+)')
        for match in attribute_pattern.finditer(code):
            attr_name = match.group(1)
            if not self.otel_patterns['attribute_naming'].match(attr_name):
                feedback.append(ValidationFeedback(
                    self.name, "warning", "naming",
                    f"Attribute '{attr_name}' doesn't follow OTEL naming convention",
                    suggestion=f"Use snake_case: '{self._to_snake_case(attr_name)}'"
                ))
        
        return feedback
    
    def _check_otel_attributes(self, node: ast.ClassDef, feedback: List[ValidationFeedback]):
        """Check for required OTEL attributes in a class."""
        has_attributes = False
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                has_attributes = True
                break
        
        if not has_attributes and 'Convention' in node.name:
            feedback.append(ValidationFeedback(
                self.name, "error", "structure",
                f"Convention class '{node.name}' has no attributes defined",
                node.lineno
            ))
    
    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class PerformanceOptimizer(ValidationSpecialist):
    """Analyzes code for performance issues."""
    
    def __init__(self):
        super().__init__(
            "Performance Optimizer",
            ["efficiency", "caching", "memory usage", "algorithmic complexity"]
        )
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        feedback = []
        tree = self._parse_code(code)
        
        if not tree:
            return feedback
        
        for node in ast.walk(tree):
            # Check for inefficient patterns
            if isinstance(node, ast.For):
                self._check_loop_efficiency(node, code, feedback)
            
            # Check for repeated computations
            if isinstance(node, ast.FunctionDef):
                self._check_function_efficiency(node, feedback)
            
            # Check for large default mutable arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        feedback.append(ValidationFeedback(
                            self.name, "warning", "performance",
                            f"Mutable default argument in function '{node.name}'",
                            node.lineno,
                            "Use None as default and create inside function"
                        ))
        
        return feedback
    
    def _check_loop_efficiency(self, node: ast.For, code: str, feedback: List[ValidationFeedback]):
        """Check for common loop inefficiencies."""
        # Check for repeated len() calls
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                if node.iter.args and isinstance(node.iter.args[0], ast.Call):
                    if getattr(node.iter.args[0].func, 'id', None) == 'len':
                        feedback.append(ValidationFeedback(
                            self.name, "suggestion", "performance",
                            "Consider caching len() result before loop",
                            node.lineno
                        ))
    
    def _check_function_efficiency(self, node: ast.FunctionDef, feedback: List[ValidationFeedback]):
        """Check function for efficiency issues."""
        # Check for missing @lru_cache on pure functions
        if not node.decorator_list and self._is_pure_function(node):
            feedback.append(ValidationFeedback(
                self.name, "suggestion", "performance",
                f"Function '{node.name}' appears pure - consider @lru_cache",
                node.lineno
            ))
    
    def _is_pure_function(self, node: ast.FunctionDef) -> bool:
        """Heuristic to check if function might be pure."""
        # Simple heuristic - no assignments to non-local variables
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Global) or isinstance(subnode, ast.Nonlocal):
                return False
        return True


class APIDesignValidator(ValidationSpecialist):
    """Validates API design and usability."""
    
    def __init__(self):
        super().__init__(
            "API Design Validator",
            ["usability", "consistency", "documentation", "error handling"]
        )
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        feedback = []
        tree = self._parse_code(code)
        
        if not tree:
            return feedback
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for docstrings
                if not ast.get_docstring(node):
                    feedback.append(ValidationFeedback(
                        self.name, "warning", "documentation",
                        f"Function '{node.name}' lacks docstring",
                        node.lineno
                    ))
                
                # Check for type hints
                if not node.returns and node.name != '__init__':
                    feedback.append(ValidationFeedback(
                        self.name, "warning", "typing",
                        f"Function '{node.name}' lacks return type annotation",
                        node.lineno
                    ))
                
                # Check parameter naming
                for arg in node.args.args:
                    if len(arg.arg) < 3 and arg.arg != 'self':
                        feedback.append(ValidationFeedback(
                            self.name, "suggestion", "naming",
                            f"Parameter '{arg.arg}' in '{node.name}' is too short",
                            node.lineno,
                            "Use descriptive parameter names"
                        ))
            
            if isinstance(node, ast.ClassDef):
                # Check for class docstring
                if not ast.get_docstring(node):
                    feedback.append(ValidationFeedback(
                        self.name, "warning", "documentation",
                        f"Class '{node.name}' lacks docstring",
                        node.lineno
                    ))
        
        return feedback


class SecurityAuditor(ValidationSpecialist):
    """Checks for security best practices."""
    
    def __init__(self):
        super().__init__(
            "Security Auditor",
            ["input validation", "injection prevention", "secure defaults"]
        )
        self.dangerous_patterns = [
            (re.compile(r'eval\s*\('), "Use of eval() is dangerous"),
            (re.compile(r'exec\s*\('), "Use of exec() is dangerous"),
            (re.compile(r'__import__\s*\('), "Dynamic imports can be risky"),
            (re.compile(r'pickle\.loads'), "Pickle deserialization is unsafe"),
        ]
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        feedback = []
        
        # Check for dangerous patterns
        for pattern, message in self.dangerous_patterns:
            for match in pattern.finditer(code):
                line_num = code[:match.start()].count('\n') + 1
                feedback.append(ValidationFeedback(
                    self.name, "error", "security",
                    message,
                    line_num
                ))
        
        # Check for input validation
        tree = self._parse_code(code)
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if 'from_' in node.name or 'parse_' in node.name:
                        # Check if function validates input
                        has_validation = self._has_validation(node)
                        if not has_validation:
                            feedback.append(ValidationFeedback(
                                self.name, "warning", "security",
                                f"Function '{node.name}' should validate input",
                                node.lineno
                            ))
        
        return feedback
    
    def _has_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function has input validation."""
        for subnode in ast.walk(node):
            # Look for try/except, isinstance, or validation calls
            if isinstance(subnode, ast.Try):
                return True
            if isinstance(subnode, ast.Call):
                if isinstance(subnode.func, ast.Name):
                    if subnode.func.id in ['isinstance', 'validate', 'check']:
                        return True
        return False


class DocumentationReviewer(ValidationSpecialist):
    """Reviews documentation completeness and quality."""
    
    def __init__(self):
        super().__init__(
            "Documentation Reviewer",
            ["docstrings", "comments", "examples", "type annotations"]
        )
    
    async def validate(self, code: str, file_path: Path) -> List[ValidationFeedback]:
        feedback = []
        tree = self._parse_code(code)
        
        if not tree:
            return feedback
        
        # Check module-level docstring
        module_docstring = ast.get_docstring(tree)
        if not module_docstring:
            feedback.append(ValidationFeedback(
                self.name, "warning", "documentation",
                "Module lacks docstring",
                1
            ))
        
        # Check all classes and functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Check docstring quality
                    issues = self._check_docstring_quality(docstring, node)
                    feedback.extend(issues)
        
        # Check for TODO/FIXME comments
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK):\s*(.+)', re.IGNORECASE)
        for match in todo_pattern.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            feedback.append(ValidationFeedback(
                self.name, "suggestion", "maintenance",
                f"{match.group(1)}: {match.group(2)}",
                line_num,
                "Address or create issue for tracking"
            ))
        
        return feedback
    
    def _check_docstring_quality(self, docstring: str, node: ast.AST) -> List[ValidationFeedback]:
        """Check docstring quality and completeness."""
        issues = []
        
        if len(docstring) < 10:
            issues.append(ValidationFeedback(
                self.name, "warning", "documentation",
                f"Docstring for '{node.name}' is too brief",
                node.lineno,
                "Add more detail about purpose and usage"
            ))
        
        # Check for parameter documentation in functions
        if isinstance(node, ast.FunctionDef) and node.args.args:
            if 'Args:' not in docstring and 'Parameters:' not in docstring:
                if len(node.args.args) > 1 or (node.args.args and node.args.args[0].arg != 'self'):
                    issues.append(ValidationFeedback(
                        self.name, "suggestion", "documentation",
                        f"Function '{node.name}' parameters not documented",
                        node.lineno
                    ))
        
        return issues


class MultiAgentValidator:
    """Orchestrates multiple validation specialists in parallel."""
    
    def __init__(self, max_workers: int = 5):
        self.specialists = [
            OTELComplianceSpecialist(),
            PerformanceOptimizer(),
            APIDesignValidator(),
            SecurityAuditor(),
            DocumentationReviewer()
        ]
        self.max_workers = max_workers
    
    async def validate_code(self, 
                           code: str, 
                           file_path: Path,
                           specialists: Optional[List[str]] = None) -> Dict[str, List[ValidationFeedback]]:
        """
        Run validation with multiple specialists in parallel.
        
        Args:
            code: Code to validate
            file_path: Path to the file
            specialists: Optional list of specialist names to use
        
        Returns:
            Dictionary mapping specialist names to their feedback
        """
        # Filter specialists if requested
        active_specialists = self.specialists
        if specialists:
            active_specialists = [s for s in self.specialists if s.name in specialists]
        
        # Run validations in parallel
        tasks = []
        for specialist in active_specialists:
            task = specialist.validate(code, file_path)
            tasks.append((specialist.name, task))
        
        results = {}
        for name, task in tasks:
            try:
                feedback = await task
                results[name] = feedback
            except Exception as e:
                results[name] = [ValidationFeedback(
                    name, "error", "internal",
                    f"Specialist failed: {str(e)}"
                )]
        
        return results
    
    def get_summary(self, results: Dict[str, List[ValidationFeedback]]) -> Dict[str, Any]:
        """Generate summary statistics from validation results."""
        total_issues = sum(len(feedback) for feedback in results.values())
        
        by_severity = {
            'error': 0,
            'warning': 0,
            'suggestion': 0
        }
        
        by_category = {}
        
        for feedback_list in results.values():
            for feedback in feedback_list:
                by_severity[feedback.severity] += 1
                by_category[feedback.category] = by_category.get(feedback.category, 0) + 1
        
        return {
            'total_issues': total_issues,
            'by_severity': by_severity,
            'by_category': by_category,
            'specialists_run': len(results)
        }
    
    def format_report(self, results: Dict[str, List[ValidationFeedback]]) -> str:
        """Format validation results as a readable report."""
        lines = [
            "# Multi-Agent Validation Report",
            "",
            "## Summary",
            ""
        ]
        
        summary = self.get_summary(results)
        lines.append(f"Total Issues: {summary['total_issues']}")
        lines.append(f"Specialists Run: {summary['specialists_run']}")
        lines.append("")
        lines.append("### By Severity")
        for severity, count in summary['by_severity'].items():
            if count > 0:
                lines.append(f"- {severity.capitalize()}: {count}")
        
        lines.append("")
        lines.append("### By Category")
        for category, count in sorted(summary['by_category'].items()):
            lines.append(f"- {category}: {count}")
        
        lines.append("")
        lines.append("## Detailed Feedback")
        lines.append("")
        
        # Group feedback by severity
        all_feedback = []
        for specialist, feedback_list in results.items():
            for feedback in feedback_list:
                all_feedback.append(feedback)
        
        # Sort by severity (errors first) and line number
        severity_order = {'error': 0, 'warning': 1, 'suggestion': 2}
        all_feedback.sort(key=lambda f: (
            severity_order.get(f.severity, 3),
            f.line_number or 0
        ))
        
        current_severity = None
        for feedback in all_feedback:
            if feedback.severity != current_severity:
                current_severity = feedback.severity
                lines.append(f"### {current_severity.upper()}S")
                lines.append("")
            
            lines.append(f"- **{feedback.specialist}** ({feedback.category}): {feedback.message}")
            if feedback.line_number:
                lines.append(f"  - Line: {feedback.line_number}")
            if feedback.suggestion:
                lines.append(f"  - Suggestion: {feedback.suggestion}")
            lines.append("")
        
        return '\n'.join(lines)


# Integration with CLI
async def validate_with_agents(file_path: Path) -> None:
    """Run multi-agent validation on a file."""
    validator = MultiAgentValidator()
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    print(f"🔍 Running multi-agent validation on {file_path.name}")
    print(f"👥 Specialists: {len(validator.specialists)}")
    print()
    
    results = await validator.validate_code(code, file_path)
    report = validator.format_report(results)
    
    print(report)
    
    # Save report
    report_path = file_path.with_suffix('.validation.md')
    report_path.write_text(report)
    print(f"\n📄 Full report saved to: {report_path}")


if __name__ == "__main__":
    # Test the validator
    import asyncio
    
    test_file = Path("src/weavergen/semantic_parser.py")
    if test_file.exists():
        asyncio.run(validate_with_agents(test_file))