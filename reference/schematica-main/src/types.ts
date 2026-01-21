/**
 * Type definitions for Schematica MCP Server
 */

export interface Schematic {
  id: string;
  model: string;
  component: string;
  version: string;
  summary: string;
  url: string;
  last_verified: string;
  category: string;
  status: 'active' | 'deprecated' | 'draft';
}

export interface SchematicResult {
  model: string;
  component: string;
  version: string;
  summary: string;
  url: string;
  last_verified: string;
}

export interface SchematicListItem {
  id: string;
  model: string;
  component: string;
  category: string;
  status: string;
}

export interface FetchSchematicParams {
  query: string;
  model?: string;
  component?: string;
}

export interface ListSchematicsParams {
  category?: string;
  model?: string;
  status?: string;
  limit?: number;
}
