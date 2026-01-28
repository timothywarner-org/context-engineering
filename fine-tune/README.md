# WARNERCO Schematics Fine-Tuning Data

Training data for fine-tuning an OpenAI GPT model on WARNERCO Robotics schematic knowledge.

## Files

| File | Description |
|------|-------------|
| `schematics.json` | Original source data (25 robot schematics) copied from `src/warnerco/backend/data/schematics/` |
| `warnerco_schematics_finetune.jsonl` | Fine-tuning dataset in OpenAI chat completions format (15 examples) |

## JSONL Format

Each line is a standalone JSON object using the [OpenAI chat completions format](https://platform.openai.com/docs/guides/fine-tuning):

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Best Practices Applied

### 1. Consistent System Prompt
Every example uses the same system message defining the assistant's role, tone, and behavioral expectations. This teaches the model a stable persona.

### 2. Diverse Question Types
The 15 examples cover a range of query patterns a user might ask:

| Type | Example | Count |
|------|---------|-------|
| **Direct lookup** | "What is the force resolution of..." | 3 |
| **Enumeration** | "What components does the WC-100 have?" | 2 |
| **Comparison** | "Compare the sensor capabilities of..." | 1 |
| **Filtering** | "Which schematics are deprecated or draft?" | 2 |
| **Recommendation** | "I need a robot for delivery, what should I consider?" | 1 |
| **Troubleshooting** | "I'm getting inconsistent weld quality..." | 1 |
| **Aggregation** | "What categories exist and how many each?" | 2 |
| **Cross-referencing** | "What safety certifications are represented?" | 1 |
| **Temporal** | "Which schematics were most recently verified?" | 1 |
| **Capability survey** | "What communication capabilities exist?" | 1 |

### 3. Grounded Responses with Citations
Every assistant response cites specific schematic IDs (e.g., WRN-00001), version numbers, and exact specification values from the source data. This teaches the model to ground answers in data rather than hallucinate.

### 4. Structured Output Patterns
Responses use consistent formatting: bold labels, numbered lists, markdown tables, and clear section breaks. This teaches the model to produce scannable, professional output.

### 5. Appropriate Hedging
When information is absent or inferred, responses explicitly note gaps (e.g., "communication modules are not in the current schematic set") rather than fabricating data.

### 6. Multi-Hop Reasoning
Several examples require combining information across multiple schematics (e.g., the Hercules Lifter payload question pulls from hydraulic, load cell, and frame schematics).

## How to Fine-Tune

### Validate the file

```bash
# Install the OpenAI CLI
pip install openai

# Validate format (checks for errors before uploading)
openai tools fine_tunes.prepare_data -f warnerco_schematics_finetune.jsonl
```

### Upload and create fine-tuning job

```python
from openai import OpenAI
client = OpenAI()

# Upload training file
file = client.files.create(
    file=open("warnerco_schematics_finetune.jsonl", "rb"),
    purpose="fine-tune"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18"  # or gpt-3.5-turbo, gpt-4o
)

print(f"Job ID: {job.id}")
```

### Monitor progress

```python
# Check status
job = client.fine_tuning.jobs.retrieve(job.id)
print(job.status)

# List events
events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job.id, limit=10)
for event in events.data:
    print(event.message)
```

## Scaling This Dataset

15 examples is a starting point. OpenAI recommends **50-100 examples minimum** for noticeable improvement. To expand:

1. **More question types**: Add "what-if" scenarios, maintenance schedules, compatibility checks, part substitution queries.
2. **Multi-turn conversations**: Extend single-turn examples into multi-turn dialogues where the user asks follow-up questions.
3. **Negative examples**: Include cases where the model should say "that information is not in the schematic database" rather than guessing.
4. **Edge cases**: Questions about the deprecated (WRN-00021) and draft (WRN-00025) schematics, requests spanning models, ambiguous queries.

### Multi-turn example format

```json
{
  "messages": [
    {"role": "system", "content": "You are a WARNERCO Robotics technical assistant..."},
    {"role": "user", "content": "Tell me about the Atlas Prime."},
    {"role": "assistant", "content": "The Atlas Prime (WC-100) has four documented components..."},
    {"role": "user", "content": "Which of those is deprecated?"},
    {"role": "assistant", "content": "The cable management system (WRN-00021, v1.3) is deprecated..."}
  ]
}
```

## Cost Estimate

Fine-tuning pricing (as of 2025) for `gpt-4o-mini`:
- Training: ~$0.30 per 1M tokens
- This file is approximately 5,000 tokens, so training cost is negligible
- Scaling to 100 examples would still be under $0.01 for a single epoch
