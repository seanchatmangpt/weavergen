#!/usr/bin/env python3
"""
Weaver Wrapper - Direct interface to Weaver CLI commands
Let's understand how Weaver Forge works by calling it directly
"""

import subprocess
import sys
from pathlib import Path
import json

class WeaverWrapper:
    """Simple wrapper around Weaver CLI commands"""
    
    def __init__(self):
        self.check_weaver_installed()
    
    def check_weaver_installed(self):
        """Check if weaver is available"""
        try:
            result = self.run_command(["weaver", "--version"])
            print(f"✓ Weaver installed: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Weaver not found. Please install it first.")
            sys.exit(1)
    
    def run_command(self, cmd: list, capture=True) -> subprocess.CompletedProcess:
        """Run a command and return result"""
        print(f"\n🔧 Running: {' '.join(cmd)}")
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                print(f"📤 Output:\n{result.stdout}")
            if result.stderr:
                print(f"⚠️  Error:\n{result.stderr}")
            return result
        else:
            # Run interactively
            return subprocess.run(cmd)
    
    def registry_check(self, registry_path: str):
        """Check a semantic convention registry"""
        print(f"\n📋 Checking registry: {registry_path}")
        return self.run_command(["weaver", "registry", "check", "-r", registry_path])
    
    def registry_resolve(self, registry_path: str, output: str = None):
        """Resolve a semantic convention registry"""
        print(f"\n🔄 Resolving registry: {registry_path}")
        cmd = ["weaver", "registry", "resolve", "-r", registry_path]
        if output:
            cmd.extend(["-o", output])
        return self.run_command(cmd)
    
    def registry_generate(self, registry_path: str, templates: str, target: str, output: str = None, params: dict = None):
        """Generate code/docs from registry using templates"""
        print(f"\n🏗️ Generating from registry: {registry_path}")
        print(f"   Templates: {templates}")
        print(f"   Target: {target}")
        
        # Correct syntax: weaver registry generate -r <registry> --templates <templates> <target> [output]
        cmd = ["weaver", "registry", "generate", "-r", registry_path, "--templates", templates, target]
        
        # Output is positional, not a flag
        if output:
            cmd.append(output)
        
        if params:
            for key, value in params.items():
                cmd.extend(["--param", f"{key}={value}"])
        
        return self.run_command(cmd)
    
    def registry_stats(self, registry_path: str):
        """Get statistics about a registry"""
        print(f"\n📊 Getting stats for: {registry_path}")
        return self.run_command(["weaver", "registry", "stats", "-r", registry_path])
    
    def help(self, command: str = None):
        """Get help for weaver commands"""
        if command:
            # Split command properly (e.g. "registry generate" -> ["registry", "generate"])
            parts = command.split()
            return self.run_command(["weaver"] + parts + ["--help"])
        else:
            return self.run_command(["weaver", "--help"])


def main():
    """Interactive exploration of Weaver commands"""
    weaver = WeaverWrapper()
    
    print("\n🎯 Weaver CLI Wrapper - Let's explore Weaver Forge")
    print("=" * 50)
    
    while True:
        print("\n📍 Available commands:")
        print("1. check <path>     - Check a registry")
        print("2. resolve <path>   - Resolve a registry") 
        print("3. generate         - Generate code from registry")
        print("4. stats <path>     - Get registry statistics")
        print("5. help [command]   - Get help")
        print("6. test             - Run test sequence")
        print("7. quit             - Exit")
        
        choice = input("\n> ").strip().lower()
        
        if choice.startswith("check "):
            path = choice[6:].strip()
            weaver.registry_check(path)
        
        elif choice.startswith("resolve "):
            path = choice[8:].strip()
            weaver.registry_resolve(path)
        
        elif choice == "generate":
            registry = input("Registry path: ").strip()
            templates = input("Templates path: ").strip()
            target = input("Target (e.g., python): ").strip()
            output = input("Output dir (optional): ").strip()
            
            params = {}
            while True:
                param = input("Add param (key=value) or press Enter to skip: ").strip()
                if not param:
                    break
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
            
            weaver.registry_generate(
                registry_path=registry,
                templates=templates,
                target=target,
                output=output if output else None,
                params=params if params else None
            )
        
        elif choice.startswith("stats "):
            path = choice[6:].strip()
            weaver.registry_stats(path)
        
        elif choice.startswith("help"):
            parts = choice.split()
            if len(parts) > 1:
                weaver.help(" ".join(parts[1:]))
            else:
                weaver.help()
        
        elif choice == "test":
            print("\n🧪 Running test sequence...")
            
            # Test 1: Check weaver-forge.yaml with proper registry structure
            print("\n--- Test 1: Check test_registry ---")
            weaver.registry_check("test_registry")
            
            # Test 2: Resolve it
            print("\n--- Test 2: Resolve test_registry ---")
            weaver.registry_resolve("test_registry")
            
            # Test 3: Try to generate
            print("\n--- Test 3: Generate from test_registry ---")
            weaver.registry_generate(
                registry_path="test_registry",
                templates="templates",
                target="python"
            )
        
        elif choice in ["quit", "exit", "q"]:
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❓ Unknown command. Try 'help'")


if __name__ == "__main__":
    main()