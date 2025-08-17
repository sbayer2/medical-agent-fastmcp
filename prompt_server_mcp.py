#!/usr/bin/env python3
"""
MCP Prompt Server for Medical Agent
Provides dynamic prompts that guide tool usage
"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

class PromptServer:
    def __init__(self, prompts_dir: str = "/app/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, str]:
        """Load all prompt files from the prompts directory"""
        prompts = {}
        if self.prompts_dir.exists():
            for prompt_file in self.prompts_dir.glob("*.prompt"):
                key = prompt_file.stem
                prompts[key] = prompt_file.read_text()
        return prompts
    
    def get_prompt(self, name: str, context: Dict[str, Any] = None) -> str:
        """Get a specific prompt with optional context substitution"""
        if name not in self.prompts:
            return f"No prompt found for: {name}"
        
        prompt = self.prompts[name]
        
        # Substitute context variables if provided
        if context:
            for key, value in context.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        return prompt
    
    def list_prompts(self) -> List[str]:
        """List all available prompts"""
        return list(self.prompts.keys())
    
    def get_tool_guidance(self, task: str) -> Dict[str, Any]:
        """Provide guidance on which tools to use for specific tasks"""
        tool_guidance = {
            "analyze_file": {
                "required_tools": ["filesystem"],
                "steps": [
                    "First, use filesystem tool to read the medical document",
                    "Then analyze the content using medical_processor prompt",
                    "Do NOT attempt to analyze without reading the file first"
                ],
                "prompt": "medical_processor"
            },
            "patient_summary": {
                "required_tools": ["filesystem"],
                "steps": [
                    "Use filesystem to access patient records",
                    "Apply patient_summary prompt for formatting",
                    "Ensure HIPAA compliance in output"
                ],
                "prompt": "patient_summary"
            },
            "billing": {
                "required_tools": ["stripe", "filesystem"],
                "steps": [
                    "First verify the analysis was completed",
                    "Use stripe tool to create billing record",
                    "Do NOT skip billing verification"
                ],
                "prompt": None
            },
            "fetch_guidelines": {
                "required_tools": ["fetch"],
                "steps": [
                    "Use fetch tool to retrieve medical guidelines",
                    "Do NOT make up medical information",
                    "Always cite sources"
                ],
                "prompt": None
            }
        }
        
        return tool_guidance.get(task, {
            "required_tools": [],
            "steps": ["No specific guidance available for this task"],
            "prompt": None
        })

def handle_mcp_request(request: Dict[str, Any], server: PromptServer) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    method = request.get("method", "")
    params = request.get("params", {})
    
    if method == "prompts/list":
        return {
            "prompts": [
                {
                    "name": name,
                    "description": f"Prompt for {name.replace('_', ' ')}"
                }
                for name in server.list_prompts()
            ]
        }
    
    elif method == "prompts/get":
        prompt_name = params.get("name", "")
        context = params.get("context", {})
        return {
            "prompt": server.get_prompt(prompt_name, context)
        }
    
    elif method == "tools/guidance":
        task = params.get("task", "")
        return {
            "guidance": server.get_tool_guidance(task)
        }
    
    elif method == "tools/list":
        # Inform about available tools and their purposes
        return {
            "tools": [
                {
                    "name": "filesystem",
                    "purpose": "Read medical documents and files",
                    "required_for": ["file analysis", "document reading"]
                },
                {
                    "name": "fetch",
                    "purpose": "Retrieve external medical resources",
                    "required_for": ["guidelines", "research papers"]
                },
                {
                    "name": "stripe",
                    "purpose": "Handle billing and payment processing",
                    "required_for": ["billing", "payment tracking"]
                }
            ]
        }
    
    else:
        return {
            "error": f"Unknown method: {method}"
        }

def main():
    """Main MCP server loop"""
    server = PromptServer()
    
    # MCP uses JSON-RPC over stdio
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            response = handle_mcp_request(request, server)
            
            # Add JSON-RPC fields
            response["jsonrpc"] = "2.0"
            response["id"] = request.get("id", 1)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1) if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
