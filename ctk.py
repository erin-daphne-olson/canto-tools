# Toolkit for working with Cantonese Phonology
# Erin Olson ekolson@mit.edu
# Last updated: 2019 07 12

# This script is meant to be a repository for general purpose functions having
# to do with the construction of phonological tableaux in Python 3.7. As many
# of these were constructed primarily for working with the LSHK transcription
# system of Cantonese, they are not guaranteed to be fully appicable to all
# languages as of this time.

# Things to include:
#   x 0. Alphabet
#   x 1. Syllable parser
#   x 2. Gen functions
#   x 3. Eval function
#   x 4. Candidate object
#   x 5. Tableau object
#   x 6. Constraint object (new)

import re
import string



# ---------- 0. Alphabet to be used ----------------------------------------- #
OBSTRUENTS = ["b", "p", "f", "d", "t", "g", "gw", "k", 'kw', "h"]
obst_pattern = "[bpdtgkfh]w?"

SIBILANTS = ["c", "z", "s"]
sib_pattern = "[czs]"

GENERAL_OBST = OBSTRUENTS + SIBILANTS
gen_obst_pattern = "[bpdtgkfhczs]w?"

SONORANTS = ["l", "j", "m", "n", "ng", "w"]
son_pattern = "[mnwlj]g?"

CONSONANTS = OBSTRUENTS + SIBILANTS + SONORANTS + ["C"]
cons_pattern = "[Cbpdtgkmnfsczhljw][wg]?"

CODAS = ["m", "n", "ng", "p", "t", "k", "j", "w", "C"]
coda_pattern = "[Cptkmnjw]g?"

VOWELS = ["aa", "a", "e", "i", "o", "oe", "eo", "u", "yu", "V"]
vowel_pattern = "[Vaeo]+|yu|[iu]"

# Set up interesting contexts for use in the Dep constraints
def post_consonant(char):
    """Returns a string with the appropriate post-consonantal environment."""
    # regexr 4cs1n for testing
    return "({0})\s*({1})".format(cons_pattern, char)

def pre_consonant(char):
    """Returns a string with the appropriate pre-consonantal environment."""
    # regexr 4cuau for testing
    return "({0})\s*({1})".format(char, cons_pattern)

def post_vowel(char):
    """Returns a string with the appropriate post-vocalic environment."""
    # regexr 4cuc2 for testing
    return "({0})\s*({1})".format(vowel_pattern, char)

def pre_vowel(char):
    """"Returns a string with the appropriate pre-vocalic envrionment."""
    # regexr 4cuc8 for testing
    return "({0})\s*({1})".format(char, vowel_pattern)

# Make a unique kind of error for unwanted characters
class CharacterError(Exception):
    """Error class for non-Chinese characters."""
    pass



# ---------- 1. Syllable parsing -------------------------------------------- #
# Make a checking function for each component of the transcription system
def check_onset(onset, verbose=False):
    """Takes a hypothesized onset and makes sure it is a consonant or the empty string.
    If verbose is True, displays a warning to the user."""
    if onset == "" or onset in CONSONANTS:
        return onset
    else:
        if verbose:
            print( "WARNING: Onset cannot be %s." % (onset) )
        raise CharacterError

def check_vowel(vowel, verbose=False):
    """Takes a hypothesized vowel and makes sure it is a vowel or syllabic sonorant.
    If verbose is True, displays a warning to the user."""
    if vowel in VOWELS or vowel in ["m", "n", "ng"]:
        return vowel
    else:
        if verbose:
            print( "WARNING: Vowel cannot be %s." % (vowel) )
        raise CharacterError

def check_coda(coda, verbose=False):
    """Takes a hypothesized coda and makes sure it is a licit coda segment.
    If verbose is True, displays a warning to the user."""
    if coda == "" or coda in CODAS:
        return coda
    else:
        if verbose:
            print( "WARNING: Coda cannot be %s." % (coda) )
        raise CharacterError

def check_tone(tone, verbose=False):
    """Takes a hypothesized tone and makes sure it is a numeric character.
    If verbose is True, displays a warning to the user."""
    if tone.isdigit():
        return tone
    else:
        if verbose:
            print( "WARNING: Tone cannot be %s." % (tone) )
        raise CharacterError

# Make a function to partition a syllable into onset, nucleus, and coda
def split_syllable(sigma, warning=False, verbose=False):
    """Takes a string representing a syllable and returns a tuple of substrings
    of the form ('onset', 'nucleus', 'coda', 'tone'). If warning is True, runs
    the check functions on the result before returning to the user. If verbose
    is True, displays which forms are ruled out by the checking functions."""
    # Set defaults
    onset = ""; nucleus = ""; coda = ""; tone = ""

    if sigma in ["", " "]:
        return (onset, nucleus, coda, tone)

    try:
        # Begin by parsing the tone, if there is one
        if sigma[-1].isdigit():
            tone = sigma[-1]
            # Peel off tone to work with segments only
            segments = sigma[:-1]
        # Otherwise, proceed as usual
        else:
            segments = sigma

        # If it's a single member syllable, store the segment as the nucleus
        if (segments in CONSONANTS) or (segments in VOWELS):
            nucleus = segments

        # Otherwise, if it's not a recognized consonant or vowel, store it as
        # a nucleus for the purposes of checking
        elif len(segments) == 1:
            nucleus = segments

        # Otherwise, if it's a two-segment word, split into vowels and consonants
        elif len(segments) == 2:
            # If the first segment is a consonant...
            if segments[0] in (OBSTRUENTS + SIBILANTS + ["l", "j", "w", "C"]):
                # ...store it as the onset
                onset = segments[0]
                # Then, if the second segment is an obstruent...
                if segments[1] in OBSTRUENTS + SIBILANTS:
                    # ... store it as the coda
                    coda = segments[1]
                # Otherwise, store it as the nucleus
                else:
                    nucleus = segments[1]

            # If the first segment is a nasal and it's followed by a vocalic
            # segment...
            elif segments[0] in ["m", "n", "ng"] and segments[1] in VOWELS + ["j", "w"]:
                # ... the nasal is the onset and the vowel is the nucleus
                onset = segments[0]; nucleus = segments[1]

            # Otherwise, assume the syllable consists of a nucleus and a coda
            else:
                nucleus = segments[0]; coda = segments[1]

        # Otherwise, use regular expressions to parse the syllable
        elif len(segments) > 2:
            # First, find the group of all consonants at the front of the syllable
            onset = re.search("^({0})*".format(cons_pattern), segments).group()
            x = len(onset)

            # Next, scan the rest of the string for the first licit nucleus
            nucleus = re.search("([aeo]+|[iumljw]|yu|ng?)|V|$", segments[x:]).group()
            y = x + len(nucleus)

            # If there are no more segments in the string after these two
            # parsing steps ...
            if y == len(segments):
                # ... the coda must be empty
                coda = ""
            # Otherwise, the coda is just the rest of the string
            else:
                coda = segments[y:]

            # Quick fix #1 -- if there's only an onset left, re-parse it as a
            # nucleus
            if nucleus == "" and coda == "":
                if onset[:2] == "ng":
                    nucleus = onset[2:]; onset = "ng"
                elif onset[-2:] == "ng":
                    nucleus = "ng"; onset = onset[:-2]
                else:
                    nucleus = onset; onset = ""

            # Quick fix #2 -- if there's only a nasal onset and coda left,
            # reparse as a nucleus
            if onset in ["m", "ng", "n"] and nucleus == "":
                nucleus = onset; onset = ""

        # If warning mode is on, check whether the syllable is a licit syllable of
        # Cantonese
        if warning:
            onset = check_onset(onset, verbose)
            nucleus = check_vowel(nucleus, verbose)
            coda = check_coda(coda, verbose)
            tone = check_tone(tone, verbose)

    except CharacterError:
        if verbose:
            print( "WARNING: [%s] does not conform to standard transcription." % (sigma) )
        return CharacterError

    return (onset, nucleus, coda, tone)



# ---------- 2. Gen functions ----------------------------------------------- #
# Make some helper functions for the Gen functions
# Make a function to split a list of syllables into a list of all possible
# subcomponents
def componify(syll_list):
    """Takes a list of syllables, already divided into their subcomponents,
    and returns a list of components, separated by a space."""
    components = []
    for i in range(len(syll_list)):
        new_components = []
        # Split each syllable into its non-tone components and store in components
        non_tones = syll_list[i].split(".")[:-1]
        # Ensure that all double-segment onsets are also split
        if len(non_tones[0]) > 1 and non_tones[0] not in CONSONANTS:
            new_components.extend(re.findall("ng?|[kg]w?|[Cbpdtmfsczhljw]", non_tones[0]))
        else:
            new_components.append(non_tones[0])
        # Ensure that all double-segment nuclei are also split
        if len(non_tones[1]) >1 and non_tones[1] not in VOWELS + ["ng", "m", "n", "l", "j", "w"]:
            new_components.extend(re.findall(".", non_tones[1]))
        else:
            new_components.append(non_tones[1])
        # Ensure that all double-segment codas are also split
        if len(non_tones[2]) > 1 and non_tones[2] not in CONSONANTS:
            new_components.extend(re.findall("ng?|[kg]w?|[Cbpdtmfsczhljw]", non_tones[2]))
        else:
             new_components.append(non_tones[2])
        # Add the whole thing to the list of components
        components.extend(new_components)
        # Add a space component between each syllable
        if i != (len(syll_list) - 1):
            components.append(" ")

    return components

# Make a re-syllabifier for V-epenthesis candidates
def resyllabify(component_list, k):
    """Takes a list of components and the index of the epenthetic vowel
    and modifies the list of components, so that spaces are inserted
    to reflect new syllable divisions."""

    # First, get the prior context
    if k-3 >= 0:
        before = component_list[k-3:k]
    elif k-2 >= 0:
        before = component_list[k-2:k]
    else:
        before = component_list[:k]

    # Next get the following context
    after = component_list[k+1:k+3]

    # If the prior context is empty...
    if before[-2:] in [[], [""], [" "], ["", ""], [" ", ""], ["", " "], [" ", " "]]:
        # ...and the following context is not a consonant cluster...
        if (after[0] in VOWELS or after[1] in VOWELS + ["j", "w", "l", "m", "n", "ng"]):
            # ...add a space after the vowel
            component_list[k] += " "
        else:
            # ...add a space after the following consonant
            component_list[k+1] += " "

        # ...and the preceding nucleus is actually an obstruent
        if len(before) == 3 and before[-3] in OBSTRUENTS:
            # ...delete any spaces between the vowel and the obstruent nucleus
            component_list[k-1] = ""
            component_list[k-2] = ""

    # If the prior context is a consonant...
    elif (before[-1] in CONSONANTS):
        # ...and if the prior does not have a vowel...
        if len(before) > 1 and before[-2] in VOWELS:
            # ...add a space after that vowel
            component_list[k-2] += " "
        # ... and if the following context is not a vowel, don't add any spaces
        elif len(after) > 1 and after[0] in CONSONANTS and after[1] not in VOWELS:
            pass
        else:
            # ...add a space after the vowel
            component_list[k] += " "
    # If the further-away context is a consonant or a coda
    elif before[-1] == " " and (before[-2] in CONSONANTS):
        # ... take away the space, if there is one...
        component_list[k-1] = ""
        # ...and add a space before the consonant...
        component_list[k-2] = " " + component_list[k-2]
        # ...and add a space after the V
        component_list[k] += " "
    # If the prior context is a vowel...
    elif before[-1] in VOWELS:
        # ...add the space before the vowel
        component_list[k] = " " + component_list[k]

# Make a GEN function that takes an entry and returns a list of all of the
# possible Harmonic Serialism-compliant deletion and epenthesis forms
# for that entry
def GEN_ONE(tableau, const_set):
    """Takes a Tableau object and adds to it a set of empty Candidates,
    representing all single-change deletion and epenthesis forms
    for that Tableau. If const_set is "trigram", split consonants up
    into obstruents, sibilants, and sonorants."""
    # Get a list of syllables from the parsed version of the entry
    syllables = tableau.get_parsed_input().split()

    # Get a list of all of the syllable components
    components = componify(syllables)

    # Add the fully faithful Candidate to the Tableau
    tableau.add_candidate("".join(components).strip())

    # Get the single deletion Candidates
    for j in range(len(components)):
        if components[j] not in (" ", ""):
            components_copy = components[:]
            deleted = components_copy.pop(j)
            tableau.add_candidate("".join(components_copy))

    # Get the single epenthesis candidates, both vowel and consonant
    for k in range(len(components)):
        if components[k] not in (" ", ""):
            # Add the vowel epenthesis candidate
            components_V = components[:]
            components_V.insert(k, "V")
            # Do some extra work on the V-epenthesis candidates to make
            # sensisble syllable divisions
            resyllabify(components_V, k)
            # Add the resulting candidate
            tableau.add_candidate("".join(components_V))

            # Depending on the kind of constraint set used, add the consonant
            # epenthesis forms
            if const_set == "trigram":
                components_T = components[:]; components_T.insert(k, "T"); tableau.add_candidate("".join(components_T))
                components_S = components[:]; components_S.insert(k, "S"); tableau.add_candidate("".join(components_S))
                components_R = components[:]; components_R.insert(k, "R"); tableau.add_candidate("".join(components_R))
            else:
                components_C = components[:]; components_C.insert(k, "C")
                # Add the C-epenthesis candidates as-is
                tableau.add_candidate("".join(components_C))

    # Add the word-final epenthesis candidates
    if const_set == "trigram":
        tableau.add_candidate("".join(components + ["T"]))
        tableau.add_candidate("".join(components + ["S"]))
        tableau.add_candidate("".join(components + ["R"]))
    else:
        tableau.add_candidate("".join(components + ["C"]))
    if components[-1] in CONSONANTS:
        # Resyllabify the final consonant as an onset, if there is one
        components[-1] = " " + components[-1]
        tableau.add_candidate("".join(components + ["V"]))
    else:
        # Just treat the final vowel as its own syllable
        tableau.add_candidate("".join(components + [" V"]))

# Make a GEN function that takes an entry and returns a list of all of the
# # possible two-change deletion and epenthesis forms for that entry
def GEN_TWO(tableau, const_set):
    """Takes a Tableau object and adds to it a set of empty Candidates,
    representing all single- and select double-change deletion and
    epenthesis forms for that Tableau. If const_set is "trigram", split
    consonants up into obstruents, sibilants, and sonorants."""
    # First, get the single-change deletion and epenthesis forms
    GEN_ONE(tableau, const_set)

    # Next, get the list of Candidates
    candidates = tableau.get_candidates()

    # Find only the deletion candidates
    del_candidates = [ x for x in candidates[1:] if ("C" not in x) and ("V" not in x) and ("T" not in x) and ("S" not in x) and ("R" not in x) and x != "" ]
    for d in del_candidates:
        # Get the parsed entry for that candidate
        d_parsed = tableau.get_candidate(d).get_parsed_output().split()

        # Split into components
        components = componify(d_parsed)

        # Next, add the Vowel epenthesis candidates
        for k in range(len(components)):
            if components[k] not in ["", " "]:
                components_V = components[:]
                components_V.insert(k, "V")
                # Run the resyllabifier
                resyllabify(components_V, k)
                # add the resulting candidate
                tableau.add_candidate("".join(components_V))

        # Add the word-final epenthesis candidate
        if components[-1] in CONSONANTS:
            # Resyllabify as an onset
            components[-1] = " " + components[-1]
            tableau.add_candidate("".join(components + ["V"]))
        elif components[-1] in ["", " "] and components[-2] in CONSONANTS:
            components[-2] = " " + components[-2]
        else:
            # Treat the final vowel as its own syllable
            tableau.add_candidate("".join(components + [" V"]))



# ---------- 3. Eval function ----------------------------------------------- #
# Make an EVAL function that takes a Tableau object and applies each
# Constraint in its constraint list to each of its Candidates, storing it in
# each Candidate's list of violations.
def EVAL(tableau):
    """"Takes a Tableau object and applies each of its Constraints to each
    of its Candidates, storing the results in the Candidate's violation list."""
    # First, get the list of Constraints
    const_names = tableau.get_constraints()
    # And the list of Candidates
    cand_names = tableau.get_candidates()

    for const in const_names:
        # Get the Constraint object itself
        f = tableau.get_constraint(const)

        # Loop through the Candidates and apply the constraint
        for cand in cand_names:
            # Get the Candidate itself
            c = tableau.get_candidate(cand)

            # Apply the Constraint to the candidate, depending on its type
            if f.get_type() in ["Dep", "Phonotactic"]:
                # Use the unparsed output form of the Candidate
                v = f.func(c.get_output())
            elif f.get_type() == "Max":
                # Use both the parsed input of the Tableau and the parsed ouptut
                # of the Candidate
                v = f.func(tableau.get_input(), c.get_output())
            else:
                # Use the parsed output of the Candidate
                v = f.func(c.get_parsed_output())

            # Add the violation to the Candidate
            c.add_violation(v)




# ---------- 4. Candidate handling ------------------------------------------ #
# Candidate object
class Candidate():
    def __init__(self, out, win=0, vios=[]):
        """Initialization function for a Candidate object.
        Takes an output string, a value representing its output probability,
        and a list of violations, and stores them to the Candidate as output,
        freq, and violations, respectively.
        The default value for freq is 0, and the default value for vios is
        the empty set.
        Parses the output into its sub-syllabic consituents and stores it
        as parsed_output."""
        self.output = out
        components = ""
        for sigma in out.split():
            components += (".".join(list(split_syllable(sigma))) + " ")
        self.parsed_output = components.strip()
        self.freq = win
        self.violations = vios

    def __repr__(self):
        return "Candidate '{0}'".format(self.output)

    def get_output(self):
        """Returns the output attribute of the Candidate."""
        return self.output

    def get_parsed_output(self):
        """Returns the parsed output attribute of the Candidate."""
        return self.parsed_output

    def get_freq(self):
        """Returns the frequency attribute of the Candidate."""
        return self.freq

    def get_violations(self):
        """Returns a copy of the violation attribute of the Candidate."""
        return self.violations[:]

    def add_violation(self, x):
        """Adds a value to the violation attribute of the Candidate."""
        # NOTE: I had to make it this clunky, because if I tried to access
        # an empty violations attribute directly, the script treated all
        # instances of the empty set created by GEN as identical,
        # and appending x to the violation profile of any candidate led
        # to appending x to the violation profile of every candidate.
        old_vios = self.get_violations()
        old_vios.append(x)
        self.violations = old_vios

    def add_freq(self, n=1):
        """Adds n to the Candidate's frequency attribute.
        If no n is spedified, adds 1 by default."""
        self.freq += n



# ---------- 5. Tableau handling -------------------------------------------- #
# Tableau object
class Tableau():
    def __init__(self, inp, constraints={}):
        """"Initialization function for a Tableau object.
        Takes an input string and dictionary of Constraints and stores them to
        the Tableau as input and constraints, respectivley, along with an
        inclusion parapmeter, set to False by default; and an empty dictionary
        for storing Candidates.
        Parses the input into its sub-syllabic constituents and stores it as
        parsed_input.
        """
        self.input = inp
        components = ""
        for sigma in inp.split():
            components += (".".join(list(split_syllable(sigma))) + " ")
        self.parsed_input = components.strip()
        self.constraints = constraints
        self.incl = False
        self.cands = {}

    def __repr__(self):
        return "Tableau '{0}' with {1} candidates".format(self.input, len(self.cands))

    def get_input(self):
        """Returns the input attribute of the Tableau."""
        return self.input

    def get_parsed_input(self):
        """Returns the parsed input attribute of the Tableau."""
        return self.parsed_input

    def get_constraints(self):
        """Returns a lis of the Constraint names in the constraints attribute of
        the Tableau."""
        return list(self.constraints)

    def get_constraint(self, const_name):
        """Goven the name of a Constraint, retrieves it from the dictionary.
        If it does not exist, prints a warning and does nothing."""
        try:
            return self.constraints[const_name]
        except KeyError:
            print("WARNING: Tableau does not have a constraint '{0}'.".format(const_name))

    def add_constraint(self, name, kind, function=lambda x: 0, desc=None):
        """If there is no Constraint already present in the Constraint dictionary,
        adds a Constraint to the Tableau object, referred to by its name."""
        new_constraint = Constraint(name, kind, function, desc)
        if new_constraint not in self.get_constraints():
            self.constraints[new_constraint.get_name()] = new_constraint

    def get_candidates(self):
        """Returns a list of Candidate names of the Tableau, by order of insertion."""
        return list(self.cands)

    def get_candidate(self, cand_name):
        """Given the (unparsed) name of a Candidate, retrieves it from the dictionary.
        If it does not exist, prints a warning and does nothing."""
        try:
            return self.cands[cand_name]
        except KeyError:
            print("WARNING: Tableau does not have a candidate '{0}'.".format(cand_name))

    def add_candidate(self, out, win=0, vios=[]):
        """If there is no candidate already present in the candidate ditionary,
        Adds a Candidate to the Tableau object, referred to by its
        out(put) value."""
        new_candidate = Candidate(out, win, vios)
        if new_candidate not in self.get_candidates():
            self.cands[new_candidate.get_output()] = new_candidate

    def vios(self):
        """Returns a list of lists of violation profiles.
        Each violation profile will begin with its probability value, followed by
        the list of constraint violations."""
        profile = []
        for cand in self.get_candidates():
            c = self.get_candidate(cand)
            violine = c.get_violations()
            violine.insert(0, c.get_freq())
            profile.append(violine)
        return profile

    def include(self, value=None):
        """Allows the user to change the inclusion parameter of the Tableau.
        If no Boolean value is passed to the function, returns the current
        value of the inclusion parameter without changing it."""
        if value == None:
            return self.incl
        elif type(value) == bool:
            self.incl = value
        else:
            print("WARNING: Tableau inclusion value cannot be '{0}.".format(value))
            print("         Inclusion value must be a Boolean or None.")

    def print(self, parsed=False):
        """Returns a print-friendly version of the Tableau for writing to
        output files. If parsed is True, returns the parsed versions of all
        inputs and candidates."""
        # Set the input up first
        if parsed:
            ur = self.get_parsed_input()
        else:
            ur = self.get_input()

        # Set up the block of text to be returned
        ur_block = ""

        # Then loop through candidates
        for cand in self.get_candidates():
            # Get the candidate of interest
            c = self.get_candidate(cand)

            # Set up the output
            if parsed:
                sr = c.get_parsed_output()
            else:
                sr = c.get_output()

            # Set up the output line
            line = [ur, sr, str(c.get_freq())] + [ str(x) for x in c.get_violations() ]

            # Add line to block
            ur_block += ("\t".join(line) + "\n")

        # Return the block text
        return ur_block



# ----------- 6. Constraint handling ---------------------------------------- #
# Constraint object
class Constraint():
    def __init__(self, name, kind, function=lambda x: 0, desc=None):
        """Initialization function for a Constraint object.
        Takes a string representing the name of the function, a description
        of its intended purpose, and the kind of the function, as well as the
        evaluation function for the constraint. Stores all variables internally
        as name, description, type, and func, respectively.
        Function will default to returning only 0."""
        self.name = name
        if kind in ["Markedness", "Prosodic", "Phonotactic", "Faithfulness", "Max", "Dep"]:
            self.type = kind
        else:
            print("WARNING: {0} is not a recognized type for Constraint.".format(kind))
            print("         Constraint must be 'Markedness', 'Prosodic', 'Phonotactic',")
            print("         'Faithfulness', 'Max', or 'Dep'.")
            self.type = None
        self.description = desc
        self.func = function

    def __repr__(self):
        return "{1} Constraint '{0}'".format(self.name, self.type)

    def get_name(self):
        """Returns the name attribute of the Constraint."""
        return self.name

    def get_type(self):
        """Returns the type or kind of the Constraint."""
        return self.type

    def get_description(self):
        """Returns the descriptive text for the Constraint, if present"""
        if self.description is not None:
            return self.description
        else:
            print("Constraint '{0}' has no descriptive text.".format(self.name))

# Generic function for checking presence/absence/quality of syllable components
def COMPONENT_CHECK(index, condition_list, ban=True):
    """Takes a list representing the indices of the components to be checked
    (e.g., 0 for "Onset", 2 for "Coda") and a list of (il)licit segments for
    that component, and returns a function that will take an output
    string and return the number of violations of the condition established.
    If ban is True, the condition_list is treated as a ban on that list of
    segments. If ban is False, the condition_list is treated as a requirement
    for that position."""
    def F(output):
        check = 0
        for sigma in output.split():
            components = sigma.split(".")
            for i in index:
                if ban:
                    if components[i] in condition_list:
                        check += 1
                else:
                    if components[i] not in condition_list:
                        check += 1
        return check
    return F

# Generic function for establishing phonotactic restrictions
def PHONOTACTIC(pattern):
    """Takes a string representing the regex pattern of a particular
    phonotactic restriction, and returns a function that will count
    the number of times that pattern occurs in an unparsed output
    string."""
    def F(output):
        return len(re.findall(pattern, output))
    return F

# Generic function for establishing Dep constraints
def GENERIC_DEP(lenv, renv, segment):
    """Takes a function establishing the environments, as defined by
    regex patterns, and a string representing the segment to be scanned for,
    and returns a function that will count the nubmer of times that
    combination of environment and segment occurs in an unparsed output
    string."""
    # Determine the search environment first
    if lenv == None:
        search_string = renv(segment)
    elif renv == None:
        search_string = lenv(segment)
    else:
        search_string = lenv(renv(segment))
    # Define the function
    def F(output):
        return len(re.findall(search_string, output))
    return F

# Generic function for establishing Max contraints
def GENERIC_MAX(segment_pattern, lenv=None, renv=None):
    """Takes the regex pattern for segments being examined for
    deletion, and a pair of lists indicating their deletion environment,,
    and returns a function that will count how many times a segment
    of that class is deleted from an input to an output string."""
    # Determine the search parameter first
    # If it's a context-free constraint, just use the segment pattern
    if lenv == None and renv == None:
        inp_parameter = segment_pattern
        out_parameter = segment_pattern
    # If there is a preceding context (if you need to scan left)
    elif lenv != None and renv == None:
        inp_parameter = "({0})(\s|\d)*({1})".format(lenv, segment_pattern)
        out_parameter = "({0})(\s|[CV])*({1})".format(lenv, segment_pattern)
    elif lenv == None and renv != None:
        inp_parameter = "({0})(\s|\d)*({1})".format(segment_pattern, renv)
        out_parameter = "({0})(\s|[CV])*({1})".format(segment_pattern, renv)
    else:
        inp_parameter = "({0})(\s|\d)*({1})(\s|\d)*({2})".format(lenv, segment_pattern, renv)
        out_parameter = "({0})(\s|[CV])*({1})(\s|[CV])*({2})".format(lenv, segment_pattern, renv)


    def F(inp, outp):
        # Define default behaviour for empty candidates
        if outp == "":
            return 1

        # First, check to see if the search parameter is present in the input
        i_matches = re.findall(inp_parameter, inp)
        if len(i_matches) != 0:
            # See if you can find all of them in the output
            o_matches = re.findall(out_parameter, outp)
            if len(o_matches) == len(i_matches):
                return 0
            else:
                return len(re.findall(segment_pattern, inp)) - len(re.findall(segment_pattern, outp))

        # Define default behaviour
        return 0
    return F
