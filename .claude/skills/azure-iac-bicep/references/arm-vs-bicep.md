# ARM vs Bicep: Decision and Migration

Load when deciding the IaC language or migrating legacy ARM JSON to Bicep.

## The decision

**Default to Bicep for all new Azure-native IaC.** It compiles to ARM JSON, so anything ARM can deploy, Bicep can author, with a fraction of the syntax noise and far better tooling (type checking, IntelliSense, modules, what-if integration).

| Concern | Bicep | ARM JSON | Terraform |
|---------|-------|----------|-----------|
| Azure-native, day-one resource support | Yes | Yes | Lags provider updates |
| Authoring ergonomics | Concise DSL, typed | Verbose JSON, untyped | HCL, typed |
| State management | Stateless (Azure is the state) | Stateless | External state file to secure and lock |
| Multi-cloud | Azure only | Azure only | Yes |
| Preview before apply | `what-if` | `what-if` | `plan` |
| Best fit | Azure-only shops, fastest path to new services | Legacy you have not yet migrated | Multi-cloud estates, existing Terraform investment |

**Recommendation for this repo:** Bicep first. ARM JSON only as the compiled artifact or when a tool consumes raw templates. Terraform only when an existing multi-cloud Terraform estate forces the issue. For Terraform-on-Azure specifics, call `mcp__azure__azureterraformbestpractices`.

## Migrating ARM JSON to Bicep

Never hand-rewrite. Decompile, then clean up.

```bash
# Decompile an existing ARM template to Bicep. Best-effort; review the output.
az bicep decompile --file azuredeploy.json
```

Decompilation is lossy in predictable ways. After decompiling, do a cleanup pass:

1. **Replace generated variable names.** The decompiler emits names like `variables_storageAccount_name`. Rename to intent-revealing identifiers.
2. **Collapse `concat()` and `format()` into interpolation.** `concat('st', parameters('env'))` becomes `'st${env}'`.
3. **Re-introduce modules.** A monolithic ARM template decompiles to a monolithic Bicep file. Extract reusable units into `modules/`.
4. **Replace `reference()` and `resourceId()` strings** with direct symbolic references (`storage.id`, `storage.properties.primaryEndpoints.blob`).
5. **Add decorators.** Decompiled params have no `@description`, `@allowed`, or constraints. Add them.
6. **Confirm apiVersions.** Decompilation preserves whatever the ARM template had, which may be stale. Check each against `mcp__azure__bicepschema` and bump where safe.
7. **Verify equivalence with what-if.** Run `what-if` against the live environment. A clean migration shows **no changes** for already-deployed resources.

## What decompilation cannot recover

- Original comments and intent (gone in the JSON).
- Module boundaries (everything is flat).
- Parameter constraints beyond `allowedValues`.

Treat the decompiled file as a starting skeleton, not a finished module. The cleanup is the actual work.
