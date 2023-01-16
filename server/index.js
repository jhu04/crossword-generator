const express = require('express');
const mongoose = require('mongoose');
mongoose.set('strictQuery', true);
const cors = require('cors');
require('dotenv-expand').expand(require('dotenv').config()).parsed;

const app = express();
app.use(express.json());
app.use(cors());
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});
const router = require('./routes');

const PORT = process.env.PORT || 5001;

mongoose
  .connect(process.env.ATLAS_URI, { autoIndex: false })
  .then(() => console.log('Database connected'))
  .catch(err => console.log(err));

app.use('/', router);
app.listen(PORT, () => console.log('Server connected'));
