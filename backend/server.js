const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

// Check Referrals
app.post('/referrals', (req, res) => {
    const { userId, referrals } = req.body;
    if (referrals >= 10) {
        res.json({ boost: 3 });
    } else {
        res.json({ boost: 0 });
    }
});

// Check Stars
app.post('/stars', (req, res) => {
    const { userId, stars } = req.body;
    if (stars >= 20) {
        res.json({ points: 20 });
    } else {
        res.json({ points: 0 });
    }
});

// Leaderboard
app.get('/leaderboard', (req, res) => {
    res.json([
        { user: "User1", points: 50 },
        { user: "User2", points: 45 },
        { user: "User3", points: 40 }
    ]);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
