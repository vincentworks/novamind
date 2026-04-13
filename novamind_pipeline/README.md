# NovaMind AI Marketing Content Pipeline

## Folder structure

```text
novamind_pipeline/
  README.md
  requirements.txt
  /data
    contacts.json
    schema_example.json
    generated_content.json
    campaign_log.json
    performance_log.json
  /src
    generate_content.py
```

## JSON schema

The pipeline stores generated content in a structured JSON format:

```json
{
  "topic": "AI in creative automation",
  "personas": [
    "Creative Agency Founder",
    "Operations Manager",
    "Marketing Lead"
  ],
  "blog_title": "How AI Is Changing Creative Agency Workflows",
  "blog_outline": [
    "Why agencies are overwhelmed by repetitive work",
    "Where AI fits into creative operations",
    "Examples of automations across teams",
    "Risks and best practices",
    "What agencies should do next"
  ],
  "blog_draft": "400-600 word draft goes here",
  "newsletters": {
    "Creative Agency Founder": "Persona-specific email copy",
    "Operations Manager": "Persona-specific email copy",
    "Marketing Lead": "Persona-specific email copy"
  },
  "campaign_metadata": {
    "campaign_id": "cmp_001",
    "campaign_date": "2026-04-13",
    "status": "draft"
  }
}
```

## Run locally

1. Create a `.env` file with:

```bash
OPENAI_API_KEY=your_key_here
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the generator:

```bash
python src/generate_content.py --topic "AI in creative automation"
```

4. Output will be saved to:

```text
data/generated_content.json
```

## Notes

- The script uses three default personas aligned with NovaMind's target audience.
- It generates a blog title, outline, 400-600 word draft, and three customized newsletter versions.
- If no API key is provided, the script falls back to deterministic mock content so the pipeline still works for demo purposes.
