import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Link
} from 'react-router-dom';

import Header from 'components/Header/Header';
import Home from 'pages/Home/Home';
import Puzzle from 'pages/Puzzle/Puzzle';
import NotFound from 'pages/NotFound/NotFound';
import css from './index.scss';

function App() {
  return (
    <Router>
      <main>
        <Header />
        <Switch>
          <Route exact path="/" component={Home} />
          <Route exact path="/puzzle/:puzzleName" component={Puzzle} />
          <Route path="*" component={NotFound} />
        </Switch>
      </main>
    </Router>
  );
}

export default App;
