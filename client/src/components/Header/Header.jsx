import React from 'react';
import logo from 'assets/crossify.png'
import { GithubIcon } from 'components/Icons/GithubIcon';

import css from './Header.scss';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <div className={css.headerContainer}>
      <Link to="/">
        <img src={logo} alt="Logo" />
      </Link>
      <a href="https://github.com/jhu04/crossword-generator" target="_blank">
        <GithubIcon />
      </a>
    </div>
  );
}