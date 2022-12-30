import invert from 'lodash/invert';

export const across = 'across';
export const down = 'down';

export const directions = {
  A: across,
  D: down
};

export const abbreviatedDirections = invert(directions);
