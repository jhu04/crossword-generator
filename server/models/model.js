const mongoose = require('mongoose');
const schema = new mongoose.Schema({}, { collection: process.env.COLLECTION });

module.exports = mongoose.model('', schema);