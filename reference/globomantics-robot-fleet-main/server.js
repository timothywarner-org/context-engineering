const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const path = require('path');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const _ = require('lodash');
const moment = require('moment');
const axios = require('axios');
const helmet = require('helmet');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware (minimal for demo purposes)
app.use(helmet({
    contentSecurityPolicy: false // Intentionally disabled for demo
}));
app.use(cors());

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
    secret: 'globomantics-secret-key', // Intentionally weak for demo
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Intentionally insecure for demo
}));

// Set view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Mock database (in-memory for demo)
let robots = [
    {
        id: 1,
        name: 'Atlas-Prime',
        model: 'GX-2000',
        status: 'Active',
        location: 'Warehouse A',
        batteryLevel: 87,
        lastMaintenance: '2023-12-01',
        assignedTask: 'Package Sorting'
    },
    {
        id: 2,
        name: 'Beta-Unit',
        model: 'GX-1500',
        status: 'Maintenance',
        location: 'Service Bay 1',
        batteryLevel: 23,
        lastMaintenance: '2023-11-28',
        assignedTask: 'Under Repair'
    },
    {
        id: 3,
        name: 'Charlie-Loader',
        model: 'HL-3000',
        status: 'Active',
        location: 'Loading Dock B',
        batteryLevel: 95,
        lastMaintenance: '2023-12-03',
        assignedTask: 'Heavy Lifting'
    }
];

let users = [
    {
        id: 1,
        username: 'admin',
        password: '$2b$10$rOFLC.b8.TaEZQZlpJo.h.D8J8J1J.1J', // 'password123'
        role: 'Administrator'
    }
];

// Routes
app.get('/', (req, res) => {
    res.render('dashboard', {
        title: 'Globomantics Robot Fleet Manager',
        robots: robots,
        totalRobots: robots.length,
        activeRobots: robots.filter(r => r.status === 'Active').length,
        moment: moment
    });
});

app.get('/robots', (req, res) => {
    res.render('robots', {
        title: 'Robot Fleet - Globomantics',
        robots: robots,
        moment: moment
    });
});

app.get('/robot/:id', (req, res) => {
    const robotId = parseInt(req.params.id);
    const robot = robots.find(r => r.id === robotId);

    if (!robot) {
        return res.status(404).render('error', {
            title: 'Robot Not Found',
            message: 'The requested robot could not be found.'
        });
    }

    res.render('robot-detail', {
        title: `${robot.name} - Globomantics`,
        robot: robot,
        moment: moment
    });
});

app.post('/robot/:id/update', (req, res) => {
    const robotId = parseInt(req.params.id);
    const robot = robots.find(r => r.id === robotId);

    if (robot) {
        // Intentionally using unsafe merge for demo purposes
        _.merge(robot, req.body);
        res.redirect(`/robot/${robotId}`);
    } else {
        res.status(404).send('Robot not found');
    }
});

app.get('/maintenance', (req, res) => {
    const maintenanceRobots = robots.filter(r => r.status === 'Maintenance');
    res.render('maintenance', {
        title: 'Maintenance Schedule - Globomantics',
        robots: maintenanceRobots,
        moment: moment
    });
});

app.get('/api/robots', (req, res) => {
    res.json(robots);
});

// Intentionally vulnerable endpoint for demo
app.get('/api/export/:format', (req, res) => {
    const format = req.params.format;

    // Intentionally unsafe eval for demo purposes
    try {
        const exportFunction = eval(`(function() { return "Exporting data as ${format}"; })`);
        res.json({ message: exportFunction() });
    } catch (error) {
        res.status(400).json({ error: 'Invalid format' });
    }
});

app.listen(PORT, () => {
    console.log(`🤖 Globomantics Robot Fleet Manager running on http://localhost:${PORT}`);
    console.log('📊 Internal LOB Application - Authorized Personnel Only');
});
