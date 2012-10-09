PyTuring
========

A multi tape turing machine emulator written in Python.

The other part of my school project relating to turing machines.

Turing machine programs are written in a very specific way. The lines are as follows:

first line is the number of tapes. This is a multitape machine and the number is technically unbounded.

The second line is the symbols used in the tape, space delimited. Can accept hexadecimal values via `"0x*hexvalue*"`, quotes included. Has a shortcut `ascii` that has it accept the set of ascii characters.

The third line is a list of states. States can be named whatever you want, but are traditionally named q0, q1, q2, etcetera.

The fourth line is the starting state, the state that the machine begins at. Traditionally q0.

Following this is a list of transitions. Transitions are of the format: `StartState,EndState,[InTapeState/OutTapeState/Direction,]*TapeCount`

* StartState is the state that the transition is executed on.
* EndState is the state the machine is sent to if the transition is taken
* InTapeState is the value to be matched for the transition. This is a regular expression for ease of use (some definition files can be terabytes in length if this weren't regular expressions). You can use the word `Blank` to accept a blank (written as `Blank` in the tape file). Also created shortcut `Unconditional`, which will take this transition always, useful for an "else" kind of idea.
* OutTapeState is the value to be written back to the tape. Because the in state is a regular expression, I created a shortcut to write back whatever is found to the tape, just write `self`. Can also write a blank with the command `Blank`.
* Direction is the direction the tape head will move after this transition. L is left, R is right, N makes it not move.
* TapeCount is the number of tapes you have in the machine, you need an InTapeState, OutTapeState, and Direction for each one.

Examples can be found in the examples directory.

Usage: `Python TM.py [tmFile] [options] [TapeFile]*`

tmFile is a turing machine file. If it is not included here, it will be asked for after starting the program.

Options are

* -nl: removes the nl that most text editors put at the end of files. Turing machines usually don't take \n into acount.
* -o: outputs all the tapes to files named "Tape[n]" after it finishes executing
* -db: prints debug information as the program runs.
* -dbs: prints debug information as the program runs, but also steps through each transition

TapeFile is a file that initializes the tapes to a certain value. If you have this, you need to have one for every tape your machine uses.

