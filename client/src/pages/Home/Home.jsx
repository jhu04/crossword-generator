import React from 'react';
import moment from 'moment';

import css from './Home.scss'
import calendarIcon from 'images/calendar-icon.png'
import birdsflyingIcon from 'images/birdsflying-icon.jpg'

function Home() {
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
              <a href="/puzzle/mini">
                <div className={css.button}>
                  Play Mini
                </div>
              </a>
              <a href="/puzzle/maxi">
                <div className={css.button}>
                  Play Maxi
                </div>
              </a>
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
              <div className={css.button}>
                5x5
              </div>
              <div className={css.button}>
                7x7
              </div>
              <div className={css.button}>
                9x9
              </div>
            </div>
            <div className={css.buttonRow}>
              <div className={css.button}>
                11x11
              </div>
              <div className={css.button}>
                13x13
              </div>
              <div className={css.button}>
                15x15
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
