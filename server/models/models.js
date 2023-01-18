const mongoose = require('mongoose');
const ObjectId = require('mongodb').ObjectId;

const puzzleSchema = new mongoose.Schema({
  "_id": ObjectId,
  "puzzle_meta": {
    "height": Number,
    "width": Number,
    "publishType": String,
    "dailyDate": String
  }
}, { collection: process.env.PUZZLE_COLLECTION });

const idSchema = new mongoose.Schema({
  "_id": String,
  "puzzle_id_list": Array
}, { collection: process.env.ID_COLLECTION });

const puzzleModel = mongoose.model('puzzle', puzzleSchema);
const idModel = mongoose.model('id', idSchema)

module.exports = { puzzleModel, idModel };