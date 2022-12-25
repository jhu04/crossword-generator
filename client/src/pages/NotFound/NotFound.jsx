import React from 'react';
import { Link } from 'react-router-dom';
import css from './NotFound.scss';

export default function NotFound() {
  return (
    <div className={css.bgText} txt='404'>
      <div>
        <h1>
          Oops!
        </h1>
        <h2>
          We couldn't find the page you were looking for.
          <br></br>
          (Unless you were looking for this.)
        </h2>
        <h2>
          <Link to="/">Go back home.</Link>
        </h2>
      </div>
    </div>
  )
}