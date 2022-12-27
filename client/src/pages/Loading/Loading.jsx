import React from 'react';
import TypeWriter from 'typewriter-effect';
import css from './Loading.scss';

export default function Loading() {
  return (
    <div className={css.wrapper}>
      <h1>
        <TypeWriter
          options={{ 
            strings: ['Loading...'],
            autoStart: true,
            loop: true
          }}
        />
      </h1>
    </div>
  )
}