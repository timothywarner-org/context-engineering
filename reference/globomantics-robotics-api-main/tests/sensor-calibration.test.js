/**
 * Unit Tests for Sensor Calibration
 */

const SensorCalibration = require('../src/sensor-calibration');

describe('SensorCalibration', () => {
  let calibration;
  let testRobot;

  beforeEach(() => {
    testRobot = {
      id: 'sensor-test-123',
      name: 'Sensor Test Robot',
      type: 'sensor-array'
    };
    calibration = new SensorCalibration(testRobot);
  });

  describe('calibrate()', () => {
    test('returns calibration results with all sensor types', () => {
      const result = calibration.calibrate();

      expect(result).toHaveProperty('sensors');
      expect(result.sensors).toHaveProperty('temperature');
      expect(result.sensors).toHaveProperty('proximity');
      expect(result.sensors).toHaveProperty('pressure');
    });

    test('includes robot identification in results', () => {
      const result = calibration.calibrate();

      expect(result.robotId).toBe(testRobot.id);
      expect(result.robotName).toBe(testRobot.name);
    });

    test('includes timestamp in results', () => {
      const result = calibration.calibrate();

      expect(result).toHaveProperty('timestamp');
      expect(new Date(result.timestamp)).toBeInstanceOf(Date);
    });

    test('returns success status for normal calibration', () => {
      const result = calibration.calibrate();

      expect(['success', 'completed_with_warnings']).toContain(result.status);
    });
  });

  describe('calibrateSensor()', () => {
    test('returns proper sensor data structure', () => {
      const range = { min: 0, max: 100, unit: 'test' };
      const result = calibration.calibrateSensor('test', range);

      expect(result).toHaveProperty('type');
      expect(result).toHaveProperty('rawValue');
      expect(result).toHaveProperty('calibratedValue');
      expect(result).toHaveProperty('offset');
      expect(result).toHaveProperty('unit');
      expect(result).toHaveProperty('status');
    });

    test('calculates offset between raw and calibrated values', () => {
      const range = { min: 0, max: 100, unit: 'test' };
      const result = calibration.calibrateSensor('test', range);

      const expectedOffset = result.calibratedValue - result.rawValue;
      expect(result.offset).toBeCloseTo(expectedOffset, 5);
    });
  });

  describe('generateBaseValue()', () => {
    test('generates temperature values in expected range', () => {
      const value = calibration.generateBaseValue('temperature');

      expect(value).toBeGreaterThanOrEqual(17);
      expect(value).toBeLessThanOrEqual(27);
    });

    test('generates proximity values in expected range', () => {
      const value = calibration.generateBaseValue('proximity');

      expect(value).toBeGreaterThanOrEqual(100);
      expect(value).toBeLessThanOrEqual(300);
    });

    test('generates pressure values around atmospheric pressure', () => {
      const value = calibration.generateBaseValue('pressure');

      expect(value).toBeGreaterThanOrEqual(96);
      expect(value).toBeLessThanOrEqual(106);
    });

    test('returns 0 for unknown sensor type', () => {
      const value = calibration.generateBaseValue('unknown');

      expect(value).toBe(0);
    });
  });

  describe('validateSensorHealth()', () => {
    test('returns healthy status for good sensor data', () => {
      const sensorData = {
        temperature: { calibratedValue: 22, status: 'ok' },
        proximity: { calibratedValue: 150, status: 'ok' }
      };

      const result = calibration.validateSensorHealth(sensorData);

      expect(result.healthy).toBe(true);
      expect(result.issues).toHaveLength(0);
    });

    test('identifies sensors with no data', () => {
      const sensorData = {
        temperature: null,
        proximity: { calibratedValue: 150, status: 'ok' }
      };

      const result = calibration.validateSensorHealth(sensorData);

      expect(result.healthy).toBe(false);
      expect(result.issues).toContain('temperature: No data available');
    });

    test('identifies sensors with warnings', () => {
      const sensorData = {
        temperature: {
          calibratedValue: 22,
          status: 'warning',
          message: 'Sensor drift detected'
        }
      };

      const result = calibration.validateSensorHealth(sensorData);

      expect(result.healthy).toBe(false);
      expect(result.issues[0]).toContain('Sensor drift detected');
    });
  });
});
