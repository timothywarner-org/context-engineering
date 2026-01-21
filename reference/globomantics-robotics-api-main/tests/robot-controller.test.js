/**
 * Unit Tests for Robot Controller
 */

const RobotController = require('../src/robot-controller');

describe('RobotController', () => {
  let controller;
  let testRobot;

  beforeEach(() => {
    testRobot = {
      id: 'test-123',
      name: 'Test Robot',
      type: 'arm',
      status: 'idle',
      batteryLevel: 100
    };
    controller = new RobotController(testRobot);
  });

  describe('Move Command', () => {
    test('moves robot forward by default', () => {
      const result = controller.execute('move', {});

      expect(result.success).toBe(true);
      expect(result.direction).toBe('forward');
      expect(result.distance).toBe(1);
    });

    test('moves robot in specified direction', () => {
      const result = controller.execute('move', { direction: 'backward', distance: 3 });

      expect(result.success).toBe(true);
      expect(result.direction).toBe('backward');
      expect(result.distance).toBe(3);
    });

    test('rejects invalid direction', () => {
      const result = controller.execute('move', { direction: 'up' });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid direction');
    });

    test('drains battery when moving', () => {
      const initialBattery = testRobot.batteryLevel;
      const result = controller.execute('move', { distance: 10 });

      expect(result.newBatteryLevel).toBeLessThan(initialBattery);
    });
  });

  describe('Rotate Command', () => {
    test('rotates robot by 90 degrees by default', () => {
      const result = controller.execute('rotate', {});

      expect(result.success).toBe(true);
      expect(result.degrees).toBe(90);
    });

    test('rotates by specified degrees', () => {
      const result = controller.execute('rotate', { degrees: 180 });

      expect(result.success).toBe(true);
      expect(result.degrees).toBe(180);
    });
  });

  describe('Stop Command', () => {
    test('stops robot and sets status to idle', () => {
      controller.execute('move', {});
      const result = controller.execute('stop');

      expect(result.success).toBe(true);
      expect(result.status).toBe('idle');
    });
  });

  describe('Grab/Release Commands', () => {
    test('grab command works for arm type robot', () => {
      const result = controller.execute('grab');

      expect(result.success).toBe(true);
      expect(result.action).toBe('grab');
    });

    test('grab command fails for non-arm robot', () => {
      testRobot.type = 'mobile';
      controller = new RobotController(testRobot);

      const result = controller.execute('grab');

      expect(result.success).toBe(false);
      expect(result.error).toContain('does not support');
    });

    test('release command works for arm type robot', () => {
      const result = controller.execute('release');

      expect(result.success).toBe(true);
      expect(result.action).toBe('release');
    });
  });

  describe('Charge Command', () => {
    test('charge command restores battery to 100%', () => {
      // Drain battery first
      controller.execute('move', { distance: 20 });

      const result = controller.execute('charge');

      expect(result.success).toBe(true);
      expect(result.newBatteryLevel).toBe(100);
    });
  });

  describe('Battery Management', () => {
    test('rejects commands when battery is depleted', () => {
      testRobot.batteryLevel = 0;
      controller = new RobotController(testRobot);

      const result = controller.execute('move', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('Battery depleted');
    });

    test('allows charge command even with depleted battery', () => {
      testRobot.batteryLevel = 0;
      controller = new RobotController(testRobot);

      const result = controller.execute('charge');

      expect(result.success).toBe(true);
    });
  });

  describe('Unknown Commands', () => {
    test('rejects unknown commands', () => {
      const result = controller.execute('fly', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unknown command');
      expect(result.availableCommands).toContain('move');
    });
  });

  describe('getRobot()', () => {
    test('returns current robot state', () => {
      controller.execute('move', { distance: 5 });
      const robot = controller.getRobot();

      expect(robot.status).toBe('moving');
      expect(robot.batteryLevel).toBeLessThan(100);
    });
  });
});
