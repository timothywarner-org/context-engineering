/**
 * Schematic lookup service for Globomantics Robotics
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  Schematic,
  SchematicResult,
  SchematicListItem,
  FetchSchematicParams,
  ListSchematicsParams
} from './types';

export class SchematicService {
  private schematics: Schematic[] = [];

  constructor() {
    this.loadSchematics();
  }

  private loadSchematics(): void {
    const dataPath = path.join(__dirname, '..', 'data', 'schematics.json');
    try {
      const data = fs.readFileSync(dataPath, 'utf-8');
      this.schematics = JSON.parse(data);
      console.log(`Loaded ${this.schematics.length} schematics from database`);
    } catch (error) {
      console.error('Failed to load schematics:', error);
      this.schematics = [];
    }
  }

  /**
   * Parse a natural language query to extract model and component
   */
  private parseQuery(query: string): { model?: string; component?: string } {
    const normalizedQuery = query.toLowerCase();

    // Try to extract model number (patterns like XR-18, MK-9, etc.)
    const modelPattern = /\b([a-z]{2})-?(\d{1,2})\b/i;
    const modelMatch = normalizedQuery.match(modelPattern);
    const model = modelMatch ? `${modelMatch[1].toUpperCase()}-${modelMatch[2]}` : undefined;

    // Common component keywords to look for
    const componentKeywords = [
      'cooling manifold', 'heat sink', 'thermal', 'radiator', 'cooling fan',
      'heat exchanger', 'cryogenic pump', 'coolant',
      'servo', 'stepper motor', 'actuator', 'joint', 'gearbox', 'drive shaft',
      'linear actuator', 'hydraulic', 'pneumatic', 'motor controller',
      'lidar', 'ultrasonic', 'infrared', 'proximity sensor', 'force feedback',
      'gyroscope', 'accelerometer', 'camera', 'depth sensor', 'encoder',
      'power distribution', 'battery', 'voltage regulator', 'capacitor',
      'inverter', 'charging port', 'power supply', 'solar panel', 'fuel cell',
      'control board', 'microcontroller', 'communication', 'signal processor',
      'data bus', 'network adapter', 'wireless', 'diagnostic', 'firmware', 'safety interlock',
      'chassis', 'mounting bracket', 'housing', 'protective casing', 'connector',
      'base plate', 'support beam', 'cable routing', 'access panel', 'shock absorber',
      'gripper', 'end effector', 'wrist', 'finger', 'tool changer',
      'suction cup', 'magnetic gripper', 'payload', 'claw', 'manipulator'
    ];

    let component: string | undefined;
    for (const keyword of componentKeywords) {
      if (normalizedQuery.includes(keyword)) {
        component = keyword;
        break;
      }
    }

    return { model, component };
  }

  /**
   * Calculate relevance score for a schematic against search criteria
   */
  private calculateScore(
    schematic: Schematic,
    model?: string,
    component?: string,
    query?: string
  ): number {
    let score = 0;

    // Exact model match gets highest priority
    if (model && schematic.model.toUpperCase() === model.toUpperCase()) {
      score += 100;
    } else if (model && schematic.model.toUpperCase().includes(model.toUpperCase())) {
      score += 50;
    }

    // Component matching
    if (component) {
      const schematicComponent = schematic.component.toLowerCase();
      const searchComponent = component.toLowerCase();

      if (schematicComponent === searchComponent) {
        score += 80;
      } else if (schematicComponent.includes(searchComponent) || searchComponent.includes(schematicComponent)) {
        score += 40;
      }
    }

    // Query text matching against summary
    if (query) {
      const words = query.toLowerCase().split(/\s+/);
      const summaryLower = schematic.summary.toLowerCase();
      const componentLower = schematic.component.toLowerCase();

      for (const word of words) {
        if (word.length > 2) {
          if (summaryLower.includes(word)) score += 5;
          if (componentLower.includes(word)) score += 10;
        }
      }
    }

    // Prefer active schematics
    if (schematic.status === 'active') score += 10;
    if (schematic.status === 'deprecated') score -= 5;

    return score;
  }

  /**
   * Fetch schematic matching the query
   */
  fetchSchematic(params: FetchSchematicParams): SchematicResult | null {
    const { query, model: explicitModel, component: explicitComponent } = params;

    // Parse query for model and component
    const parsed = this.parseQuery(query);
    const model = explicitModel || parsed.model;
    const component = explicitComponent || parsed.component;

    if (!model && !component && !query) {
      return null;
    }

    // Score all schematics and find best match
    const scored = this.schematics.map(schematic => ({
      schematic,
      score: this.calculateScore(schematic, model, component, query)
    }));

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    // Return best match if score is reasonable
    const best = scored[0];
    if (!best || best.score < 10) {
      return null;
    }

    const { schematic } = best;
    return {
      model: schematic.model,
      component: schematic.component,
      version: schematic.version,
      summary: schematic.summary,
      url: schematic.url,
      last_verified: schematic.last_verified
    };
  }

  /**
   * List all available schematics with optional filtering
   */
  listSchematics(params: ListSchematicsParams = {}): SchematicListItem[] {
    const { category, model, status, limit = 50 } = params;

    let filtered = this.schematics;

    if (category) {
      filtered = filtered.filter(s =>
        s.category.toLowerCase() === category.toLowerCase()
      );
    }

    if (model) {
      filtered = filtered.filter(s =>
        s.model.toUpperCase().includes(model.toUpperCase())
      );
    }

    if (status) {
      filtered = filtered.filter(s =>
        s.status.toLowerCase() === status.toLowerCase()
      );
    }

    // Apply limit
    filtered = filtered.slice(0, Math.min(limit, 100));

    return filtered.map(s => ({
      id: s.id,
      model: s.model,
      component: s.component,
      category: s.category,
      status: s.status
    }));
  }

  /**
   * Get total count of schematics
   */
  getCount(): number {
    return this.schematics.length;
  }

  /**
   * Get available categories
   */
  getCategories(): string[] {
    return [...new Set(this.schematics.map(s => s.category))].sort();
  }
}
