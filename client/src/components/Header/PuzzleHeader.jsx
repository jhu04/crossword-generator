import React from 'react';
import { connect } from 'react-redux';

import css from './PuzzleHeader.scss';

function TitleDiv({ title }) {
  return (
    <div className={css.title}>
      {title}
    </div>
  );
}

class PuzzleHeader extends React.Component {
  render() {
    let author = this.props.author;
    if (!author.toLowerCase().includes('by')) {
      author = `By ${author}`;
    }

    return (
      <div className={css.headerContainer}>
        <div>
          <div className={css.title}>
            <TitleDiv title={this.props.title} />
          </div>
          <div className={css.subtitle}>
            {author}
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = (state, ownProps) => {
  const { puzzleMeta } = state.puzzle[ownProps.puzzleId] || {};
  return {
    ...puzzleMeta
  }
};

const connectedHeader = connect(mapStateToProps)(PuzzleHeader);

export default connectedHeader;
