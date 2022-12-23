import React from 'react';
import logo from 'images/nytimes_games.jpg'
import { GithubIcon } from 'components/Icons/GithubIcon';

import css from './Header.scss';

export default function Header() {
  return (
    <div className={css.headerContainer}>
      <a href="/">
        <img src={logo} alt="Logo" />
      </a>
      <a href="https://github.com/jhu04/crossword-generator" target="_blank">
        <GithubIcon />
      </a>
    </div>
  );
}