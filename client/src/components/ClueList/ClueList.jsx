import React from 'react';
import map from 'lodash/map';
import { connect } from 'react-redux';

import { Clue } from 'components/Clue/Clue';


import css from './ClueList.scss';


class ClueList extends React.Component {
  constructor(props) {
    super(props);
    this.clues = {};
  }

  componentDidUpdate() {
    if (this.list && this.props.activeClueNumber) {
      this.list.scrollTop = this.clues[this.props.activeClueNumber].offsetTop - this.list.offsetTop;
    }
  }

  render() {
    const { direction, clues, puzzleId } = this.props;

    return (
      <div className={css.clueListContainer}>
        <div className={css.directionName}>
          {direction}
        </div>
        <ol className={css.clueList} ref={list => { this.list = list }}>
          {map(clues, (clue, clueNumberString) => {
            const clueNumber = Number(clueNumberString);
            return (
              <Clue
                key={clueNumber}
                puzzleId={puzzleId}
                clueNumber={clueNumber}
                direction={direction}
                clueRef={clue => { this.clues[clueNumber] = clue }}
              />
            )
          })}
        </ol>
      </div>
    )
  }
}

const mapStateToProps = (state, ownProps) => {
  const { clues, activeCellNumber, cells } = state.puzzle[ownProps.puzzleId] || {};
  const { direction } = ownProps;

  // console.log(clues, activeCellNumber, cells, direction);

  if (state.modal.activeModal === 'start') {
    return {
      clues: clues[direction]
    };
  }

  const activeCell = cells[activeCellNumber];
  return {
    activeClueNumber: clues[direction][activeCell.cellClues[direction]].clueNumber,
    clues: clues[direction],
  }
};

const connectedClueList = connect(mapStateToProps)(ClueList);

export {
  connectedClueList as ClueList,
};
