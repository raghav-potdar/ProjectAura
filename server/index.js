const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(bodyParser.json());

// simple sqlite DB in server/data
const dbPath = path.join(__dirname, 'data.sqlite');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
  db.run(
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      firstName TEXT,
      lastName TEXT,
      email TEXT UNIQUE,
      passwordHash TEXT,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )`
  );
});

app.post('/api/register', async (req, res) => {
  try {
    const { firstName, lastName, email, password } = req.body;
    if (!firstName || !lastName || !email || !password) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // check if email exists
    db.get('SELECT id FROM users WHERE email = ?', [email], async (err, row) => {
      if (err) return res.status(500).json({ error: 'Database error' });
      if (row) return res.status(409).json({ error: 'Email already registered' });

      const saltRounds = 10;
      const hash = await bcrypt.hash(password, saltRounds);

      db.run(
        'INSERT INTO users (firstName, lastName, email, passwordHash) VALUES (?, ?, ?, ?)',
        [firstName, lastName, email, hash],
        function (insertErr) {
          if (insertErr) return res.status(500).json({ error: 'Failed to register' });
          return res.json({ success: true, userId: this.lastID });
        }
      );
    });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
