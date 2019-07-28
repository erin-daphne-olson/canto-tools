# canto-tools
Tools for making and working with phonological tableaux for Cantonese (LSHK) data

This script is meant to be a repository for general purpose functions having
to do with the construction of phonological tableaux in Python 3.7. As many
of these were constructed primarily for working with the LSHK transcription
system of Cantonese, they are not guaranteed to be fully appicable to all
languages as of this time.

# Kinds of functions included here
## Segment-oriented functions
Sets up interesting classes of segments in LSHK transcription and their associated 
regex patterns. Also sets up relevant segmental context functions using regex.

## Syllable parsing functions
Defines functions for parsing an LSHK-compliant syllable of Cantonese into
standard syllable components, and for checking whether each component is allowed
in LSHK transcription.

## Candidate generator functions
Defines functions for generating empty Candidates (see definition below), given 
a target input transcription. Contains two main functions:
* GEN_ONE(), for generating all alternate forms that instantiate one deletion or insertion of a phonological segment
* GEN_TWO() for generating all alternate forms created in GEN_ONE(), plus those that combine one deletion and one insertion

## Eval function
Defines a function that applies all Constraint functions to each Candidate 
in a Tableau (see definitions below).

## Candidate object definition
Defines a Candidate object with attributes:
* Output, representing the LSHK transcription of the candidate
* Parsed_output, representing the result of applying the syllable parsing function to the LSHK transcription
* Frequency, reprsenting how often that output is seen in the corpus
* Violations, a list representing the number of times the candidate violates the constraints listed in the tableau

Contains methods for safe access of each attribute, as well as methods for:
* Setting the value of the frequency attribute
* Increasing the value of the frequency attribute

## Tableau object definition
Defines a Tableau object with attributes:
* Input, representing the LSHK transcription of the input from the corpus
* Parsed_input, representing the result of applying the syllable parsing function to the LSHK transcription
* Constraints, a list of functions to be applied to each candidate
* Inclusion, a Boolean to determine whether the Tableau should be included in a file or not
* Candidates, a dictionary of each Candidate object associated with the input

Contains methods for safe access of each attribute, as well as methods for:
* Adding to the list of constraints
* Adding to the dictionary of Candidates
* Changing the value of the Inclusion attribute
* Generating a print version of the Tableau for file writing

## Constraint object definition and generic functions
Defines a Constranint object with attributes:
* Name of the constraint
* Kind, a string indicating the generic function used to generate the constraint function
* Description, a string that describes the desired behaviour of the constraint function
* Function, a function to be applied to a Candidate during the evaluation process

Contains methods for safe access of each attribute.

Generic functions for each kind of constraint are provided here as well. These include:
* Component_Check, which searches for the presence or absence a particular syllabic component
* Phonotactic, which finds all instances of a regex pattern in a Candidate transcription
* Generic_Dep, which searches a Candidate for an insertion in context
* Generic_Max, which searces a Candidate for a deletion in context
