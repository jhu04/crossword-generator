import _ from 'lodash';

import { directions, across, down } from 'constants/clue';
import { CODE_ARROW_RIGHT, CODE_ARROW_LEFT, CODE_ARROW_DOWN, CODE_ARROW_UP } from 'constants/keys';
import { WORD, PUZZLE, INCOMPLETE, SQUARE } from 'constants/scopes';


export const getOtherDirection = direction => {
  return direction === across ? down : across;
};

const getStepSize = (direction, width, positive = true) => {
  const multiplier = positive ? 1 : -1;
  return multiplier * (direction === across ? 1 : width);
};

export const clueRange = (clue, direction, width) => {
  const stepSize = getStepSize(direction, width);
  return _.range(clue.clueStart, clue.clueEnd + stepSize, stepSize);
};

const getNextCellNumber = (start, end, cells, direction, width, moveForward = true) => {
  const stepSize = getStepSize(direction, width, moveForward);

  for (let i = start; i < end; i += stepSize) {
    const candidateCell = cells[i];
    if (!candidateCell.guess) {
      return i;
    }
  }
};

const getNextClue = (cellNumber, direction, cells, clues, width, defaultClues, forward) => {
  const activeCell = cells[cellNumber];
  const activeClue = clues[direction][activeCell.cellClues[direction]];
  const newClueNumber = forward ? activeClue.nextClueNumber : activeClue.previousClueNumber;

  let newClue = clues[direction][newClueNumber];
  let newDirection = direction;

  if (!newClue) {
    newDirection = getOtherDirection(newDirection);
    newClue = forward ? defaultClues[newDirection].first : defaultClues[newDirection].last;
  }

  return {
    newClue,
    newDirection
  };
};

export const getAnyRelated = (cellNumber, activeClue, clues, width) => {
  if (!activeClue.related) {
    return false;
  }

  for (let direction in activeClue.related) {
    if (!activeClue.related.hasOwnProperty(direction)) {
      continue;
    }

    const relatedClueNumbers = activeClue.related[direction];
    for (let i = 0; i < relatedClueNumbers.length; i++) {
      const relatedClueNumber = relatedClueNumbers[i];
      if (cellNumberInClue(cellNumber, clues[direction][relatedClueNumber], direction, width)) {
        return true;
      }
    }
  }

  return false;
}

export const cellNumberInClue = (cellNumber, clue, direction, width) => {
  const inRange = cellNumber <= clue.clueEnd && cellNumber >= clue.clueStart;
  if (direction === across) {
    return inRange;
  }
  return inRange && (cellNumber - clue.clueStart) % width === 0;
};

export const getGuessCellNumber = (activeCellNumber, activeDirection, cells, clues, width) => {
  const stepSize = getStepSize(activeDirection, width);
  const activeCell = cells[activeCellNumber];
  const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];

  if (activeCellNumber === activeClue.clueEnd) {
    return activeCellNumber;
  }

  if (activeCell.solved) {
    return activeCellNumber + stepSize;
  }

  const nextCellNumber = getNextCellNumber(activeCellNumber + stepSize, activeClue.clueEnd + 1, cells, activeDirection, width);
  if (nextCellNumber !== undefined) {
    return nextCellNumber;
  }

  const previousCellNumber = getNextCellNumber(activeClue.clueStart, activeCellNumber, cells, activeDirection, width);
  if (previousCellNumber !== undefined) {
    return previousCellNumber;
  }

  return activeCellNumber + stepSize;
};

export const getRemoveGuessCellNumber = (activeCellNumber, activeDirection, cells, clues, width) => {
  const stepSize = getStepSize(activeDirection, width, false);
  const activeCell = cells[activeCellNumber];
  const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];

  if (activeCell.guess && !activeCell.solved) {
    return activeCellNumber;
  }

  const previousCellNumber = activeCellNumber + stepSize;
  return previousCellNumber >= activeClue.clueStart ? previousCellNumber : activeClue.clueStart;
};

export const getMoveClueNumber = (activeCellNumber, activeDirection, cells, clues, width, defaultClues, forward) => {
  const numClues = _.keys(clues[across]).length + _.keys(clues[down]).length;

  // move to the next empty cell
  let { newClue, newDirection } = getNextClue(activeCellNumber, activeDirection, cells, clues, width, defaultClues, forward);
  for (let i = 0; i < numClues - 1; i += 1) {
    const newCellNumber = getNextCellNumber(newClue.clueStart, newClue.clueEnd + 1, cells, newDirection, width);

    if (newCellNumber !== undefined) {
      return {
        newDirection,
        newCellNumber
      }
    }

    ({ newClue, newDirection } = getNextClue(newClue.clueEnd, newDirection, cells, clues, width, defaultClues, forward));
  }

  // there are no empty cells, move to the next clue
  ({ newClue, newDirection } = getNextClue(activeCellNumber, activeDirection, cells, clues, width, defaultClues, forward));
  const newCellNumber = newClue.clueStart;

  return {
    newDirection: newDirection,
    newCellNumber: newCellNumber
  }
};

export const getMoveCellNumber = (activeCellNumber, activeDirection, cells, width, move) => {
  const lateralMovement = move === CODE_ARROW_LEFT || move === CODE_ARROW_RIGHT;
  const verticalMovement = move === CODE_ARROW_UP || move === CODE_ARROW_DOWN;

  if (activeDirection === across && verticalMovement) {
    return {
      newCellNumber: activeCellNumber,
      newDirection: down
    }
  } else if (activeDirection === down && lateralMovement) {
    return {
      newCellNumber: activeCellNumber,
      newDirection: across
    }
  }

  const positiveMovement = move === CODE_ARROW_DOWN || move === CODE_ARROW_RIGHT;
  const stepSize = getStepSize(activeDirection, width, positiveMovement);

  const numModWidth = activeCellNumber % width;
  const startNumber = activeDirection === across ? activeCellNumber - numModWidth : numModWidth;
  const endNumber = activeDirection === across ? startNumber + width - 1 : startNumber + width * width - width;

  for (let i = activeCellNumber + stepSize; i >= startNumber && i <= endNumber; i += stepSize) {
    if (cells[i].open) {
      return {
        newDirection: activeDirection,
        newCellNumber: i
      }
    }
  }

  return {
    newDirection: activeDirection,
    newCellNumber: activeCellNumber
  }
};

export const getClickClueNumber = (cells, clues, width, direction, clueNumber) => {
  const newClue = clues[direction][clueNumber];
  const nextEmptyCellNumber = getNextCellNumber(newClue.clueStart, newClue.clueEnd + 1, cells, direction, width);

  return nextEmptyCellNumber || newClue.clueStart;
};

const changeCells = (cellRange, cells, callback) => {
  let cellRangeIndex = 0;
  return cells.map((cell, cellIndex) => {
    if (cellRangeIndex >= cellRange.length) {
      return cell;
    }

    const cellToChange = cellRange[cellRangeIndex];

    if (cellIndex === cellToChange) {
      cellRangeIndex++;
      return {
        ...cell,
        ...callback(cell),
      }
    }

    return cell;
  });
};

const checkCells = (cell) => {
  return {
    cheated: cell.cheated || (cell.guess && cell.guess !== cell.answer),
    solved: cell.solved || (cell.guess === cell.answer),
  };
};

const revealCells = (cell) => {
  return {
    cheated: cell.cheated || cell.guess !== cell.answer,
    solved: true,
    revealed: true,
    guess: cell.answer,
  };
};

const clearCells = (cell) => {
  return {
    guess: cell.solved ? cell.guess : undefined,
  };
};

export const isPuzzleSolved = (cells) => {
  return cells.every(cell => !cell.open || cell.guess === cell.answer);
}

export const getCellChange = (callback, cells, clues, width, activeCellNumber, activeDirection, option) => {
  if (option === SQUARE) {
    return changeCells([activeCellNumber], cells, callback);

  } else if (option === WORD) {
    const activeCell = cells[activeCellNumber];
    const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];
    return changeCells(clueRange(activeClue, activeDirection, width), cells, callback);

  } else if (option === INCOMPLETE) {
    const activeCell = cells[activeCellNumber];
    const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];
    const cellRange = clueRange(activeClue, activeDirection, width).filter(cellNumber => {
      const otherDirection = getOtherDirection(activeDirection);
      const parallelCell = cells[cellNumber];
      const parallelClue = clues[otherDirection][parallelCell.cellClues[otherDirection]];
      return !clueRange(parallelClue, otherDirection, width).every(parallelCellNumber => {
        return cells[parallelCellNumber].guess;
      })
    });
    return changeCells(cellRange, cells, callback);

  } else if (option === PUZZLE) {
    return changeCells(_.range(cells.length), cells, callback);
  }
};

export const getRevealCells = (cells, clues, width, activeCellNumber, activeDirection, option) => {
  return getCellChange(revealCells, cells, clues, width, activeCellNumber, activeDirection, option);
};


export const getCheckCells = (cells, clues, width, activeCellNumber, activeDirection, option) => {
  return getCellChange(checkCells, cells, clues, width, activeCellNumber, activeDirection, option);
};

export const getClearCells = (cells, clues, width, activeCellNumber, activeDirection, option) => {
  return getCellChange(clearCells, cells, clues, width, activeCellNumber, activeDirection, option)
};

export const initializePuzzle = (puzzleObject) => {
  const { layout, answers, clues } = puzzleObject.puzzle_data;
  const { width } = puzzleObject.puzzle_meta;
  let availableCells = 0;
  const cells = layout.map((cell, index) => {
    if (cell) {
      availableCells += 1;
    }

    return {
      open: !!cell,
      answer: answers[index],
      cellClues: {},
    }
  });

  const cluesByNumber = {
    [across]: {},
    [down]: {}
  };

  const defaultClues = {
    [across]: {},
    [down]: {}
  };

  _.each(clues, (clueList, directionLetter) => {
    let previousClue;
    const direction = directions[directionLetter];

    _.each(clueList, clue => {
      const cell = cells[clue.clueStart];
      clue.clueNumber = clue.clueNum;
      cell.clueStart = clue.clueNumber;

      if (previousClue) {
        previousClue.nextClueNumber = clue.clueNumber;
        clue.previousClueNumber = previousClue.clueNumber;
      }

      cluesByNumber[direction][clue.clueNumber] = clue;

      clueRange(clue, direction, width).forEach(clueNumber => {
        cells[clueNumber].cellClues[direction] = clue.clueNumber;
      });

      previousClue = clue;
    });
    defaultClues[direction] = {
      first: clueList[0],
      last: clueList[clueList.length - 1]
    }
  });

  return {
    availableCells,
    cells,
    width,
    defaultClues,
    clues: cluesByNumber,
    activeCellNumber: 0,
    activeDirection: across,
    puzzleMeta: puzzleObject.puzzle_meta,
    timer: 0,
    raw: puzzleObject,
    filledCells: 0,
  };
};
