import React from 'react';
import classNames from 'classnames';
import { connect } from 'react-redux';

import { cellNumberInClue, getAnyRelated } from 'utils/puzzle';
import { cellClick } from 'reducers/puzzle';

import css from './Cell.scss';


class Cell extends React.Component {
  render() {
    const { open, cheated, solved, revealed, active, selected, related, obscured } = this.props;
    const closed = !open;

    const squareClasses = classNames(css.cell, {
      [css.cell_closed]: closed,
      [css.cell_obscured]: obscured && this.props.guess,
      [css.cell_selected]: selected,
      [css.cell_active]: active,
      [css.cell_related]: related,
    });

    if (closed) {
      return <div className={squareClasses} />;
    }

    const cheatClasses = classNames({
      [css.cheat]: cheated,
      [css.revealed]: revealed,
    });

    const tatterClasses = classNames({
      [css.tatter]: revealed
    });

    const guessClasses = classNames(css.guess, {
      [css.solved]: solved,
    });


    return (
      <div className={squareClasses} onClick={this.props.cellClick}>
        <div className={cheatClasses}>
          <div className={tatterClasses} />
        </div>
        <div className={css.number}>
          {this.props.clueStart}
        </div>
        <div className={guessClasses}>
          {this.props.guess}
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  const { cells, activeDirection, clues, activeCellNumber, width } = state.puzzle[ownProps.puzzleId] || {};
  if (state.modal.activeModal === 'start') {
    return {
      ...cells[ownProps.cellNumber],
    };
  }

  const activeCell = cells[activeCellNumber];
  const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];

  return {
    active: activeCellNumber === ownProps.cellNumber,
    selected: cellNumberInClue(ownProps.cellNumber, activeClue, activeDirection, width),
    related: getAnyRelated(ownProps.cellNumber, activeClue, clues, width),
    obscured: state.modal.activeModal === 'pause',
    ...cells[ownProps.cellNumber],
  }
};

const mapDispatchToProps = dispatch => {
  return {
    cellClick: (puzzleId, cellNumber) => () => dispatch(cellClick(puzzleId, cellNumber)),
  }
};

const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    cellClick: dispatchProps.cellClick(ownProps.puzzleId, ownProps.cellNumber),
  }
}

const connectedCell = connect(mapStateToProps, mapDispatchToProps, mergeProps)(Cell);

export {
  connectedCell as Cell,
}
