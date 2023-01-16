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

    const date = this.props.publishType === 'Daily'
                   ? this.props.dailyDate
                   : this.props.printDate;
    const [year, month, day] = date.split("-");

    return (
      <div className={css.headerContainer}>
        <div>
          <h1 className={css.title}>
            {this.props.title}
          </h1>
          <h2 className={css.date}>
            {month}/{day}/{year}
          </h2>
          <h3 className={css.byline}>
            {author}
          </h3>
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
