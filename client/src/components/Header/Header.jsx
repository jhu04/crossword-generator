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
      <Link to="/about" className={css.nav_link}>
        About
      </Link>
    </div>
  );
}