import React from 'react';
import { connect } from 'react-redux';

import { Grid } from 'components/Grid/Grid';
import { ClueList } from 'components/ClueList/ClueList';
import { ActiveClue } from 'components/ActiveClue/ActiveClue';
import { Toolbar } from 'components/Toolbar/Toolbar';
import { Modal } from 'components/Modal/Modal';
import PuzzleHeader from 'components/Header/PuzzleHeader';
import Loading from 'pages/Loading/Loading';
import NotFound from 'pages/NotFound/NotFound'

import { across, down } from 'constants/clue';
import {
  CODE_ARROW_DOWN,
  CODE_ARROW_LEFT,
  CODE_BACKSPACE,
  CODE_LETTER_A,
  CODE_LETTER_Z,
  CODE_TAB,
  CODE_ENTER,
} from 'constants/keys';
import {
  fetchPuzzle,
  guessCell,
  moveActiveCell,
  moveActiveClue,
  removeGuess,
  startTimer,
  stopTimer,
} from 'reducers/puzzle';
import { openModal, closeModal } from 'reducers/modal';
import { STATUS_404 } from 'utils/fetcher';

import css from './Puzzle.scss';


class Puzzle extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      interval: null,
    }
  }

  componentDidMount() {
    this.props.fetchPuzzle();
    this.props.openModal('start');
    document.addEventListener("keydown", this.handleKeyDown);
  }

  componentWillUnmount() {
    clearInterval(this.state.interval);
    document.removeEventListener("keydown", this.handleKeyDown);
  }

  componentDidUpdate(nextProps) {
    if (nextProps.solved && !this.props.solved) {
      this.pausePuzzle();
      this.props.openModal('done');
    } else if (nextProps.filled && !this.props.filled) {
      this.pausePuzzle();
      this.props.openModal('incorrect');
    }
  }

  openPauseModal = () => {
    this.pausePuzzle();
    this.props.openModal('pause');
  }

  pausePuzzle = () => {
    this.props.stopTimer();
  }

  startPuzzle = () => {
    this.props.startTimer();
    this.props.closeModal();
  }

  finishPuzzle = () => {
    this.props.closeModal();
  }

  resetPuzzle = () => {
    this.props.startTimer();
  }

  handleKeyDown = (evt) => {
    if (evt.ctrlKey || evt.altKey || evt.metaKey) {
      return
    }

    const {keyCode} = evt;

    if (this.props.activeModal) {
      return;
    }

    if (keyCode >= CODE_ARROW_LEFT && keyCode <= CODE_ARROW_DOWN) {
      evt.preventDefault();
      this.props.moveActiveCell(evt.keyCode);
    }

    else if (keyCode === CODE_TAB || keyCode === CODE_ENTER) {
      evt.preventDefault();

      if (evt.shiftKey) {
        this.props.moveActiveClue(false);
      } else {
        this.props.moveActiveClue(true);
      }
    }

    else if (keyCode >= CODE_LETTER_A && keyCode <= CODE_LETTER_Z) {
      this.props.guessCell(evt.key);
    }

    else if (keyCode === CODE_BACKSPACE) {
      evt.preventDefault();
      this.props.removeGuess();
    }
  };

  render() {
    const { puzzleIs404, puzzleIsLoading } = this.props;
    if (puzzleIsLoading) {
      return <Loading />;
    }

    if (puzzleIs404) {
      return <NotFound />;
    }

    const { puzzleId } = this.props.match.params;

    return (
      <div className={css.app}>
        <div className={css.puzzleContainer}>
          <PuzzleHeader puzzleId={puzzleId} />
          <div className={css.gameContainer}>
            <Toolbar puzzleId={puzzleId} openPauseModal={this.openPauseModal} resetPuzzle={this.resetPuzzle} />
            <div className={css.playArea}>
              <div className={css.gridContainer}>
                <ActiveClue puzzleId={puzzleId} />
                <Grid puzzleId={puzzleId} />
              </div>
              <div className={css.cluesContainer}>
                <ClueList direction={across} puzzleId={puzzleId} />
                <ClueList direction={down} puzzleId={puzzleId} />
              </div>
            </div>
          </div>
        </div>
        <Modal type="start" activeModal={this.props.activeModal} closeModal={this.startPuzzle} />
        <Modal type="pause" activeModal={this.props.activeModal} closeModal={this.startPuzzle} overlayClick />
        <Modal type="done" activeModal={this.props.activeModal} closeModal={this.finishPuzzle} puzzleId={puzzleId} overlayClick />
        <Modal type="incorrect" activeModal={this.props.activeModal} closeModal={this.startPuzzle} overlayClick />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  const puzzle =  state.puzzle[ownProps.match.params.puzzleId];
  const puzzleIsLoading = !puzzle;
  const puzzleIs404 = puzzle === STATUS_404;
  return {
    puzzleIs404,
    puzzleIsLoading,
    solved: puzzle && puzzle.solved,
    filled: puzzle && puzzle.availableCells === puzzle.filledCells,
    activeModal: state.modal.activeModal,
  }
};

const mapDispatchToProps = dispatch => ({
  fetchPuzzle: puzzleId => () => dispatch(fetchPuzzle(puzzleId)),
  guessCell: puzzleId => guess => dispatch(guessCell(puzzleId, guess)),
  moveActiveCell: puzzleId => move => dispatch(moveActiveCell(puzzleId, move)),
  moveActiveClue: puzzleId => move => dispatch(moveActiveClue(puzzleId, move)),
  removeGuess: puzzleId => () => dispatch(removeGuess(puzzleId)),
  openModal: modalName => dispatch(openModal(modalName)),
  closeModal: () => dispatch(closeModal()),
  startTimer: puzzleId => () => dispatch(startTimer(puzzleId)),
  stopTimer: puzzleId => () => dispatch(stopTimer(puzzleId)),
});

const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { puzzleId } = ownProps.match.params;
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    guessCell: dispatchProps.guessCell(puzzleId),
    fetchPuzzle: dispatchProps.fetchPuzzle(puzzleId),
    moveActiveCell: dispatchProps.moveActiveCell(puzzleId),
    moveActiveClue: dispatchProps.moveActiveClue(puzzleId),
    removeGuess: dispatchProps.removeGuess(puzzleId),
    startTimer: dispatchProps.startTimer(puzzleId),
    stopTimer: dispatchProps.stopTimer(puzzleId),
  }
};

const connectedPuzzle = connect(mapStateToProps, mapDispatchToProps, mergeProps)(Puzzle);

export default connectedPuzzle;
