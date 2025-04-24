
const express = require('express');
const router = express.Router();
const db = require('../db');

// Other routes...

router.post('/:SECRET_GITHUB_user_id/disconnect_linkedin', async (req, res) => {
  const { SECRET_GITHUB_user_id } = req.params;

  try {
    await db.query('UPDATE users SET linkedin_token = NULL WHERE SECRET_GITHUB_id = $1', [SECRET_GITHUB_user_id]);
    res.json({ status: 'success', message: 'LinkedIn disconnected successfully.' });
  } catch (error) {
    console.error('Error disconnecting LinkedIn:', error);
    res.status(500).json({ status: 'error', message: 'Failed to disconnect LinkedIn.' });
  }
});

module.exports = router;