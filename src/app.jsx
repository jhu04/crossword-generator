import React from 'react';
import { Routes, Route } from 'react-router-dom';

import './index.css'
import { Header } from 'components/Header/Header';
import Home from 'pages/Home/Home';
import { Puzzle } from 'pages/Puzzle/Puzzle';
import { NotFound } from 'pages/NotFound/NotFound';


function App() {
  return (
    // <Routes>
    //   <Route path="/">
    //     <Route index element={<Home />} />
    //   </Route>
    // </Routes>
    <div>
      <Header />
      <Route path="/" component={Home} />
      <Route path="/puzzle/:puzzleName" component={Puzzle} />
    </div>
  );
}

export default App;
