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
import Loading from './pages/Loading/Loading';
import css from './index.scss';

function App() {
  const [freeModeSize, setFreeModeSize] = useState(0);
  const [selectedCrossword, setSelectedCrossword] = useState(null);
  const SERVER_URL =
    (process.env.NODE_ENV === 'production')
      ? process.env.SERVER_URL_PROD
      : process.env.SERVER_URL_DEV;

  useEffect(() => {
    Axios.get(`${SERVER_URL}/api/size/${freeModeSize}`)
      .then((res) => {
        if (res.data.length) {
          setSelectedCrossword(_.sample(res.data)._id);
        }
      })
      .catch((err) => console.error(err.toJSON()));
  }, [freeModeSize]);

  function RedirectedFreeMode() {
    window.location.href = `/puzzle/${selectedCrossword}`;
  }

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
            <Redirect to="/puzzle/63a7b79854254903cdd9410f" />
          </Route>
          <Route exact path="/puzzle/daily/maxi">
            <Redirect to="/puzzle/63a7b79854254903cdd9410f" />
          </Route>
          <Route exact path="/puzzle/free/redirect">
            {
              selectedCrossword
                ? <RedirectedFreeMode />
                : <Loading />
            }
          </Route>
          <Route path="*" component={NotFound} />
        </Switch>
      </main>
    </Router>
  );
}

export default App;
