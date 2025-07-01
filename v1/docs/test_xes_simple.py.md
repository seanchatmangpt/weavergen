This Python file, `test_xes_simple.py`, is a simple test script for the XES conversion functionality within WeaverGen.
It demonstrates the use of the `XESConverter` from `src.weavergen.xes_converter`.
The script loads OpenTelemetry spans from a JSON file (`final_8020_output/execution_spans.json`).
It then uses the `spans_to_xes` method of the `XESConverter` to convert these loaded spans into an XES (eXtensible Event Stream) format file, saving it as `simple_test.xes`.
This file serves as a basic verification that the span-to-XES conversion process is working correctly, facilitating integration with process mining tools.