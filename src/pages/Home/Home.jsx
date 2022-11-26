import React from 'react';
import moment from 'moment';

import css from './home.scss'
import { Page } from 'components/Page/Page';
import calendarIcon from 'images/calendar-icon.png'
import birdsflyingIcon from 'images/birdsflying-icon.jpg'

export class Home extends React.Component {
  render() {
    return (
      <p>
        Homepage
      </p>
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
      //     <h2>
      //       {moment().format('dddd') + ' ' + moment().format('LL')}
      //     </h2>
      //     <button>
      //       Mini
      //     </button>
      //     <button>
      //       Maxi
      //     </button>
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
}
