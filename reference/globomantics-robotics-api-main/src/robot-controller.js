/**
 * Robot Controller - Handles robot commands and state management
 */

class RobotController {
  constructor(robot) {
    this.robot = { ...robot };
    this.commands = {
      'move': this.move.bind(this),
      'stop': this.stop.bind(this),
      'rotate': this.rotate.bind(this),
      'grab': this.grab.bind(this),
      'release': this.release.bind(this),
      'charge': this.charge.bind(this)
    };
  }

  execute(command, parameters = {}) {
    const handler = this.commands[command];
    if (!handler) {
      return {
        success: false,
        error: `Unknown command: ${command}`,
        availableCommands: Object.keys(this.commands)
      };
    }

    if (this.robot.batteryLevel <= 0 && command !== 'charge') {
      return {
        success: false,
        error: 'Battery depleted. Please charge the robot.'
      };
    }

    return handler(parameters);
  }

  move(params) {
    const { direction = 'forward', distance = 1 } = params;
    const validDirections = ['forward', 'backward', 'left', 'right'];

    if (!validDirections.includes(direction)) {
      return {
        success: false,
        error: `Invalid direction. Use: ${validDirections.join(', ')}`
      };
    }

    this.robot.status = 'moving';
    this.robot.batteryLevel = Math.max(0, this.robot.batteryLevel - distance * 2);

    return {
      success: true,
      action: 'move',
      direction,
      distance,
      newBatteryLevel: this.robot.batteryLevel
    };
  }

  stop() {
    this.robot.status = 'idle';
    return {
      success: true,
      action: 'stop',
      status: this.robot.status
    };
  }

  rotate(params) {
    const { degrees = 90 } = params;
    this.robot.status = 'rotating';
    this.robot.batteryLevel = Math.max(0, this.robot.batteryLevel - Math.abs(degrees) / 90);

    return {
      success: true,
      action: 'rotate',
      degrees,
      newBatteryLevel: this.robot.batteryLevel
    };
  }

  grab() {
    if (this.robot.type !== 'arm' && this.robot.type !== 'manipulator') {
      return {
        success: false,
        error: 'This robot type does not support grab operations'
      };
    }

    this.robot.status = 'grabbing';
    this.robot.batteryLevel = Math.max(0, this.robot.batteryLevel - 5);

    return {
      success: true,
      action: 'grab',
      newBatteryLevel: this.robot.batteryLevel
    };
  }

  release() {
    if (this.robot.type !== 'arm' && this.robot.type !== 'manipulator') {
      return {
        success: false,
        error: 'This robot type does not support release operations'
      };
    }

    this.robot.status = 'releasing';
    this.robot.batteryLevel = Math.max(0, this.robot.batteryLevel - 2);

    return {
      success: true,
      action: 'release',
      newBatteryLevel: this.robot.batteryLevel
    };
  }

  charge() {
    this.robot.status = 'charging';
    this.robot.batteryLevel = 100;

    return {
      success: true,
      action: 'charge',
      newBatteryLevel: this.robot.batteryLevel
    };
  }

  getRobot() {
    return this.robot;
  }
}

module.exports = RobotController;
