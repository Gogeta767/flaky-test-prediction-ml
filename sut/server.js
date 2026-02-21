const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');

const configPath = path.join(__dirname, 'config', 'sut-config.json');
let config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const makeRand = require('./lib/rand');
const flakiness = require('./lib/flakiness');

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// dev: get/set config
app.get('/__config', (req,res) => res.json(config));
app.post('/__config', (req,res) => {
  if (!config.dev_mode) return res.status(403).send('forbidden');
  config = Object.assign(config, req.body || {});
  res.json({ ok: true, config });
});

// main API endpoint with injection
app.get('/api/data', async (req,res) => {
  const rng = makeRand((config.seed || Date.now()) + Math.floor(Math.random()*100000));
  const injected = await flakiness.maybeInject(req, res, config, rng);
  if (injected && injected.aborted) {
    // aborted — socket destroyed for realism; nothing else to do
    return;
  }
  // if maybeInject already sent failure (500), it returned injectedFailure true; otherwise send success
  if (injected.injectedFailure) {
    return res.status(500).json({ error: 'Injected failure' });
  }
  res.json({ ok: true, ts: Date.now(), injectedDelay: injected.injectedDelay });
});

// simple root
app.get('/', (req,res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

// API endpoint to serve test results
app.get('/api/test-results', (req, res) => {
  const testResultsPath = path.join(__dirname, '..', 'test-results', 'results.json');
  if (fs.existsSync(testResultsPath)) {
    const data = fs.readFileSync(testResultsPath, 'utf8');
    res.json(JSON.parse(data));
  } else {
    res.status(404).json({ error: 'Test results not found' });
  }
});

// API endpoint to serve orchestrator logs
app.get('/api/orchestrator-logs', (req, res) => {
  const logsDir = path.join(__dirname, '..', 'data', 'raw');
  const logs = fs.readdirSync(logsDir).map(file => {
    const content = fs.readFileSync(path.join(logsDir, file), 'utf8');
    return { file, content };
  });
  res.json(logs);
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log('SUT listening on', port));
