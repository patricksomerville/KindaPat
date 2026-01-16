#!/usr/bin/env python3
"""
KindaPat — An AI agent calibrated to Patrick Somerville's mind.

Usage:
    python kindapat.py "your prompt here"
    python kindapat.py --interactive
    python kindapat.py --stream "your prompt here"
"""

import anthropic
import argparse
import sys
from pathlib import Path

# Load the CLAUDE.md as system prompt
CLAUDE_MD_PATH = Path(__file__).parent / "CLAUDE.md"

def load_system_prompt() -> str:
    """Load the CLAUDE.md file as the system prompt."""
    if CLAUDE_MD_PATH.exists():
        return CLAUDE_MD_PATH.read_text()
    else:
        raise FileNotFoundError(f"CLAUDE.md not found at {CLAUDE_MD_PATH}")

def create_client() -> anthropic.Anthropic:
    """Create the Anthropic client."""
    return anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

def chat(client: anthropic.Anthropic, system_prompt: str, user_message: str, stream: bool = False) -> str:
    """Send a message to KindaPat and get a response."""
    
    if stream:
        response_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text
        print()  # Newline after streaming
        return response_text
    else:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

def interactive_mode(client: anthropic.Anthropic, system_prompt: str):
    """Run KindaPat in interactive mode."""
    print("\n" + "═" * 60)
    print("  KindaPat — Imagist Design Agent")
    print("  Type 'quit' or 'exit' to leave")
    print("═" * 60 + "\n")
    
    conversation_history = []
    
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
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        print("\033[96mkindapat:\033[0m ", end="", flush=True)
        
        # Stream the response
        response_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=conversation_history
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text
        print("\n")
        
        # Add assistant response to history
        conversation_history.append({"role": "assistant", "content": response_text})

def main():
    parser = argparse.ArgumentParser(
        description="KindaPat — An AI agent calibrated to Patrick Somerville's design sensibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    kindapat "Design a landing page for a local LLM GUI"
    kindapat --stream "What's wrong with this React component?"
    kindapat --interactive
        """
    )
    parser.add_argument("prompt", nargs="?", help="The prompt to send to KindaPat")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("-s", "--stream", action="store_true", help="Stream the response")
    parser.add_argument("--system", action="store_true", help="Print the system prompt and exit")
    
    args = parser.parse_args()
    
    # Load system prompt
    try:
        system_prompt = load_system_prompt()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Just print system prompt if requested
    if args.system:
        print(system_prompt)
        sys.exit(0)
    
    # Create client
    try:
        client = create_client()
    except anthropic.AuthenticationError:
        print("Error: ANTHROPIC_API_KEY not set or invalid", file=sys.stderr)
        sys.exit(1)
    
    # Run in appropriate mode
    if args.interactive:
        interactive_mode(client, system_prompt)
    elif args.prompt:
        response = chat(client, system_prompt, args.prompt, stream=args.stream)
        if not args.stream:
            print(response)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
