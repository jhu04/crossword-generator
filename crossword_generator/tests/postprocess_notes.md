# Notes on `test_fill`

For internal use.

1/13/2023
- Initial run
  - `time_limit`: Tested 2, 5, 10 sec. 2 sec is best in almost all cases, and is up to 2 times faster (on average to produce successful grid fills) than 5 sec and 4 times faster than 10 sec.
  - `selector`: Tested `Selector` and `ProbabilisticSelector`. They perform similarly in speed, but `ProbabilisticSelector` has similarity scores up to 1.5 lower.

