# `test_fill` log

For internal use.

### 1/13/2023
- Session 1
  - `time_limit`: Tested 2, 5, 10 sec. 2 sec is best in almost all cases, and is
  up to 2 times faster (on average to produce successful grid fills) than 5 sec 
  and 4 times faster than 10 sec.
  - `selector`: Tested `Selector` and `ProbabilisticSelector`. They perform 
  similarly in speed, but `ProbabilisticSelector` has similarity scores up to 
  1.5 lower.
  - `num_sample_strings`, `num_test_strings`: No statistically significant trends. `num_sample_strings=10`, `num_test_strings=5` seem popular, but will maintain 
  the same values.

- Session 2
  - Used `time_limit=2` (but can do lower for $n \in \{5, 7, 9, 11\}$, which have
  corresponding runtimes around 0.01s, 0.5s, 0.3s, 0.4s respectively; $n=13$ has
  mean runtime around 1s and $n=15$ around 2s). These may
  (should) change with updates to `const.WORD_LENGTH_REQUIREMENTS`.
  - Used only `ProbabilisticSelector`.
  - `num_sample_strings=10`, `num_test_strings=5` typically performs best among
  $(5, 2), (10, 2), (10, 5), (20, 5), (20, 10)$.