# Quotes Source Directory

This directory contains text files for bulk importing quotes into the Stoic MCP server.

## Usage

1. Create a `.txt` file in this directory
2. Add quotes in the format: `"Quote text" - Author, Source`
3. Run: `npm run import <filename.txt>`

## Format

Each quote should be on a single line:

```
"Quote text here" - Author Name, Source Book
```

## Example

See `sample-import.txt` for an example file.

## Notes

- Lines starting with `#` are treated as comments
- Blank lines are ignored
- Theme is auto-detected from quote text
- All quotes are added with `addedBy: "manual"`
