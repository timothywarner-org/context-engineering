/**
 * Globomantics Robotics Control API
 * Main entry point for the robot control system
 */

const express = require('express');
const { v4: uuidv4 } = require('uuid');
const logger = require('./logger');
const RobotController = require('./robot-controller');
const SensorCalibration = require('./sensor-calibration');

const app = express();
app.use(express.json());

// Robot fleet storage
const robots = new Map();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

// List all robots
app.get('/api/robots', (req, res) => {
  const robotList = Array.from(robots.values());
  logger.info(`Listed ${robotList.length} robots`);
  res.json(robotList);
});

// Get robot by ID
app.get('/api/robots/:id', (req, res) => {
  const robot = robots.get(req.params.id);
  if (!robot) {
    return res.status(404).json({ error: 'Robot not found' });
  }
  res.json(robot);
});

// Register new robot
app.post('/api/robots', (req, res) => {
  const { name, type, location } = req.body;

  if (!name || !type) {
    return res.status(400).json({ error: 'Name and type are required' });
  }

  const robot = {
    id: uuidv4(),
    name,
    type,
    location: location || 'unknown',
    status: 'idle',
    batteryLevel: 100,
    sensors: {
      temperature: null,
      proximity: null,
      pressure: null
    },
    createdAt: new Date().toISOString(),
    lastCalibration: null
  };

  robots.set(robot.id, robot);
  logger.info(`Registered new robot: ${robot.name} (${robot.id})`);
  res.status(201).json(robot);
});

// Send command to robot
app.post('/api/robots/:id/command', (req, res) => {
  const robot = robots.get(req.params.id);
  if (!robot) {
    return res.status(404).json({ error: 'Robot not found' });
  }

  const { command, parameters } = req.body;
  if (!command) {
    return res.status(400).json({ error: 'Command is required' });
  }

  const controller = new RobotController(robot);
  const result = controller.execute(command, parameters);

  // Update robot state
  robots.set(robot.id, controller.getRobot());

  logger.info(`Executed command '${command}' on robot ${robot.id}`);
  res.json(result);
});

// Calibrate robot sensors
app.post('/api/robots/:id/calibrate', (req, res) => {
  const robot = robots.get(req.params.id);
  if (!robot) {
    return res.status(404).json({ error: 'Robot not found' });
  }

  const calibration = new SensorCalibration(robot);
  const result = calibration.calibrate();

  // Update robot with calibration results
  robot.sensors = result.sensors;
  robot.lastCalibration = result.timestamp;
  robots.set(robot.id, robot);

  logger.info(`Calibrated sensors for robot ${robot.id}`);
  res.json(result);
});

// Delete robot
app.delete('/api/robots/:id', (req, res) => {
  if (!robots.has(req.params.id)) {
    return res.status(404).json({ error: 'Robot not found' });
  }

  robots.delete(req.params.id);
  logger.info(`Deleted robot ${req.params.id}`);
  res.status(204).send();
});

// Export for testing
module.exports = app;

// Start server if run directly
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    logger.info(`Globomantics Robotics API running on port ${PORT}`);
  });
}
