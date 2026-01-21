/**
 * Script to generate synthetic schematic data for Globomantics Robotics
 */

import * as fs from 'fs';
import * as path from 'path';

interface Schematic {
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

// Model prefixes and numbers
const modelPrefixes = ['XR', 'MK', 'GR', 'RM', 'AX', 'TX', 'VX', 'ZR', 'HX', 'DR', 'SR', 'CX', 'NX', 'PX', 'QR'];
const modelNumbers = Array.from({ length: 50 }, (_, i) => i + 1);

// Component categories and specific components
const components: Record<string, string[]> = {
  'thermal': [
    'cooling manifold',
    'heat sink assembly',
    'thermal paste applicator',
    'radiator unit',
    'cooling fan array',
    'heat exchanger',
    'thermal control module',
    'cryogenic pump',
    'thermal sensor array',
    'coolant reservoir'
  ],
  'motion': [
    'servo assembly',
    'stepper motor unit',
    'actuator array',
    'joint mechanism',
    'gearbox assembly',
    'drive shaft',
    'linear actuator',
    'hydraulic cylinder',
    'pneumatic valve',
    'motor controller'
  ],
  'sensors': [
    'LIDAR array',
    'ultrasonic sensor bank',
    'infrared detector',
    'proximity sensor',
    'force feedback sensor',
    'gyroscope module',
    'accelerometer unit',
    'vision camera array',
    'depth sensor',
    'encoder assembly'
  ],
  'power': [
    'power distribution unit',
    'battery management system',
    'voltage regulator',
    'capacitor bank',
    'inverter module',
    'charging port assembly',
    'power supply unit',
    'solar panel interface',
    'fuel cell connector',
    'emergency power cutoff'
  ],
  'control': [
    'main control board',
    'microcontroller unit',
    'communication module',
    'signal processor',
    'data bus interface',
    'network adapter',
    'wireless transceiver',
    'diagnostic port',
    'firmware module',
    'safety interlock'
  ],
  'structural': [
    'chassis frame',
    'mounting bracket',
    'housing assembly',
    'protective casing',
    'joint connector',
    'base plate',
    'support beam',
    'cable routing channel',
    'access panel',
    'shock absorber mount'
  ],
  'manipulation': [
    'gripper assembly',
    'end effector mount',
    'wrist mechanism',
    'finger actuator',
    'tool changer',
    'suction cup array',
    'magnetic gripper',
    'payload interface',
    'articulated claw',
    'precision manipulator'
  ]
};

// Summary templates
const summaryTemplates = [
  'Controls {function} for {model} units in standard operating conditions.',
  'Manages {function} across all {model} series configurations.',
  'Provides {function} capability for enhanced {model} performance.',
  'Regulates {function} to maintain optimal {model} operation.',
  'Handles {function} subsystem for {model} robotic platforms.',
  'Integrates {function} with primary {model} control systems.',
  'Monitors and adjusts {function} parameters in {model} assemblies.',
  'Delivers {function} support for {model} industrial applications.',
  'Coordinates {function} activities in {model} autonomous systems.',
  'Enables {function} features for {model} production models.'
];

const functionDescriptions: Record<string, string[]> = {
  'thermal': ['coolant flow', 'heat dissipation', 'temperature regulation', 'thermal management', 'cooling operations'],
  'motion': ['movement control', 'torque distribution', 'speed regulation', 'position tracking', 'motion coordination'],
  'sensors': ['environmental sensing', 'object detection', 'spatial mapping', 'proximity detection', 'data acquisition'],
  'power': ['power distribution', 'energy management', 'voltage regulation', 'charge cycling', 'power flow'],
  'control': ['signal routing', 'command processing', 'system coordination', 'communication handling', 'diagnostic operations'],
  'structural': ['load bearing', 'component mounting', 'structural integrity', 'vibration dampening', 'physical protection'],
  'manipulation': ['object handling', 'grip control', 'tool management', 'payload operations', 'manipulation tasks']
};

function randomElement<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generateVersion(): string {
  const major = Math.floor(Math.random() * 5) + 1;
  const minor = Math.floor(Math.random() * 10);
  const patch = Math.random() > 0.7 ? `.${Math.floor(Math.random() * 10)}` : '';
  return `v${major}.${minor}${patch}`;
}

function generateDate(): string {
  const year = 2023 + Math.floor(Math.random() * 3);
  const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
  const day = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function generateStatus(): 'active' | 'deprecated' | 'draft' {
  const rand = Math.random();
  if (rand < 0.75) return 'active';
  if (rand < 0.9) return 'deprecated';
  return 'draft';
}

function generateSchematic(id: number): Schematic {
  const prefix = randomElement(modelPrefixes);
  const number = randomElement(modelNumbers);
  const model = `${prefix}-${number}`;

  const category = randomElement(Object.keys(components));
  const component = randomElement(components[category]);
  const version = generateVersion();

  const template = randomElement(summaryTemplates);
  const func = randomElement(functionDescriptions[category]);
  const summary = template.replace('{function}', func).replace('{model}', model);

  const urlComponent = component.toLowerCase().replace(/\s+/g, '_');
  const urlModel = model.toLowerCase();
  const url = `https://schematics.globomantics.io/${urlModel}/${urlComponent}_${version.replace(/\./g, '_')}.pdf`;

  return {
    id: `SCH-${String(id).padStart(5, '0')}`,
    model,
    component,
    version,
    summary,
    url,
    last_verified: generateDate(),
    category,
    status: generateStatus()
  };
}

function main(): void {
  const schematics: Schematic[] = [];

  // Generate 250 schematics for good coverage
  for (let i = 1; i <= 250; i++) {
    schematics.push(generateSchematic(i));
  }

  // Sort by model then component for easier browsing
  schematics.sort((a, b) => {
    if (a.model !== b.model) return a.model.localeCompare(b.model);
    return a.component.localeCompare(b.component);
  });

  const outputPath = path.join(__dirname, '..', 'data', 'schematics.json');
  fs.writeFileSync(outputPath, JSON.stringify(schematics, null, 2));

  console.log(`Generated ${schematics.length} schematics to ${outputPath}`);
  console.log(`Categories covered: ${Object.keys(components).join(', ')}`);
  console.log(`Model prefixes: ${modelPrefixes.join(', ')}`);
}

main();
