const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv-expand').expand(require('dotenv').config()).parsed;

const app = express();
app.use(express.json());
app.use(cors());
const router = require('./routes');

const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.ATLAS_URI, { autoIndex: false })
  .then(() => console.log('Database connected'))
  .catch(err => console.log(err));

app.use('/', router);
app.listen(PORT, () => console.log('Server connected'));
