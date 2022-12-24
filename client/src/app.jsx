import React, { useState, useEffect } from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from 'react-router-dom';
import Axios from 'axios';

import Header from 'components/Header/Header';
import Home from 'pages/Home/Home';
import Puzzle from 'pages/Puzzle/Puzzle';
import NotFound from 'pages/NotFound/NotFound';
import css from './index.scss';

function App() {
  const [freeModeSize, setFreeModeSize] = useState(0);
  const [crosswordsBySize, setCrosswordsBySize] = useState([]);
  const [selectedCrossword, setSelectedCrossword] = useState('');
  const SERVER_URL =
    (process.env.NODE_ENV === 'production')
      ? process.env.SERVER_URL_PROD
      : process.env.SERVER_URL_DEV;

  // TODO: buggy
  useEffect(() => {
    console.log(`${SERVER_URL}/api/size/${freeModeSize}`);
    Axios.get(`${SERVER_URL}/api/size/${freeModeSize}`)
      .then((res) => res.data)
      .then(setCrosswordsBySize)
      .catch((err) => console.error(err.toJSON()));
    console.log(crosswordsBySize);
    if (crosswordsBySize.length) {
      setSelectedCrossword(_.sample(crosswordsBySize)._id);
    }
  }, [freeModeSize]);

  // TODO: update mini/, maxi/
  return (
    <Router>
      <main>
        <Header />
        <Switch>
          <Route exact path="/">
            <Home setFreeModeSize={setFreeModeSize} />
          </Route>
          <Route exact path="/puzzle/:puzzleId" component={Puzzle} />
          <Route exact path="/puzzle/daily/mini">
            <Redirect to="/puzzle/63a169a66f69631f0c099ab9" />
          </Route>
          <Route exact path="/puzzle/daily/maxi">
            <Redirect to="/puzzle/63a169a66f69631f0c099ab9" />
          </Route>
          <Route exact path="puzzle/free/:size">
            <Redirect to={`/puzzle/${selectedCrossword}`} />
          </Route>
          <Route path="*" component={NotFound} />
        </Switch>
      </main>
    </Router>
  );
}

export default App;
