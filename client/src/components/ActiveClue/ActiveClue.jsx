import React from 'react';
import { connect } from 'react-redux';
import classNames from 'classnames';

import { abbreviatedDirections } from 'constants/clue';

import css from './ActiveClue.scss';


class ActiveClue extends React.Component {
  render() {
    const { activeClue, abbreviatedDirection, obscured } = this.props;

    const containerClasses = classNames(css.activeClueContainer, {
      [css.activeClueContainer_obscured]: obscured || !activeClue
    });

    if (obscured || !activeClue) {
      return <div className={containerClasses} />
    }

    return (
      <div className={css.activeClueContainer}>
        <div className={css.clueNumber}>
          {`${activeClue.clueNum}${abbreviatedDirection}`}
        </div>
        <div className={css.clueValue}>
          {activeClue.value}
        </div>
      </div>
    )
  }
}

const mapStateToProps = (state, ownProps) => {
  const { activeCellNumber, activeDirection, cells, clues } = state.puzzle[ownProps.puzzleId] || {};

  if (['start', 'pause'].includes(state.modal.activeModal)) {
    return {
      obscured: true,
      activeClue: {},
    }
  }

  const activeCell = cells[activeCellNumber];
  const activeClue = clues[activeDirection][activeCell.cellClues[activeDirection]];
  const abbreviatedDirection = abbreviatedDirections[activeDirection];
  return {
    obscured: ['start', 'pause'].includes(state.modal.activeModal),
    abbreviatedDirection,
    activeClue,
  }
};

const connectedActiveClue = connect(mapStateToProps)(ActiveClue);

export {
  connectedActiveClue as ActiveClue,
};
