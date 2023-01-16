import React from 'react';
import TypeWriter from 'typewriter-effect';
import css from './About.scss';

export default function () {
  return (
    <div className={css.wrapper}>
      <div className={css.content}>
        <h1>About</h1>
        <p>
          Crossify is (probably) the largest publicly available computer-generated
          collection of American-style "dense" crosswords — 25,000 and counting! 
          Our grids satisfy the usual rules, notably:
          <ul>
            <li>
              All-over interlock: No part of the grid is completely cut off by 
              black squares, and each square is contained in exactly two clues.
            </li>
            <li>
              At most one-sixth of squares in the grid are black.
            </li>
          </ul>
          We are open-source! Check out our <a 
            href="https://github.com/prestonfu/crossify"
            target="_blank"
            className={css.textLink}>
            repo
          </a> to learn more, or report bugs through Github issues.
        </p>
      </div>
    </div>
  )
}