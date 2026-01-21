/**
 * API Integration Tests for Globomantics Robotics API
 */

/* eslint-disable no-unused-vars */

const request = require('supertest');
const app = require('../src/index');

describe('Globomantics Robotics API', () => {
  let robotId;

  describe('Health Check', () => {
    test('GET /health returns healthy status', async () => {
      const response = await request(app).get('/health');

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('version');
    });
  });

  describe('Robot Registration', () => {
    test('POST /api/robots creates a new robot', async () => {
      const robotData = {
        name: 'Assembly-Bot-001',
        type: 'arm',
        location: 'Factory Floor A'
      };

      const response = await request(app)
        .post('/api/robots')
        .send(robotData);

      expect(response.status).toBe(201);
      expect(response.body.name).toBe(robotData.name);
      expect(response.body.type).toBe(robotData.type);
      expect(response.body.status).toBe('idle');
      expect(response.body.batteryLevel).toBe(100);
      expect(response.body).toHaveProperty('id');

      robotId = response.body.id;
    });

    test('POST /api/robots requires name and type', async () => {
      const response = await request(app)
        .post('/api/robots')
        .send({ name: 'Test' });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('required');
    });
  });

  describe('Robot Retrieval', () => {
    test('GET /api/robots returns all robots', async () => {
      const response = await request(app).get('/api/robots');

      expect(response.status).toBe(200);
      expect(Array.isArray(response.body)).toBe(true);
    });

    test('GET /api/robots/:id returns specific robot', async () => {
      // First create a robot
      const createResponse = await request(app)
        .post('/api/robots')
        .send({ name: 'Test-Bot', type: 'mobile' });

      const id = createResponse.body.id;

      const response = await request(app).get(`/api/robots/${id}`);

      expect(response.status).toBe(200);
      expect(response.body.id).toBe(id);
    });

    test('GET /api/robots/:id returns 404 for non-existent robot', async () => {
      const response = await request(app).get('/api/robots/non-existent-id');

      expect(response.status).toBe(404);
    });
  });

  describe('Robot Commands', () => {
    let commandRobotId;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/robots')
        .send({ name: 'Command-Test-Bot', type: 'mobile' });
      commandRobotId = response.body.id;
    });

    test('POST /api/robots/:id/command executes move command', async () => {
      const response = await request(app)
        .post(`/api/robots/${commandRobotId}/command`)
        .send({ command: 'move', parameters: { direction: 'forward', distance: 5 } });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.action).toBe('move');
      expect(response.body.direction).toBe('forward');
    });

    test('POST /api/robots/:id/command executes stop command', async () => {
      const response = await request(app)
        .post(`/api/robots/${commandRobotId}/command`)
        .send({ command: 'stop' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.action).toBe('stop');
    });

    test('POST /api/robots/:id/command rejects invalid command', async () => {
      const response = await request(app)
        .post(`/api/robots/${commandRobotId}/command`)
        .send({ command: 'fly' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Unknown command');
    });

    test('POST /api/robots/:id/command requires command parameter', async () => {
      const response = await request(app)
        .post(`/api/robots/${commandRobotId}/command`)
        .send({});

      expect(response.status).toBe(400);
    });
  });

  describe('Sensor Calibration', () => {
    let calibrationRobotId;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/robots')
        .send({ name: 'Calibration-Test-Bot', type: 'sensor-array' });
      calibrationRobotId = response.body.id;
    });

    test('POST /api/robots/:id/calibrate performs sensor calibration', async () => {
      const response = await request(app)
        .post(`/api/robots/${calibrationRobotId}/calibrate`);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('sensors');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body.sensors).toHaveProperty('temperature');
      expect(response.body.sensors).toHaveProperty('proximity');
      expect(response.body.sensors).toHaveProperty('pressure');
    });

    test('Calibration returns sensor data with proper structure', async () => {
      const response = await request(app)
        .post(`/api/robots/${calibrationRobotId}/calibrate`);

      const tempSensor = response.body.sensors.temperature;
      expect(tempSensor).toHaveProperty('rawValue');
      expect(tempSensor).toHaveProperty('calibratedValue');
      expect(tempSensor).toHaveProperty('offset');
      expect(tempSensor).toHaveProperty('unit');
    });
  });

  describe('Robot Deletion', () => {
    test('DELETE /api/robots/:id removes robot', async () => {
      // Create a robot first
      const createResponse = await request(app)
        .post('/api/robots')
        .send({ name: 'Delete-Test-Bot', type: 'mobile' });

      const id = createResponse.body.id;

      // Delete the robot
      const deleteResponse = await request(app).delete(`/api/robots/${id}`);
      expect(deleteResponse.status).toBe(204);

      // Verify it's gone
      const getResponse = await request(app).get(`/api/robots/${id}`);
      expect(getResponse.status).toBe(404);
    });

    test('DELETE /api/robots/:id returns 404 for non-existent robot', async () => {
      const response = await request(app).delete('/api/robots/non-existent-id');
      expect(response.status).toBe(404);
    });
  });
});
