const router = require('express').Router();
const model = require('../models/model');

router.get('/api/all', async (req, res) => {
  try {
    const puzzles = await model.find({});
    res.status(200).json(puzzles);
  } catch (err) {
    res.json(err);
  }
})

module.exports = router;