import React from 'react';
import { Link } from 'react-router-dom';

import css from './Home.scss'
import calendarIcon from 'assets/calendar.svg'
import birdsflyingIcon from 'assets/birdsflying.svg'

function Home({ setFreeModeSize }) {
  const dayOfWeek = new Date().toLocaleString('en', { weekday: 'long', timeZone: 'UTC' });
  const day = new Date().getUTCDate();
  const month = new Date().toLocaleString('en', { month: 'long', timeZone: 'UTC' });
  const year = new Date().getUTCFullYear();

  function FreeModeButton(freeModeSize) {
    return (
      <Link to={'/puzzle/free/redirect'}>
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
          <h1 className={css.cardTitle}>The Daily</h1>
          <h2 className={css.date}>{dayOfWeek}, {month} {day}, {year}</h2>
          <div className={css.buttonGroup}>
            <div className={css.buttonRow}>
              <Link to="/puzzle/daily/mini">
                <div className={css.button}>
                  Mini
                </div>
              </Link>
              <Link to="/puzzle/daily/maxi">
                <div className={css.button}>
                  Maxi
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <div className={css.panel}>
        <div className={css.content}>
          <img src={birdsflyingIcon} className={css.mainMenuImage} />
          <h1 className={css.cardTitle}>Free Mode</h1>
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
