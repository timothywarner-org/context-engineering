# Bulk Quote Import Guide

## Overview

The `import-quotes` utility allows you to bulk import Stoic quotes from a text file into your quotes.json database.

## Usage

```bash
npm run import <filename.txt>
```

**Note:** All import files must be placed in the `local/quotes-source/` directory.

## File Format

Each quote must be on a single line in this format:

```
"Quote text here" - Author Name, Source Book
```

### Example Import File

Create a file in `local/quotes-source/my-quotes.txt`:

```text
# Comments start with # and are ignored
# Blank lines are also ignored

"The impediment to action advances action. What stands in the way becomes the way." - Marcus Aurelius, Meditations
"Man is not worried by real problems so much as by his imagined anxieties about real problems." - Epictetus, Discourses
"If you are distressed by anything external, the pain is not due to the thing itself, but to your estimate of it." - Marcus Aurelius, Meditations
```

Then import:

```bash
npm run import my-quotes.txt
```

## Features

### Automatic ID Generation
- IDs are generated sequentially starting from `metadata.lastId + 1`
- The `lastId` metadata is automatically updated after import

### Theme Detection
The utility automatically detects themes based on keywords in the quote text:

| Theme | Keywords |
|-------|----------|
| anxiety | anxiety, anxious, worry, fear, stress |
| courage | courage, courageous, brave, bravery, bold |
| control | control, power, influence, agency |
| mindset | mind, thought, thinking, perspective, view |
| discipline | discipline, practice, habit, training |
| wisdom | wisdom, wise, knowledge, understanding |
| adversity | adversity, difficulty, challenge, obstacle, hardship |
| resilience | resilience, strength, endurance, perseverance |
| virtue | virtue, virtuous, good, moral, character |
| presence | present, now, moment, time |
| gratitude | gratitude, grateful, thankful, appreciate |
| action | action, do, doing, act |
| integrity | integrity, truth, honest, honor |
| contentment | contentment, content, satisfaction, enough |
| preparation | preparation, prepare, ready |
| opportunity | opportunity, chance, luck |
| purpose | purpose, goal, aim, direction |
| response | response, react, reaction, happen |

If no keywords match, the default theme is **wisdom**.

### Metadata Fields
All imported quotes receive:
- **id**: Auto-generated numeric ID
- **favorite**: `false`
- **notes**: `null`
- **createdAt**: Current timestamp (same for all quotes in one import)
- **addedBy**: `"manual"`

## Example Session

### 1. Create Import File

Create `local/quotes-source/my-quotes.txt`:
```text
"The best time to plant a tree was 20 years ago. The second best time is now." - Chinese Proverb, Traditional Wisdom
"A journey of a thousand miles begins with a single step." - Lao Tzu, Tao Te Ching
```

### 2. Run Import

```bash
cd local
npm run import my-quotes.txt
```

### 3. Output

```
Reading from: C:\github\stoic-mcp\local\quotes-source\my-quotes.txt
Found 2 lines to process...
Successfully parsed 2 quotes
✓ Successfully imported 2 quotes
  New quote IDs: 24 - 25
  Total quotes: 25
```

## Error Handling

### Invalid Format
If a line doesn't match the expected format, you'll see a warning:
```
Warning: Could not parse line: This is not a valid quote format
```

The import continues with other lines.

### File Not Found
```
Error: ENOENT: no such file or directory, open 'nonexistent.txt'
```

### Empty File
```
No valid quotes found in file
```

## Database Schema

After import, quotes.json will have this structure:

```json
{
  "metadata": {
    "lastId": 23,
    "version": "1.0.0",
    "lastModified": "2025-10-23T19:51:47.559Z"
  },
  "quotes": [
    {
      "id": 21,
      "text": "Quote text here",
      "author": "Author Name",
      "source": "Source Book",
      "theme": "wisdom",
      "favorite": false,
      "notes": null,
      "createdAt": "2025-10-23T19:51:47.559Z",
      "addedBy": "manual"
    }
  ]
}
```

## Atomic Operations

The import process is atomic:
- All quotes are validated before writing
- If validation fails, no changes are made to quotes.json
- The file is written in a single operation
- Metadata is updated simultaneously

## Tips

1. **Test First**: Use `sample-import.txt` to test the import process: `npm run import sample-import.txt`
2. **Organized Files**: Keep different quote collections in separate files in `quotes-source/`
3. **Backup**: Keep a backup of quotes.json before large imports
4. **Review Themes**: Check that auto-detected themes are appropriate
5. **Batch Imports**: You can run multiple imports - IDs will continue sequentially

## Troubleshooting

### Wrong Theme Detected
Edit quotes.json manually to fix the theme, or modify the quote text to include better keywords.

### Duplicate Quotes
The utility doesn't check for duplicates. Review your import file before running.

### Line Breaks in Quotes
The parser expects one quote per line. Multi-line quotes are not supported. Use `\n` in the text if needed, or combine into a single line.

## Related

- See `DEMO_RUNBOOK.md` for MCP server usage
- See `README.md` for overall project documentation
