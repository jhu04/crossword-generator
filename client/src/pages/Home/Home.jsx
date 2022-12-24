import React from 'react';
import { Link } from 'react-router-dom';
import moment from 'moment';

import css from './Home.scss'
import calendarIcon from 'images/calendar-icon.png'
import birdsflyingIcon from 'images/birdsflying-icon.jpg'

function Home({setFreeModeSize}) {
  console.log(setFreeModeSize);
  function FreeModeButton(freeModeSize) {
    return (
      <Link to={`/puzzle/free/${freeModeSize}`}>
        <div className={css.button} onClick={() => {
          setFreeModeSize(freeModeSize);
        }}>
          {freeModeSize}x{freeModeSize}
        </div>
      </Link>
    );
  }

  return (
    <div className={css.wrapper}>
      <div className={css.panel}>
        <div className={css.content}>
          <img src={calendarIcon} className={css.mainMenuImage} />
          <h1>The Daily</h1>
          <h2>
            {moment().format('dddd') + ', ' + moment().format('LL')}
          </h2>
          <div className={css.buttonGroup}>
            <div className={css.buttonRow}>
              <Link to="/puzzle/daily/mini">
                <div className={css.button}>
                  Play Mini
                </div>
              </Link>
              <Link to="/puzzle/daily/maxi">
                <div className={css.button}>
                  Play Maxi
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <div className={css.panel}>
        <div className={css.content}>
          <img src={birdsflyingIcon} className={css.mainMenuImage} />
          <h1>Free Mode</h1>
          <div className={css.buttonGroup}>
            <div className={css.buttonRow}>
              {FreeModeButton(5)}
              {FreeModeButton(7)}
              {FreeModeButton(9)}
            </div>
            <div className={css.buttonRow}>
              {FreeModeButton(11)}
              {FreeModeButton(13)}
              {FreeModeButton(15)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
