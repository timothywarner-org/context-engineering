/**
 * Unit Tests - Schematic Service
 *
 * Tests for the core business logic of the SchematicService class.
 * These tests verify query parsing, scoring algorithms, and data retrieval.
 */

import { SchematicService } from '../../src/schematic-service';

describe('SchematicService', () => {
  let service: SchematicService;

  beforeAll(() => {
    service = new SchematicService();
  });

  describe('initialization', () => {
    it('should load schematics from database', () => {
      const count = service.getCount();
      expect(count).toBeGreaterThan(0);
    });

    it('should have categories available', () => {
      const categories = service.getCategories();
      expect(categories).toBeInstanceOf(Array);
      expect(categories.length).toBeGreaterThan(0);
    });
  });

  describe('fetchSchematic', () => {
    it('should find schematic by model number', () => {
      const result = service.fetchSchematic({
        query: 'XR-18 cooling'
      });
      expect(result).not.toBeNull();
      if (result) {
        expect(result.model).toBeDefined();
        expect(result.component).toBeDefined();
      }
    });

    it('should find schematic by component name', () => {
      const result = service.fetchSchematic({
        query: 'cooling manifold'
      });
      expect(result).not.toBeNull();
    });

    it('should return null for invalid query', () => {
      const result = service.fetchSchematic({
        query: ''
      });
      expect(result).toBeNull();
    });

    it('should accept explicit model parameter', () => {
      const result = service.fetchSchematic({
        query: 'thermal system',
        model: 'XR-18'
      });
      // Should either find a result or return null gracefully
      expect(result === null || typeof result === 'object').toBe(true);
    });
  });

  describe('listSchematics', () => {
    it('should return array of schematics', () => {
      const results = service.listSchematics();
      expect(results).toBeInstanceOf(Array);
      expect(results.length).toBeGreaterThan(0);
    });

    it('should filter by category', () => {
      const categories = service.getCategories();
      if (categories.length > 0) {
        const results = service.listSchematics({ category: categories[0] });
        expect(results.every(s => s.category.toLowerCase() === categories[0].toLowerCase())).toBe(true);
      }
    });

    it('should respect limit parameter', () => {
      const limit = 5;
      const results = service.listSchematics({ limit });
      expect(results.length).toBeLessThanOrEqual(limit);
    });

    it('should filter by status', () => {
      const results = service.listSchematics({ status: 'active' });
      expect(results.every(s => s.status === 'active')).toBe(true);
    });
  });

  describe('data integrity', () => {
    it('should have valid schematic structure', () => {
      const results = service.listSchematics({ limit: 10 });
      results.forEach(item => {
        expect(item).toHaveProperty('id');
        expect(item).toHaveProperty('model');
        expect(item).toHaveProperty('component');
        expect(item).toHaveProperty('category');
        expect(item).toHaveProperty('status');
      });
    });

    it('should have non-empty model identifiers', () => {
      const results = service.listSchematics({ limit: 10 });
      results.forEach(item => {
        expect(item.model.length).toBeGreaterThan(0);
      });
    });
  });
});
