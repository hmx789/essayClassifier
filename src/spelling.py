#
#  Class spelling.py by George Dill 2-Apr-2018
#  Class compares given words to OpenOffice dictionary and counts the
#  word as incorrect if it is not found.
#
#  Corrections are made for inflections, as the OpenOffice dictionary
#  does not explicitly list them.
#
#  Proper capitalisation of words is not checked.
#
#

import nltk
from nltk.corpus import words
import string


class Spelling():
    numErrors = 0
    numWords = 0
    dictionary = dict()

    """ Check for punctuation """
    def isPunct(self, c):
        if c in string.punctuation:
            return True;

        return False;

    # Put corpus in hash map to speed up search
    def __init__(self):
        for word in words.words():
            # Lets not bother with capitalisation just yet
            word = word.lower()
            self.dictionary[word] = True

    def doubleConsonant(self, word):
        if word[-1] == word[-2]:
            newWord = word[:-1]
            if newWord in self.dictionary:
                return newWord
        return word;

    """ Strip ed, s endings"""
    def stripEnding(self, word):

        # Deal with Gerund *ing
        if "ing" in word[-3:]:
            word = word[:-3]
            word = self.doubleConsonant(word)
            if word not in self.dictionary:
                word = word + "e"

        # Plural ies
        elif "ies" in word[-3:] or "ied" in word[-3:]:
            word = word[:-3] + "y"

        # Plural "ren" as in children
        elif "ren" in word[-3:]:
            word = word[:-3]

        # Plural s
        elif "s" in word[-1:]:
            word = word[:-1]
            # Strip tailing e if required
            if word not in self.dictionary:
                word = word[:-1]


        # Past tense "ed"
        elif "ed" in word[-2:]:
            word = word[:-2]
            word = self.doubleConsonant(word)
            if word not in self.dictionary:
                word = word + "e"

        # Past participle "n"
        elif "n" in word[-1:]:
            word = word[:-1]

        # Adjective "ier"
        elif "ier" in word[-3:]:
            word = word[:-3]
            word += "y"

        # Adjective "er"
        elif "er" in word[-2:]:
            word = word[:-2]


        return word;

    """ Checking spelling 
        Returns the % incorrect spelling errors 
    """

    def spellCheck(self, essay):
        text = essay.split()
        text = nltk.pos_tag(text)

        self.numErrors = 0
        for pair in text:
            # Split the word / tag pair
            word = pair[0]
            tag = pair[1]
            wList = []

            # If word is a number, skip
            if "CD" == tag:
                continue

            word = word.lower()

            # Remove trailing punctuation
            while(self.isPunct(word[len(word)-1]) and len(word) > 1):
                word = word[:-1]

            wList.append(word)
            # Split word by internal punctuation
            for i in range(0, len(word)):
                if self.isPunct(word[i]):
                    wList.pop()
                    wList.append(word[:i])
                    wList.append(word[i+1:])

            # Look for word in dictionary

            for word in wList:
                self.numWords += 1
                # Skip if word is whitespace
                if word.isspace() or len(word) == 0:
                    continue

                if word not in self.dictionary:
                    # Handle regular plurals and 'ed' endings
                    newWord = self.stripEnding(word)

                    if newWord in self.dictionary:
                        continue

                    self.numErrors += 1

        pcError = 100 * self.numErrors / self.numWords

        return pcError

