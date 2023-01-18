const router = require('express').Router();
const { puzzleModel, idModel } = require('../models/models');
const ObjectId = require('mongodb').ObjectId;

const getOne = async (model, res, query) => {
  try {
    const documents = await model.findOne(query);
    if (documents) {
      res.status(200).json(documents);
    } else {
      res.sendStatus(404);
    }
  } catch (err) {
    res.json(err);
  }
}

router.get('/api/size/:size', async (req, res) => {
  const query = { _id: `size_${req.params.size}` };
  getOne(idModel, res, query);
});

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
    getOne(puzzleModel, res, query);
  } else {
    res.sendStatus(404);
  }
});

router.get('/api/id/:id', async (req, res) => {
  if (ObjectId.isValid(req.params.id)) {
    const query = { _id: ObjectId(req.params.id) };
    getOne(puzzleModel, res, query);
  } else {
    res.sendStatus(404);
  }
});

module.exports = router;