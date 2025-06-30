#!/usr/bin/env python3
"""
CCCS Integration Script for WeaverGen
Main entry point for Claude Code Context System integration
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Import CCCS modules
from session_manager import CCCSSessionManager, cccs_continue
from automation_loops import CCCSAutomationEngine


class CCCSInterface:
    """Main interface for CCCS commands and integration"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.session_manager = CCCSSessionManager(self.project_root)
        self.automation_engine = CCCSAutomationEngine(self.project_root)
    
    def continue_session(self) -> str:
        """Handle /continue command"""
        return cccs_continue()
    
    def bootstrap_session(self, registry_url: Optional[str] = None, 
                         languages: Optional[str] = None,
                         output_dir: Optional[str] = None,
                         auto_configure: bool = False) -> str:
        """Handle /bootstrap-otel command"""
        
        # Parse languages if provided
        target_languages = set()
        if languages:
            target_languages = set(lang.strip() for lang in languages.split(','))
        elif auto_configure:
            # Auto-detect from project structure
            context = self.session_manager.discover_project_context()
            target_languages = context.get('target_languages', {'python'})
        
        # Create new session
        session = self.session_manager.create_session(
            registry_url=registry_url,
            target_languages=target_languages
        )
        
        # Setup output directories
        if output_dir:
            base_output = Path(output_dir)
        else:
            base_output = self.project_root / "generated"
        
        for lang in target_languages:
            lang_output = base_output / lang
            session.output_directories[lang] = str(lang_output)
        
        self.session_manager.save_session(session)
        self.session_manager.add_context_anchor(f"Bootstrapped session with languages: {', '.join(target_languages)}")
        
        return f"""
✅ **NEW OTEL SESSION BOOTSTRAPPED**

**Session ID**: {session.session_id}
**Registry**: {registry_url or 'None specified'}
**Target Languages**: {', '.join(target_languages) if target_languages else 'None'}
**Output Directory**: {base_output}

**Auto-Discovery Results**:
{json.dumps(self.session_manager.discover_project_context(), indent=2)}

**Next Steps**:
1. Configure registry: `/weavergen:multi-generate [registry_url] [languages]`
2. Validate setup: `/weavergen:validate all`
3. Start generation: `/generate`

**Session ready for OTel code generation!**
"""
    
    def heal_session(self) -> str:
        """Handle /heal-code command"""
        validation = self.session_manager.validate_session_integrity()
        
        if validation['valid']:
            return "✅ **SESSION HEALTHY** - No repairs needed"
        
        # Attempt auto-repair
        repair_successful = self.session_manager.auto_repair_session()
        
        if repair_successful:
            return f"""
🔧 **SESSION AUTO-REPAIRED**

**Issues Found**:
{chr(10).join(f"- {error}" for error in validation['errors'])}

**Warnings**:
{chr(10).join(f"- {warning}" for warning in validation['warnings'])}

**Repair Status**: ✅ Successful
**Current Session**: {self.session_manager.get_session_summary()}

**Session continuity restored!**
"""
        else:
            return f"""
❌ **SESSION REPAIR FAILED**

**Issues Found**:
{chr(10).join(f"- {error}" for error in validation['errors'])}

**Auto-repair unsuccessful. Manual intervention required.**

**Recovery Options**:
1. `/bootstrap-otel --auto-configure` - Create new session from project context
2. Manually specify what you were working on
3. Check project structure and try again

**What were you working on before the session corruption?**
"""
    
    def validate_cccs(self) -> str:
        """Handle /validate-cccs command"""
        validation = self.session_manager.validate_session_integrity()
        automation_status = self.automation_engine.get_status()
        
        health_status = "🟢 HEALTHY" if validation['valid'] else "🟡 DEGRADED"
        if validation['errors']:
            health_status = "🔴 CRITICAL"
        
        return f"""
📊 **CCCS SYSTEM HEALTH REPORT**

**Overall Status**: {health_status}

**Session Integrity**:
- Valid: {'✅' if validation['valid'] else '❌'}
- Errors: {len(validation['errors'])}
- Warnings: {len(validation['warnings'])}

**Automation Engine**:
- Running: {'✅' if automation_status['running'] else '❌'}
- Active Loops: {len([l for l in automation_status['loops'].values() if l['enabled']])}
- Total Runs: {sum(l['run_count'] for l in automation_status['loops'].values())}

**Loop Status**:
{chr(10).join(f"- {loop_data['name']}: {'🟢' if loop_data['enabled'] else '🔴'} ({loop_data['run_count']} runs, {loop_data['success_rate']:.1%} success)" for loop_data in automation_status['loops'].values())}

**Session Summary**:
{self.session_manager.get_session_summary()}

**Recommendations**:
{chr(10).join(f"- {error}" for error in validation['errors'])}
{chr(10).join(f"- {warning}" for warning in validation['warnings'])}
"""
    
    def switch_language(self, language: str) -> str:
        """Handle /switch-lang command"""
        if not self.session_manager.current_session:
            return "❌ No active session. Use `/bootstrap-otel` to create one."
        
        # Add language to current session
        self.session_manager.add_target_language(language)
        self.session_manager.add_context_anchor(f"Switched focus to {language} generation")
        
        return f"""
🔄 **LANGUAGE CONTEXT SWITCHED**

**Active Language**: {language}
**All Target Languages**: {', '.join(self.session_manager.current_session.target_languages)}
**Session**: {self.session_manager.current_session.session_id}

**Output Directory**: {self.session_manager.current_session.output_directories.get(language, 'Not configured')}

**Ready for {language} code generation!**

**Next Steps**:
- Generate code: `/weavergen:multi-generate [registry] {language}`
- Validate: `/weavergen:validate generated --languages {language}`
- Optimize: `/weavergen:optimize all --languages {language}`
"""
    
    def discover_registries(self) -> str:
        """Handle /discover-registry command"""
        context = self.session_manager.discover_project_context()
        
        return f"""
🔍 **REGISTRY DISCOVERY RESULTS**

**Semantic Convention Files Found**:
{chr(10).join(f"- {registry}" for registry in context['registries']) if context['registries'] else "None found"}

**Generated Files**:
- Count: {len(context['generated_files'])}
- Languages: {', '.join(context['target_languages']) if context['target_languages'] else 'None detected'}

**Recent Activity**:
{chr(10).join(f"- {activity}" for activity in context['recent_activity'][:3]) if context['recent_activity'] else "No recent git activity"}

**Auto-Configuration Suggestions**:
{chr(10).join(f"- Add registry: {registry}" for registry in context['registries'][:3])}
{chr(10).join(f"- Target language: {lang}" for lang in context['target_languages'])}

**Project Context**: {len(context['registries'])} registries, {len(context['generated_files'])} generated files
"""
    
    async def start_automation(self) -> str:
        """Start automation loops"""
        try:
            # Start automation engine in background
            asyncio.create_task(self.automation_engine.start_automation())
            
            return """
🤖 **AUTOMATION LOOPS STARTED**

**Active Loops**:
- Registry Monitoring (1 hour intervals)
- Generation Quality (30 min intervals)
- Performance Optimization (2 hour intervals)
- Session Health (5 min intervals)
- Cache Optimization (30 min intervals)
- Evolution Tracking (24 hour intervals)

**Features**:
- ✅ Self-healing enabled
- ✅ Evolution tracking active
- ✅ Performance optimization running
- ✅ Quality monitoring continuous

**Automation engine running in background...**
"""
        except Exception as e:
            return f"❌ Failed to start automation: {e}"
    
    def stop_automation(self) -> str:
        """Stop automation loops"""
        self.automation_engine.stop_automation()
        return "🛑 **AUTOMATION LOOPS STOPPED**"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="CCCS Interface for WeaverGen")
    parser.add_argument('command', choices=[
        'continue', 'bootstrap', 'heal', 'validate', 'switch-lang', 
        'discover', 'start-automation', 'stop-automation'
    ])
    parser.add_argument('--registry', help="Registry URL for bootstrap")
    parser.add_argument('--languages', help="Comma-separated languages")
    parser.add_argument('--output-dir', help="Output directory")
    parser.add_argument('--auto-configure', action='store_true', help="Auto-configure from project")
    parser.add_argument('--language', help="Target language for switch-lang")
    
    args = parser.parse_args()
    
    cccs = CCCSInterface()
    
    if args.command == 'continue':
        print(cccs.continue_session())
    elif args.command == 'bootstrap':
        print(cccs.bootstrap_session(
            registry_url=args.registry,
            languages=args.languages,
            output_dir=args.output_dir,
            auto_configure=args.auto_configure
        ))
    elif args.command == 'heal':
        print(cccs.heal_session())
    elif args.command == 'validate':
        print(cccs.validate_cccs())
    elif args.command == 'switch-lang':
        if not args.language:
            print("❌ --language required for switch-lang command")
            sys.exit(1)
        print(cccs.switch_language(args.language))
    elif args.command == 'discover':
        print(cccs.discover_registries())
    elif args.command == 'start-automation':
        result = asyncio.run(cccs.start_automation())
        print(result)
    elif args.command == 'stop-automation':
        print(cccs.stop_automation())


if __name__ == "__main__":
    main()
