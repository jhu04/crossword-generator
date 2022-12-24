import React from 'react';
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
        </h2>
      </div>
    </div>
  )
}