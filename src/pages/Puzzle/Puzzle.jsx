import React from 'react';
import { connect } from 'react-redux';

import { Grid } from 'components/Grid/Grid';
import { ClueList } from 'components/ClueList/ClueList';
import { ActiveClue } from 'components/ActiveClue/ActiveClue';

import { across, down } from 'constants/clue';
import {
  CODE_ARROW_DOWN,
  CODE_ARROW_LEFT,
  CODE_BACKSPACE,
  CODE_LETTER_A,
  CODE_LETTER_Z,
  CODE_TAB
} from 'constants/keys';
import { fetchPuzzle, guessCell } from 'reducers/puzzle';
import { STATUS_404 } from 'utils/fetcher';

import css from './Puzzle.scss';


class Puzzle extends React.Component {
  componentWillMount() {
    this.props.fetchPuzzle();
    document.addEventListener("keydown", this.handleKeyDown);
  }

  handleKeyDown = (evt) => {
    if (evt.ctrlKey || evt.altKey || evt.metaKey) {
      return
    }

    const {keyCode} = evt;

    // if (keyCode >= CODE_ARROW_LEFT && keyCode <= CODE_ARROW_DOWN) {
    //   evt.preventDefault();
    //   this.props.arrowKeys(evt.code);
    // }
    //
    // else if (keyCode == CODE_TAB) {
    //   evt.preventDefault();
    //
    //   if (evt.shiftKey) {
    //     this.props.tabKeys(PREV);
    //   } else {
    //     this.props.tabKeys(NEXT);
    //   }
    // }

    if (keyCode >= CODE_LETTER_A && keyCode <= CODE_LETTER_Z) {
      this.props.guessCell(evt.key);
    }

    // else if (keyCode == CODE_BACKSPACE) {
    //   evt.preventDefault();
    //   this.props.backspaceKey();
    // }
  }

  render() {
    const { puzzle } = this.props;
    if (!puzzle) {
      return <div>loading...</div>;
    }

    if (puzzle.data === STATUS_404) {
      return <div>not found...</div>;
    }

    const { clues, activeDirection, activeClueNumber } = puzzle;
    const activeClue = clues[activeDirection][activeClueNumber];

    return (
      <div className={css.puzzleContainer}>
        <div className={css.headerContainer}>
          header
        </div>
        <div className={css.gameContainer}>
          <div className={css.gridContainer}>
            <ActiveClue clue={activeClue} direction={activeDirection} />
            <Grid {...puzzle} />
          </div>
          <div className={css.cluesContainer}>
            <ClueList
              clues={clues.across}
              directionName={across}
              activeDirection={activeDirection}
              activeClueNumber={activeClueNumber}
            />
            <ClueList
              clues={clues.down}
              directionName={down}
              activeDirection={activeDirection}
              activeClueNumber={activeClueNumber}
            />
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  puzzle: state.puzzle[ownProps.match.params.puzzleName],
});

const mapDispatchToProps = dispatch => ({
  fetchPuzzle: puzzleName => () => dispatch(fetchPuzzle(puzzleName)),
  guessCell: puzzleName => guess => dispatch(guessCell(puzzleName, guess))
});

const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { puzzleName } = ownProps.match.params;
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    guessCell: dispatchProps.guessCell(puzzleName),
    fetchPuzzle: dispatchProps.fetchPuzzle(puzzleName)
  }
};

const connectedPuzzle = connect(mapStateToProps, mapDispatchToProps, mergeProps)(Puzzle);

export {
  connectedPuzzle as Puzzle,
};
