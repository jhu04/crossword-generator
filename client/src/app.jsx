import React, { useState, useEffect } from 'react';
import {
  HashRouter as Router,
  Switch,
  Route,
  Redirect
} from 'react-router-dom';
import Axios from 'axios';
import sample from 'lodash/sample';

import Header from 'components/Header/Header';
import About from './pages/About/About';
import Home from 'pages/Home/Home';
import Puzzle from 'pages/Puzzle/Puzzle';
import NotFound from 'pages/NotFound/NotFound';
import Loading from './pages/Loading/Loading';
import css from './index.scss';

function App() {
  const [freeModeSize, setFreeModeSize] = useState(0);
  const [dailyMini, setDailyMini] = useState(null);
  const [dailyMaxi, setDailyMaxi] = useState(null);
  const [selectedFreeModeCrossword, setSelectedFreeModeCrossword] = useState(null);

  const day = String(new Date().getUTCDate()).padStart(2, '0');
  const month = String(new Date().getUTCMonth() + 1).padStart(2, '0');
  const year = new Date().getUTCFullYear();
  const today = `${year}-${month}-${day}`

  const SERVER_URL =
    (process.env.NODE_ENV === 'production')
      ? 'https://crossify-server.vercel.app'
      : 'http://localhost:5001'; // TODO: fix env variables in deployment

  useEffect(() => {
    Axios.get(`${SERVER_URL}/api/daily/mini/${today}`)
      .then((res) => setDailyMini(res.data._id))
      .catch((err) => console.error(err.toJSON()));
    Axios.get(`${SERVER_URL}/api/daily/maxi/${today}`)
      .then((res) => setDailyMaxi(res.data._id))
      .catch((err) => console.error(err.toJSON()));
  }, []);

  useEffect(() => {
    Axios.get(`${SERVER_URL}/api/size/${freeModeSize}`)
      .then((res) => {
        if (res.data.length) {
          setSelectedFreeModeCrossword(sample(res.data));
          console.log(res.data);
        }
      })
      .catch((err) => console.error(err.toJSON()));
  }, [freeModeSize]);

  return (
    <Router>
      <main>
        <Header />
        <Switch>
          <Route exact path="/">
            <Home setFreeModeSize={setFreeModeSize} />
          </Route>
          <Route exact path="/about" component={About} />
          <Route exact path="/:puzzleId"
            render={(props) => (
              <Puzzle
                setFreeModeSize={setFreeModeSize}
                setSelectedFreeModeCrossword={setSelectedFreeModeCrossword}
                {...props}
              />
            )}
          />
          <Route exact path="/daily/mini">
            {
              dailyMini
                ? <Redirect to={`/${dailyMini}`} />
                : <Loading />
            }
          </Route>
          <Route exact path="/daily/maxi">
            {
              dailyMaxi
                ? <Redirect to={`/${dailyMaxi}`} />
                : <Loading />
            }
          </Route>
          <Route exact path="/free/redirect">
            {
              selectedFreeModeCrossword
                ? <Redirect to={`/${selectedFreeModeCrossword}`} />
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
