const express = require("express")
const app = express()

app.get('/', (req, res) => {
    res.json({ message: 'Welcome! Try /api/hello or /api/status' });
});

app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello World!' })
});

app.get('/api/status', (req, res) => {
    res.json({ status: 'ok', time: new Date().toISOString() });
})

app.listen(3000, () => {
    console.log('Server running at http://localhost:3000')
});