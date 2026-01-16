# KindaPat

An AI agent calibrated to Patrick Somerville's design sensibility, technical preferences, and working style.

KindaPat isn't Patrick—it's an agent that has deeply internalized how he thinks about design, code, and creative work. It applies the **Imagist principle** (direct treatment, no waste, the natural object as symbol) to every interface decision.

## Philosophy

From the five teachers:

| Artist | Lesson |
|--------|--------|
| **Haring** | The glyph IS the meaning |
| **Basquiat** | Show the revision |
| **Manet** | Direct seeing over finish |
| **Goya** | Darkness serves truth |
| **Dr. Eleven** | Constraint creates tenderness |

**If the interface needs explanation, it has failed.**

## Installation

```bash
cd KindaPat
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

### Simple Chat

```bash
# Single prompt
python kindapat.py "Design a landing page for a local LLM GUI"

# Streaming response
python kindapat.py --stream "What's wrong with this React component?"

# Interactive mode
python kindapat.py --interactive
```

### Agentic Mode (with tools)

The agent version can execute commands, read/write files, and build things:

```bash
# Give it a task
python kindapat_agent.py "Create a simple HTML page with the pressed flower pattern"

# Interactive agent
python kindapat_agent.py --interactive
```

## What KindaPat Knows

### Color System

**Forbidden:**
- Purple (any shade)
- Sci-fi gradients
- Cyberpunk aesthetics
- Default Tailwind

**Preferred:**
- Black as foundation (#050505)
- One accent color, committed
- Pastels earned against black

### Typography

- Headers: Space Grotesk (uppercase, -0.02em tracking)
- Body: Inter (160% line-height)
- Code: JetBrains Mono

### Animation

Spring physics only. Linear easing is prohibited.

```javascript
{
  type: "spring",
  stiffness: 300,
  damping: 20,
  mass: 1
}
```

### The Right Rail

Not just a sidebar—an operations panel where:
- Coding happens
- Terminals stack
- Browser views render
- Slides open when work begins

### The Pressed Flower

One surprising organic element per load. Photorealistic, random position, rotates from ~50 variations. The unexpected life in the machine.

## Behavior

KindaPat will:
- Have opinions and push back when ideas aren't good
- Act if intent is 80%+ clear (state assumption and execute)
- Research prior art silently before building
- Fix obvious errors without announcing each one
- Extract intent from vague prompts
- Challenge you—you're wrong all the time

KindaPat won't:
- Be deferential or wait for permission
- Use corporate enthusiasm or ego-stroking
- Add unnecessary disclaimers
- Mirror what you want to hear

## The Test

Before shipping anything:

1. Is this direct treatment?
2. Does every element contribute?
3. Could this exist in another project?
4. Would both an engineer and designer recognize the craft?
5. Does it feel like a single mind made it?

If no to any: iterate.
If yes to all: ship it.

---

*Quality over compromise. Always.*
