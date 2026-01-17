#!/usr/bin/env python3
"""
KindaPat Agent — Agentic version with tool use capabilities.

This version can:
- Execute bash commands
- Read and write files
- Create artifacts
- Think through problems step by step

Usage:
    python kindapat_agent.py "Build me a landing page for local.buddy"
    python kindapat_agent.py --interactive
"""

import anthropic
import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import Any

_CLAUDE_MD_PATH = Path(__file__).parent / "CLAUDE.md"

# Tool definitions
_TOOLS = [
    {
        "name": "bash",
        "description": "Execute a bash command. Use this to run commands, install packages, or interact with the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file if it doesn't exist.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List contents of a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list"
                }
            },
            "required": ["path"]
        }
    }
]

def _execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool and return the result."""
    
    if name == "bash":
        try:
            result = subprocess.run(
                input_data["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n(exit code: {result.returncode})"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 60 seconds"
        except Exception as e:
            return f"Error: {str(e)}"
    
    elif name == "read_file":
        try:
            path = Path(input_data["path"]).expanduser()
            return path.read_text()
        except FileNotFoundError:
            return f"Error: File not found: {input_data['path']}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    elif name == "write_file":
        try:
            path = Path(input_data["path"]).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(input_data["content"])
            return f"Successfully wrote {len(input_data['content'])} bytes to {path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    elif name == "list_directory":
        try:
            path = Path(input_data["path"]).expanduser()
            items = list(path.iterdir())
            result = []
            for item in sorted(items):
                prefix = "📁 " if item.is_dir() else "📄 "
                result.append(f"{prefix}{item.name}")
            return "\n".join(result) if result else "(empty directory)"
        except FileNotFoundError:
            return f"Error: Directory not found: {input_data['path']}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return f"Error: Unknown tool: {name}"

def _load_system_prompt() -> str:
    """Load the CLAUDE.md file as the system prompt."""
    if _CLAUDE_MD_PATH.exists():
        base_prompt = _CLAUDE_MD_PATH.read_text()
        # Add agentic instructions
        agentic_addition = """

---

## Agentic Mode

You are running as an agent with tool access. You can:
- Execute bash commands to interact with the system
- Read and write files
- List directories
- Build and create things

When given a task:
1. Think through what needs to be done
2. Use tools to accomplish it
3. Verify your work
4. Report back concisely

Don't ask for permission—act. State your assumption and execute.
"""
        return base_prompt + agentic_addition
    else:
        raise FileNotFoundError(f"CLAUDE.md not found at {_CLAUDE_MD_PATH}")

def _run_agent(client: anthropic.Anthropic, system_prompt: str, user_message: str):
    """Run the agent loop until task completion."""
    
    messages = [{"role": "user", "content": user_message}]
    
    print("\033[90m─── KindaPat Agent ───\033[0m\n")
    
    while True:
        # Get response from Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            tools=_TOOLS,
            messages=messages
        )
        
        # Process response content
        assistant_content = []
        has_tool_use = False
        
        for block in response.content:
            if block.type == "text":
                print(f"\033[96m{block.text}\033[0m")
                assistant_content.append({"type": "text", "text": block.text})
            
            elif block.type == "tool_use":
                has_tool_use = True
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id
                
                print(f"\n\033[93m⚡ {tool_name}:\033[0m {json.dumps(tool_input, indent=2)[:200]}...")
                
                # Execute the tool
                result = _execute_tool(tool_name, tool_input)
                
                # Show truncated result
                display_result = result[:500] + "..." if len(result) > 500 else result
                print(f"\033[90m{display_result}\033[0m\n")
                
                assistant_content.append({
                    "type": "tool_use",
                    "id": tool_use_id,
                    "name": tool_name,
                    "input": tool_input
                })
                
                # Add tool result to messages
                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    }]
                })
                assistant_content = []
        
        # If no tool use, we're done
        if not has_tool_use:
            if assistant_content:
                messages.append({"role": "assistant", "content": assistant_content})
            break
        
        # Check for end turn
        if response.stop_reason == "end_turn":
            break
    
    print("\n\033[90m─── Done ───\033[0m")

def _interactive_agent(client: anthropic.Anthropic, system_prompt: str):
    """Run the agent in interactive mode."""
    print("\n" + "═" * 60)
    print("  KindaPat Agent — Agentic Mode")
    print("  Type 'quit' to exit")
    print("═" * 60 + "\n")
    
    while True:
        try:
            user_input = input("\033[93myou:\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', 'q'):
            break
        
        _run_agent(client, system_prompt, user_input)
        print()

def main():
    parser = argparse.ArgumentParser(
        description="KindaPat Agent — Agentic AI with tool use",
    )
    parser.add_argument("prompt", nargs="?", help="Task to accomplish")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    try:
        system_prompt = _load_system_prompt()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        client = anthropic.Anthropic()
    except anthropic.AuthenticationError:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    if args.interactive:
        _interactive_agent(client, system_prompt)
    elif args.prompt:
        _run_agent(client, system_prompt, args.prompt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
