import React, { useState, useEffect } from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect
} from 'react-router-dom';
import Axios from 'axios';
import sample from 'lodash/sample';

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
          setSelectedCrossword(sample(res.data)._id);
        }
      })
      .catch((err) => console.error(err.toJSON()));
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
          <Route exact path="/puzzle/:puzzleId"
            render={(props) => (
              <Puzzle 
                setFreeModeSize={setFreeModeSize} 
                setSelectedCrossword={setSelectedCrossword}
                {...props}
              />
            )}
          />
          <Route exact path="/puzzle/daily/mini">
            <Redirect to="/puzzle/63a97dc765e5479584855cbf" />
          </Route>
          <Route exact path="/puzzle/daily/maxi">
            <Redirect to="/puzzle/63a97e2564ec9287d7ac5485" />
          </Route>
          <Route exact path="/puzzle/free/redirect">
            {
              selectedCrossword
                ? <Redirect to={`/puzzle/${selectedCrossword}`} />
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
