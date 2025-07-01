"""
Template Learning System - Extract patterns from generated code

This module learns code generation patterns from existing examples
in the test_generated directory, creating a self-bootstrapping
template system.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import textwrap


@dataclass
class CodePattern:
    """Represents a discovered code pattern."""
    pattern_type: str  # class, function, import, etc.
    template: str
    variables: Set[str]
    context: Dict[str, any]
    frequency: int = 1
    
    def apply(self, substitutions: Dict[str, str]) -> str:
        """Apply substitutions to generate code from pattern."""
        result = self.template
        for var, value in substitutions.items():
            result = result.replace(f"{{{var}}}", value)
        return result


class TemplateExtractor:
    """Extracts reusable patterns from generated code."""
    
    def __init__(self, generated_dir: Path = Path("test_generated")):
        self.generated_dir = generated_dir
        self.patterns: Dict[str, List[CodePattern]] = defaultdict(list)
        self.import_patterns: Set[str] = set()
        self.class_structures: List[Dict] = []
        self.function_signatures: List[Dict] = []
    
    def analyze_directory(self) -> Dict[str, List[CodePattern]]:
        """Analyze all Python files in the generated directory."""
        py_files = list(self.generated_dir.glob("**/*.py"))
        
        for py_file in py_files:
            if py_file.name != "__init__.py":
                self.analyze_file(py_file)
        
        # Extract common patterns
        self._extract_class_patterns()
        self._extract_function_patterns()
        self._extract_import_patterns()
        
        return self.patterns
    
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for patterns."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            self._extract_from_ast(tree, file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
    
    def _extract_from_ast(self, tree: ast.AST, file_path: Path) -> None:
        """Extract patterns from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self._analyze_import(node)
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Analyze class definition for patterns."""
        class_info = {
            'name': node.name,
            'bases': [self._get_name(base) for base in node.bases],
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'methods': [],
            'attributes': [],
            'file': str(file_path)
        }
        
        # Extract methods and attributes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args],
                    'decorators': [self._get_name(dec) for dec in item.decorator_list],
                    'is_async': isinstance(item, ast.AsyncFunctionDef)
                }
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_info['attributes'].append({
                    'name': item.target.id,
                    'type': self._get_annotation(item.annotation)
                })
        
        self.class_structures.append(class_info)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """Analyze function definition for patterns."""
        func_info = {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'returns': self._get_annotation(node.returns) if node.returns else None,
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'file': str(file_path)
        }
        self.function_signatures.append(func_info)
    
    def _analyze_import(self, node: ast.AST) -> None:
        """Analyze import statements."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.import_patterns.add(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                self.import_patterns.add(f"from {module} import {alias.name}")
    
    def _extract_class_patterns(self) -> None:
        """Extract common class patterns."""
        # Group classes by structure similarity
        base_patterns = defaultdict(list)
        
        for class_info in self.class_structures:
            # Create pattern key based on structure
            key = (
                tuple(class_info['bases']),
                len(class_info['methods']),
                len(class_info['attributes'])
            )
            base_patterns[key].append(class_info)
        
        # Create templates for common patterns
        for pattern_key, classes in base_patterns.items():
            if len(classes) >= 2:  # Pattern appears at least twice
                template = self._create_class_template(classes)
                self.patterns['class'].append(template)
    
    def _extract_function_patterns(self) -> None:
        """Extract common function patterns."""
        # Group functions by signature pattern
        sig_patterns = defaultdict(list)
        
        for func_info in self.function_signatures:
            key = (
                len(func_info['args']),
                bool(func_info['returns']),
                func_info['is_async']
            )
            sig_patterns[key].append(func_info)
        
        # Create templates for common patterns
        for pattern_key, functions in sig_patterns.items():
            if len(functions) >= 2:
                template = self._create_function_template(functions)
                self.patterns['function'].append(template)
    
    def _extract_import_patterns(self) -> None:
        """Extract common import patterns."""
        # Group imports by module
        import_groups = defaultdict(list)
        
        for imp in self.import_patterns:
            if 'from' in imp:
                module = imp.split(' import ')[0].replace('from ', '')
                import_groups[module].append(imp)
            else:
                import_groups['direct'].append(imp)
        
        # Create import template
        if self.import_patterns:
            template = CodePattern(
                pattern_type='imports',
                template='\n'.join(sorted(self.import_patterns)),
                variables=set(),
                context={'all_imports': list(self.import_patterns)},
                frequency=len(self.import_patterns)
            )
            self.patterns['imports'].append(template)
    
    def _create_class_template(self, classes: List[Dict]) -> CodePattern:
        """Create a class template from similar classes."""
        # Extract common structure
        bases = classes[0]['bases']
        typical_methods = self._find_common_methods(classes)
        
        template_parts = [
            "class {class_name}({bases}):",
            '    """{docstring}"""',
            ''
        ]
        
        # Add common methods
        for method in typical_methods:
            template_parts.append(f"    def {method}(self{{{method}_args}}):")
            template_parts.append(f"        {{{method}_body}}")
            template_parts.append('')
        
        template = '\n'.join(template_parts)
        
        return CodePattern(
            pattern_type='class',
            template=template,
            variables={'class_name', 'bases', 'docstring'} | 
                     {f"{m}_args" for m in typical_methods} |
                     {f"{m}_body" for m in typical_methods},
            context={
                'base_classes': bases,
                'methods': typical_methods
            },
            frequency=len(classes)
        )
    
    def _create_function_template(self, functions: List[Dict]) -> CodePattern:
        """Create a function template from similar functions."""
        # Determine common structure
        avg_args = sum(len(f['args']) for f in functions) // len(functions)
        has_return = any(f['returns'] for f in functions)
        is_async = any(f['is_async'] for f in functions)
        
        template_parts = []
        if is_async:
            template_parts.append("async def {func_name}({args}):")
        else:
            template_parts.append("def {func_name}({args}):")
        
        template_parts.append('    """{docstring}"""')
        template_parts.append('    {body}')
        
        if has_return:
            template_parts.append('    return {return_value}')
        
        template = '\n'.join(template_parts)
        
        return CodePattern(
            pattern_type='function',
            template=template,
            variables={'func_name', 'args', 'docstring', 'body', 'return_value'},
            context={
                'avg_args': avg_args,
                'has_return': has_return,
                'is_async': is_async
            },
            frequency=len(functions)
        )
    
    def _find_common_methods(self, classes: List[Dict]) -> List[str]:
        """Find methods that appear in most classes."""
        method_counts = defaultdict(int)
        
        for class_info in classes:
            for method in class_info['methods']:
                method_counts[method['name']] += 1
        
        # Return methods that appear in at least 75% of classes
        threshold = len(classes) * 0.75
        return [m for m, count in method_counts.items() if count >= threshold]
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _get_annotation(self, node: ast.AST) -> Optional[str]:
        """Get type annotation as string."""
        if node is None:
            return None
        return ast.unparse(node)
    
    def generate_template_library(self) -> str:
        """Generate a template library module from discovered patterns."""
        code_lines = [
            '"""Auto-generated template library from code patterns."""',
            '',
            'from typing import Dict, List',
            '',
            '# Discovered patterns from test_generated analysis',
            '',
            'TEMPLATES = {',
        ]
        
        for pattern_type, patterns in self.patterns.items():
            code_lines.append(f'    "{pattern_type}": [')
            for pattern in patterns:
                code_lines.append(f'        # Frequency: {pattern.frequency}')
                code_lines.append(f'        {{')
                code_lines.append(f'            "template": """{pattern.template}""",')
                code_lines.append(f'            "variables": {list(pattern.variables)},')
                code_lines.append(f'            "context": {pattern.context}')
                code_lines.append(f'        }},')
            code_lines.append('    ],')
        
        code_lines.append('}')
        
        return '\n'.join(code_lines)


# Example usage
if __name__ == "__main__":
    extractor = TemplateExtractor()
    patterns = extractor.analyze_directory()
    
    print(f"Discovered {sum(len(p) for p in patterns.values())} patterns")
    print(f"Pattern types: {list(patterns.keys())}")
    
    # Generate template library
    library_code = extractor.generate_template_library()
    print("\nTemplate Library Preview:")
    print(library_code[:500] + "...")