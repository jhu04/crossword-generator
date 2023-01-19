const mongoose = require('mongoose');
const ObjectId = require('mongodb').ObjectId;

const schema = new mongoose.Schema({
  "_id": ObjectId,
  "puzzle_meta": {
    "height": Number,
    "width": Number,
    "publishType": String,
    "dailyDate": String
  }
}, { collection: process.env.COLLECTION });

module.exports = mongoose.model('', schema);