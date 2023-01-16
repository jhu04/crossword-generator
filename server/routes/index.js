const router = require('express').Router();
const model = require('../models/model');
const ObjectId = require('mongodb').ObjectId;

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

const getOne = async (res, query) => {
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
}

// TODO: clean code
router.get('/api/daily/:type/:date', async (req, res) => {
  if (['mini', 'maxi'].includes(req.params.type)) {
    const mini_sizes = [5];
    const maxi_sizes = [11, 13];
    const requirement = { $in: (req.params.type === 'mini' ? mini_sizes : maxi_sizes) };
    const query = {
      "puzzle_meta.publishType": "Daily",
      "puzzle_meta.dailyDate": req.params.date,
      "puzzle_meta.height": requirement,
      "puzzle_meta.width": requirement
    };
    getOne(res, query);
  } else {
    res.sendStatus(404);
  }
});

// TODO: clean code
router.get('/api/id/:id', async (req, res) => {
  if (ObjectId.isValid(req.params.id)) {
    const query = { _id: ObjectId(req.params.id) };
    getOne(res, query);
  } else {
    res.sendStatus(404);
  }
});

module.exports = router;