import React from 'react';
import moment from 'moment';

import css from './Home.scss'
import { Page } from 'components/Page/Page';
import calendarIcon from 'images/calendar-icon.png'
import birdsflyingIcon from 'images/birdsflying-icon.jpg'

function Home() {
  return (
    <div className={css.outerWrapper}>
      <main className={css.stretcher}>
        <div className={css.innerWrapper}>
          <div className={css.box}>
            <img src={calendarIcon} className={css.mainMenuImage} />
            <h1>The Daily</h1>
            <h2>
              {moment().format('dddd') + ', ' + moment().format('LL')}
            </h2>
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
          <div className={css.box}>
            <img src={birdsflyingIcon} className={css.mainMenuImage} />
            <h1>Free Mode</h1>
            <div className={css.buttonRow}>
              <div className={css.button}>
                Play
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    // <div class="flex flex-col min-h-screen max-h-screen overflow-hidden p-6 bg-white">
    //   <main class="flex flex-grow overflow-hidden">
    //     <div class="flex w-full">
    //       <div class="w-1/2 p-4 align-middle text-center border border-gray-200">
    //         <p>Left column</p>
    //       </div>
    //       <div class="ml-6 flex flex-col w-1/2 p-4 overflow-hidden text-center border border-gray-200">
    //         <p>Right column</p>
    //       </div>
    //     </div>
    //   </main>
    // </div>
    // <div class="grid grid-cols-2">
    //   <div class="p-6 h-96">
    //     <img class="w-96" src={calendarIcon} />
    //     <h1>
    //       The Daily
    //     </h1>
    //   </div>
    //   <div class="p-6 h-96">
    //     <img class="w-96" src={birdsflyingIcon} />
    //     <h1>
    //       Free Mode
    //     </h1>
    //     <h2>
    //       subtitle
    //     </h2>
    //   </div>
    // </div>
  );
}

export default Home;
