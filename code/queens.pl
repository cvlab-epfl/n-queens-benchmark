/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   N Queens solving.

   https://www.metalevel.at/queens/
   ================================

   Written Feb. 2008 by Markus Triska (triska@metalevel.at)
   Public domain code.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

:- use_module(library(clpfd)).

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   Constraint posting.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

n_queens(N, Qs) :-
    length(Qs, N),
    Qs ins 1..N,
    safe_queens(Qs).

safe_queens([]) :- print(1),fail.
safe_queens([Q|Qs]) :- safe_queens(Qs, Q, 1), print(2), safe_queens(Qs).

safe_queens([], _, _).
    safe_queens([Q|Qs], Q0, D0) :-
    Q0 #\= Q,
    abs(Q0 - Q) #\= D0,
    D1 #= D0 + 1,
    safe_queens(Qs, Q0, D1).


foo([]).
foo([Q|Qs]) :-
    print(Q),
    foo(Qs).

:- n_queens(4, Qs), labeling([ff], Qs).


/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   Examples:

   ?- n_queens(8, Qs), labeling([ff], Qs).
   Qs = [1, 5, 8, 6, 3, 7, 2, 4] ;
   Qs = [1, 6, 8, 3, 7, 4, 2, 5] .

   ?- n_queens(100, Qs), labeling([ff], Qs).
   Qs = [1, 3, 5, 57, 59, 4, 64, 7, 58|...] .

   ?- show(8, [ff], Qs).
   Qs = [1, 5, 8, 6, 3, 7, 2, 4] .

   ?- n_queens(8, Qs), show(8, [ff], Qs).
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/* win_menu:load('/Users/fua/papers/20/misc/queens/code/queens.pl').   */
/* win_menu:load('/Users/fua/papers/20/misc/queens/code/animate.pl').  */
