
from pathlib import Path
from weavergen.forge_complete import CompleteForgeGenerator

# Define paths
semantic_file = Path("test_semantic.yaml")
output_dir = Path("generated_code")

# Create a dummy semantic file for testing
if not semantic_file.exists():
    semantic_file.write_text("""
groups:
  - id: http
    type: span
    brief: "HTTP client and server spans"
    attributes:
      - id: http.method
        type: string
        brief: "HTTP request method"
      - id: http.status_code
        type: int
        brief: "HTTP response status code"
""")

# Initialize the generator
generator = CompleteForgeGenerator(semantic_file, output_dir)

# Generate the 4-layer architecture
result = generator.generate_4_layer_architecture()

if result.success:
    print("✅ Code generation successful!")
    for f in result.files:
        print(f"  - {f}")
else:
    print(f"❌ Code generation failed: {result.error}")
