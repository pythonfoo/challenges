Challenge
=========

Write a programm that reads 2 txt input file and spit out a list of found words.

The word can appear in the following directions.

`diagonal up`, `left to right`, `diagonal down`, `down`

input
-----

`chargrid.txt`:
* new line seperated text file
* each line has the same length
* case should be ignored
* not ever position has a valid character
* ` ` space or `.` dot indicate an hole in the grid

output
------

<word> (<line>,<column>,<length>)

* `<line>`: 0 index, first line in the document is 0
* `<column>`: 0 index, first column, (left side) is 0
* `<length>`: int minimum 3 characters

References:
-----------

wordlists:

official scrabble world list (zinga) `zingarelli2005.txt`:
http://www.isc.ro/en/commands/lists.html
(via https://en.wikipedia.org/wiki/Official_Tournament_and_Club_Word_List)

keepassx wordlist: `eff_large.wordlist`

Both lists are sorted alphabetically.
