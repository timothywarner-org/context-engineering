# 🔨 Build Reminder

## IMPORTANT: Always Rebuild After Code Changes!

The MCP server runs the **compiled JavaScript** in `dist/`, not the TypeScript source files.

### When to Rebuild

Rebuild after making changes to:
- ✅ `src/index.ts` - MCP server handlers
- ✅ `src/storage.ts` - Storage layer
- ✅ `src/deepseek.ts` - AI integration
- ✅ `src/types.ts` - TypeScript interfaces
- ✅ `src/import-quotes.ts` - Import utility
- ✅ Any other `.ts` files

### How to Rebuild

```bash
cd local
npm run build
```

Or clean build:
```bash
npm run clean
npm run build
```

### Signs You Need to Rebuild

❌ **Claude Desktop hangs when calling MCP server**
- Likely cause: Old compiled code doesn't match new schema

❌ **TypeScript errors but server still runs**
- Cause: Running old build from before errors were introduced

❌ **Changes not taking effect**
- Cause: Forgot to rebuild after code changes

### Automatic Rebuild

The `npm start` command includes auto-rebuild:
```bash
npm start  # Runs: npm run build --if-present && node dist/index.js
```

But Claude Desktop uses the **direct node command**, so you must build manually.

### Development Workflow

#### Option 1: Manual Build (Recommended for Claude Desktop)
```bash
# 1. Make changes to TypeScript files
# 2. Build
npm run build

# 3. Restart Claude Desktop to load new code
```

#### Option 2: Watch Mode (For Active Development)
```bash
# In one terminal - auto-rebuild on file changes
npm run watch

# Claude Desktop will use the newly built files on restart
```

#### Option 3: Dev Mode (Testing Only)
```bash
# Auto-build and run
npm run dev
```

### Quick Reference

| Command | What It Does |
|---------|--------------|
| `npm run build` | Compile TypeScript → JavaScript |
| `npm run clean` | Delete `dist/` folder |
| `npm run watch` | Auto-rebuild on file changes |
| `npm run dev` | Build + run server once |
| `npm start` | Build (if needed) + run server |
| `npm run import <file>` | Build + import quotes |

### Claude Desktop Integration

Since Claude Desktop config points to `dist/index.js`:
```json
{
  "command": "node",
  "args": ["C:\\github\\stoic-mcp\\local\\dist\\index.js"]
}
```

You must:
1. **Build** after TypeScript changes
2. **Restart Claude Desktop** to load new code

### Pro Tip: Use Watch Mode

For active development, keep watch mode running:

```bash
# Terminal 1: Auto-rebuild
cd local
npm run watch

# Make changes in your editor
# Files rebuild automatically

# Restart Claude Desktop to test changes
```

### Pre-Flight Checklist

Before restarting Claude Desktop:
- [ ] All TypeScript files saved
- [ ] `npm run build` completed successfully
- [ ] No TypeScript errors in output
- [ ] `dist/index.js` exists and has recent timestamp

### Troubleshooting

**Q: Claude Desktop still hangs after rebuild**

A: Ensure:
1. Build completed with zero errors
2. You fully quit and restarted Claude Desktop (not just refresh)
3. Path in config is correct: `C:\\github\\stoic-mcp\\local\\dist\\index.js`

**Q: Changes not appearing**

A:
1. Check file timestamp: `ls -l dist/index.js`
2. Rebuild: `npm run build`
3. Hard restart Claude Desktop

**Q: Import errors in build**

A: Check that imports use `.js` extension:
```typescript
// ✅ Correct
import { Quote } from './types.js';

// ❌ Wrong
import { Quote } from './types';
```

## Remember: Build → Restart → Test

🔨 **Build** the TypeScript
🔄 **Restart** Claude Desktop
✅ **Test** your changes

---

**Don't forget: If the MCP server hangs, rebuild first!**
