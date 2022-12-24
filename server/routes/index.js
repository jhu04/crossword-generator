const router = require('express').Router();
const model = require('../models/model');
const ObjectId = require('mongodb').ObjectId;

router.get('/api/all', async (req, res) => {
  const query = {};
  try {
    const puzzles = await model.find(query);
    res.status(200).json(puzzles);
  } catch (err) {
    res.json(err);
  }
});

router.get('/api/size/:size', async (req, res) => {
  const size = parseInt(req.params.size);
  const query = { "puzzle_meta.height": size, "puzzle_meta.width": size };
  try {
    const puzzles = await model.find(query);
    res.status(200).json(puzzles);
  } catch (err) {
    res.json(err);
  }
});

// TODO: clean code
router.get('/api/id/:id', async (req, res) => {
  if (ObjectId.isValid(req.params.id)) {
    const query = { _id: ObjectId(req.params.id) };
    try {
      const puzzles = await model.findOne(query);
      if (puzzles) {
        res.status(200).json(puzzles);
      } else {
        res.sendStatus(404);
      }
    } catch (err) {
      res.json(err);
    }
  } else { res.sendStatus(404); }
});



module.exports = router;