# Crossword Generator

Automates "dense" crossword generation.

Thanks to:
* [George Ho](https://cryptics.georgeho.org/): [dataset](https://cryptics.georgeho.org/data/clues) of crossword clues
* [@omfgtora](https://github.com/omfgtora) and [@gzzo](https://github.com/gzzo): [React crossword template](https://github.com/gzzo/crosswords)

----

## TODO (11/26)

* Database setup
    * Create a sample table, write to it from Python, and read from it from JS
* Python
    * Generate grids, assign them some id (`[a-zA-Z]{6}`), and write the result (id, size $n$, string of length $n^2$ representing the grid, and dictionary/json of clues)
        * Leave this running for ~1 week and see how much we get lol
    * Add enough dailies ($5\times5$ or $6\times6$ mini; $12\times12$ through $15\times15$ maxi) for ~2 years, or as much as we can reasonably put with reasonable supply for free mode
        * That is, pick a puzzle arbitrarily and replace its id with one of `mini-yyyy-mm-dd` or `maxi...` or something
* Javascript
    * Pick a better name for maxi?
    * Fix frontend
        * Position things correctly vertically on homepage
        * Fix modal
        * Create menu for free mode dimension selection
    * Figure out how to use database as `contentBase`
        * Convert the json to a usable format (intentional; storing json in this format takes more space, and runtime here should be $<900$ operations)
        * Daily: query the database for the appropriate id and display it under `puzzle/mini` or `puzzle/maxi`
        * Free: query the database for the appropriate dimension and display it under `puzzle/6charid`