#!/usr/bin/env python3
"""
CCCS Session Management for WeaverGen Code Generation
Handles session continuity, context recovery, and generation state management
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import hashlib
import os


@dataclass
class GenerationSession:
    """Represents an active code generation session"""
    session_id: str
    project_path: str
    active_registry: Optional[str] = None
    target_languages: Set[str] = field(default_factory=set)
    output_directories: Dict[str, str] = field(default_factory=dict)
    generation_state: str = "idle"  # idle, generating, validating, complete, error
    last_command: Optional[str] = None
    context_anchors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['target_languages'] = list(self.target_languages)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationSession':
        """Create from dictionary"""
        if 'target_languages' in data:
            data['target_languages'] = set(data['target_languages'])
        return cls(**data)


class CCCSSessionManager:
    """Manages CCCS sessions for code generation workflows"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.cccs_dir = self.project_root / "claude-code-context"
        self.sessions_dir = self.cccs_dir / "sessions"
        self.current_link = self.cccs_dir / "current.link"
        self.recovery_spr = self.cccs_dir / "session_recovery.spr"
        
        # Ensure directories exist
        self.cccs_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
        
        self.current_session: Optional[GenerationSession] = None
    
    def generate_session_id(self) -> str:
        """Generate unique session ID based on timestamp and project"""
        timestamp = str(int(time.time()))
        project_hash = hashlib.md5(str(self.project_root).encode()).hexdigest()[:8]
        return f"cccs_{timestamp}_{project_hash}"
    
    def create_session(self, registry_url: Optional[str] = None, 
                      target_languages: Optional[Set[str]] = None) -> GenerationSession:
        """Create new generation session"""
        session_id = self.generate_session_id()
        
        session = GenerationSession(
            session_id=session_id,
            project_path=str(self.project_root),
            active_registry=registry_url,
            target_languages=target_languages or set(),
            generation_state="idle"
        )
        
        self.current_session = session
        self.save_session(session)
        self.update_current_link(session_id)
        self.update_recovery_spr(session)
        
        return session
    
    def save_session(self, session: GenerationSession) -> None:
        """Save session to disk"""
        session.updated_at = time.time()
        session_file = self.sessions_dir / f"{session.session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load_session(self, session_id: str) -> Optional[GenerationSession]:
        """Load session from disk"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file) as f:
                data = json.load(f)
            return GenerationSession.from_dict(data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def update_current_link(self, session_id: str) -> None:
        """Update current session link"""
        with open(self.current_link, 'w') as f:
            f.write(session_id)
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID from link"""
        if not self.current_link.exists():
            return None
        
        try:
            with open(self.current_link) as f:
                return f.read().strip()
        except Exception:
            return None
    
    def load_current_session(self) -> Optional[GenerationSession]:
        """Load current active session"""
        session_id = self.get_current_session_id()
        if not session_id:
            return None
        
        session = self.load_session(session_id)
        if session:
            self.current_session = session
        
        return session
    
    def update_recovery_spr(self, session: GenerationSession) -> None:
        """Update SPR recovery file with session context"""
        spr_content = f"""# CCCS Generation Session Recovery SPR

## Session: {session.session_id}
**State**: {session.generation_state}
**Registry**: {session.active_registry or 'None'}
**Languages**: {', '.join(session.target_languages) if session.target_languages else 'None'}
**Last Command**: {session.last_command or 'None'}

## Context Anchors:
{chr(10).join(f"- {anchor}" for anchor in session.context_anchors)}

## Performance Metrics:
{json.dumps(session.performance_metrics, indent=2)}

## Auto-Generated: {datetime.fromtimestamp(session.updated_at).isoformat()}
"""
        
        with open(self.recovery_spr, 'w') as f:
            f.write(spr_content)
    
    def add_context_anchor(self, anchor: str) -> None:
        """Add context anchor to current session"""
        if self.current_session:
            self.current_session.context_anchors.append(f"{datetime.now().isoformat()}: {anchor}")
            if len(self.current_session.context_anchors) > 10:
                # Keep only last 10 anchors
                self.current_session.context_anchors = self.current_session.context_anchors[-10:]
            
            self.save_session(self.current_session)
            self.update_recovery_spr(self.current_session)
    
    def update_generation_state(self, state: str, command: Optional[str] = None) -> None:
        """Update generation state and optional last command"""
        if self.current_session:
            self.current_session.generation_state = state
            if command:
                self.current_session.last_command = command
            
            self.save_session(self.current_session)
            self.update_recovery_spr(self.current_session)
    
    def add_target_language(self, language: str, output_dir: Optional[str] = None) -> None:
        """Add target language to current session"""
        if self.current_session:
            self.current_session.target_languages.add(language)
            if output_dir:
                self.current_session.output_directories[language] = output_dir
            
            self.save_session(self.current_session)
            self.update_recovery_spr(self.current_session)
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update performance metrics for current session"""
        if self.current_session:
            self.current_session.performance_metrics.update(metrics)
            self.save_session(self.current_session)
            self.update_recovery_spr(self.current_session)
    
    def validate_session_integrity(self) -> Dict[str, Any]:
        """Validate session integrity and detect corruption"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'auto_repair_attempted': False
        }
        
        # Check if current.link exists
        if not self.current_link.exists():
            validation_result['errors'].append("Missing current.link file")
            validation_result['valid'] = False
        
        # Check if current session exists
        session_id = self.get_current_session_id()
        if session_id:
            session = self.load_session(session_id)
            if not session:
                validation_result['errors'].append(f"Current session {session_id} not found")
                validation_result['valid'] = False
            else:
                # Validate session data
                if not session.project_path or not Path(session.project_path).exists():
                    validation_result['warnings'].append("Session project path invalid")
                
                # Check if output directories exist
                for lang, output_dir in session.output_directories.items():
                    if not Path(output_dir).exists():
                        validation_result['warnings'].append(f"Output directory for {lang} not found: {output_dir}")
        
        # Check if recovery SPR exists and is recent
        if not self.recovery_spr.exists():
            validation_result['warnings'].append("Missing session recovery SPR")
        elif time.time() - self.recovery_spr.stat().st_mtime > 3600:  # 1 hour
            validation_result['warnings'].append("Session recovery SPR is stale")
        
        return validation_result
    
    def auto_repair_session(self) -> bool:
        """Attempt to auto-repair corrupted session state"""
        try:
            # If no current session, try to find the most recent one
            if not self.get_current_session_id() or not self.load_current_session():
                recent_sessions = []
                for session_file in self.sessions_dir.glob("cccs_*.json"):
                    session = self.load_session(session_file.stem)
                    if session:
                        recent_sessions.append(session)
                
                if recent_sessions:
                    # Use the most recently updated session
                    latest_session = max(recent_sessions, key=lambda s: s.updated_at)
                    self.current_session = latest_session
                    self.update_current_link(latest_session.session_id)
                    self.update_recovery_spr(latest_session)
                    return True
            
            return False
        except Exception as e:
            print(f"Auto-repair failed: {e}")
            return False
    
    def discover_project_context(self) -> Dict[str, Any]:
        """Discover project context from filesystem"""
        context = {
            'registries': [],
            'generated_files': [],
            'target_languages': set(),
            'recent_activity': []
        }
        
        # Look for semantic convention files
        for pattern in ["*.yaml", "*.yml", "*.json"]:
            for file in self.project_root.rglob(pattern):
                if any(keyword in file.name.lower() for keyword in ['convention', 'semconv', 'otel', 'telemetry']):
                    context['registries'].append(str(file))
        
        # Look for generated output directories
        common_output_dirs = ['generated', 'output', 'dist', 'build']
        for dir_name in common_output_dirs:
            output_dir = self.project_root / dir_name
            if output_dir.exists() and output_dir.is_dir():
                # Check for language-specific subdirectories
                for lang_dir in output_dir.iterdir():
                    if lang_dir.is_dir() and lang_dir.name in ['python', 'rust', 'go', 'java', 'typescript']:
                        context['target_languages'].add(lang_dir.name)
                        # Count generated files
                        files = list(lang_dir.rglob("*"))
                        context['generated_files'].extend(str(f) for f in files if f.is_file())
        
        # Convert set to list for JSON serialization
        context['target_languages'] = list(context['target_languages'])
        
        # Check git history for recent activity
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=1 week ago', '--', '.'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                context['recent_activity'] = result.stdout.strip().split('\n')[:5]
        except Exception:
            pass
        
        return context
    
    def get_session_summary(self) -> str:
        """Get human-readable session summary"""
        if not self.current_session:
            return "No active session"
        
        s = self.current_session
        summary = f"""
🔧 CCCS Generation Session: {s.session_id}

**Status**: {s.generation_state.upper()}
**Registry**: {s.active_registry or 'None configured'}
**Target Languages**: {', '.join(s.target_languages) if s.target_languages else 'None'}
**Last Command**: {s.last_command or 'None'}

**Output Directories**:
{chr(10).join(f"  - {lang}: {path}" for lang, path in s.output_directories.items()) if s.output_directories else "  None configured"}

**Recent Context**:
{chr(10).join(f"  - {anchor.split(': ', 1)[-1]}" for anchor in s.context_anchors[-3:]) if s.context_anchors else "  No recent activity"}

**Performance**: {len(s.performance_metrics)} metrics tracked
**Session Age**: {(time.time() - s.created_at) / 3600:.1f} hours
"""
        return summary.strip()


# CLI integration functions
def cccs_continue() -> str:
    """Handle /continue command with CCCS session recovery"""
    project_root = Path.cwd()
    manager = CCCSSessionManager(project_root)
    
    # Step 1: Context validation
    validation = manager.validate_session_integrity()
    
    if not validation['valid']:
        # Attempt auto-repair
        if manager.auto_repair_session():
            print("🔧 Auto-repaired session state")
        else:
            # Discover context from filesystem
            context = manager.discover_project_context()
            if context['registries'] or context['generated_files']:
                return f"""
❌ **CONTEXT VALIDATION FAILED**

Session state corrupted but project context discovered:
- Registries found: {len(context['registries'])}
- Generated files: {len(context['generated_files'])}
- Target languages: {', '.join(context['target_languages']) if context['target_languages'] else 'None'}

**Recovery Options**:
1. `/bootstrap-otel` - Create new session from discovered context
2. Specify what you were working on manually

**Context mismatch detected. What were you generating?**
"""
    
    # Step 2: Load current session
    session = manager.load_current_session()
    if not session:
        return "❌ No active session found. Use `/bootstrap-otel` to start new generation session."
    
    # Step 3: Present context confirmation
    return f"""
✅ **RESUMING GENERATION SESSION**

{manager.get_session_summary()}

**Ready to continue? Next actions**:
- Continue generation: `/generate`
- Validate output: `/validate`
- Switch language: `/switch-lang [language]`
- Add context: `/trace [description]`

**Continue with generation?**
"""


if __name__ == "__main__":
    # Demo/test functionality
    manager = CCCSSessionManager(Path.cwd())
    print(cccs_continue())
