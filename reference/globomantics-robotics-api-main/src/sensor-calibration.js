/**
 * Sensor Calibration - Handles robot sensor calibration procedures
 */

class SensorCalibration {
  constructor(robot) {
    this.robot = robot;
    this.calibrationRanges = {
      temperature: { min: -40, max: 85, unit: 'C' },
      proximity: { min: 0, max: 500, unit: 'cm' },
      pressure: { min: 0, max: 1000, unit: 'kPa' }
    };
  }

  calibrate() {
    const results = {
      robotId: this.robot.id,
      robotName: this.robot.name,
      timestamp: new Date().toISOString(),
      sensors: {},
      status: 'success',
      warnings: []
    };

    // Calibrate each sensor type
    for (const [sensorType, range] of Object.entries(this.calibrationRanges)) {
      const calibrationResult = this.calibrateSensor(sensorType, range);
      results.sensors[sensorType] = calibrationResult;

      if (calibrationResult.status === 'warning') {
        results.warnings.push(`${sensorType}: ${calibrationResult.message}`);
      }
    }

    if (results.warnings.length > 0) {
      results.status = 'completed_with_warnings';
    }

    return results;
  }

  calibrateSensor(sensorType, range) {
    // Simulate calibration by generating realistic values
    const baseValue = this.generateBaseValue(sensorType);
    const offset = this.calculateOffset(baseValue, range);
    const calibratedValue = baseValue + offset;

    const result = {
      type: sensorType,
      rawValue: baseValue,
      calibratedValue: calibratedValue,
      offset: offset,
      unit: range.unit,
      status: 'ok',
      timestamp: new Date().toISOString()
    };

    // Check if value is within acceptable range
    if (calibratedValue < range.min || calibratedValue > range.max) {
      result.status = 'warning';
      result.message = `Value ${calibratedValue}${range.unit} outside normal range`;
    }

    // Check for sensor drift
    if (Math.abs(offset) > (range.max - range.min) * 0.1) {
      result.status = 'warning';
      result.message = `Significant sensor drift detected: ${offset.toFixed(2)}${range.unit}`;
    }

    return result;
  }

  generateBaseValue(sensorType) {
    // Generate realistic base values for demonstration
    const baseValues = {
      temperature: 22 + (Math.random() * 10 - 5), // 17-27 C
      proximity: 100 + (Math.random() * 200),      // 100-300 cm
      pressure: 101.3 + (Math.random() * 10 - 5)   // ~atmospheric pressure in kPa
    };
    return baseValues[sensorType] || 0;
  }

  calculateOffset(baseValue, range) {
    // Small random offset to simulate calibration adjustment
    const maxOffset = (range.max - range.min) * 0.05;
    return (Math.random() * maxOffset * 2) - maxOffset;
  }

  validateSensorHealth(sensorData) {
    const issues = [];

    for (const [sensor, data] of Object.entries(sensorData)) {
      if (!data || data.calibratedValue === null) {
        issues.push(`${sensor}: No data available`);
      } else if (data.status === 'warning') {
        issues.push(`${sensor}: ${data.message}`);
      }
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }
}

module.exports = SensorCalibration;
