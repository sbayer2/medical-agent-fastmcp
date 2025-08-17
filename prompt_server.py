#!/usr/bin/env python3
"""
Simple MCP prompt server that provides medical prompts
"""
import json
import sys

# Mock MCP protocol response
def handle_request():
    # For now, just provide a simple response to test MCP connection
    response = {
        "prompts": {
            "medical_processor": "Analyze medical information and extract vital signs, medications, diagnoses",
            "patient_summary": "Create HIPAA-compliant patient summary"
        }
    }
    print(json.dumps(response))

if __name__ == "__main__":
    # Simple mock - in reality this would implement full MCP protocol
    handle_request()
