import nltk
import string

""" A class for holding word / tag counts for an essay type """

class classStats():


    wordCount = dict()      #Unique word / tag pairs
    bigramCount = dict()    #Unique tag/tag pairs
    tagCount = dict()       #Unique tags
    uniqueWords = 0


    def __init__(self):
        return;



    """ Count bigrams """
    def countBigram(self, tag1, tag2):
        # Count Pairs
        if (tag1, tag2) in self.bigramCount:
            self.bigramCount[(tag1, tag2)] = self.bigramCount[(tag1, tag2)] + 1
        else:
            self.bigramCount[(tag1, tag2)] = 1

        # Count individual tags
        if tag1 in self.tagCount:
            self.tagCount[tag1] = self.tagCount[tag1] + 1
        else:
            self.tagCount[tag1] = 1

        return;

    """ Stripping words of punctuation and sent to lower case for accurate counts"""
    def cleanWord(self, word):
        word = word.casefold()

        for c in string.punctuation:
            word = word.replace(c, "")

        return word;

    """ Add words to the dictionary """
    def addWord(self, word, tag):
        word = self.cleanWord(word)

        if (word, tag) in classStats.wordCount:
            classStats.wordCount[(word, tag)] = classStats.wordCount[(word, tag)] + 1

        else:
            classStats.wordCount[(word, tag)] = 1

        return;

    """ Print all word productions probability """
    def printAll(self):
        for pairs in self.wordCount:
            print(pairs, " ", self.productionProb(pairs[0], pairs[1]))
        return;

    """ Return lexical production probability """
    def productionProb(self, word, tag):
        word = self.cleanWord(word)
        wordCount = self.wordCount[(word, tag)]
        tagCount = 0

        for pairs in self.wordCount:
            if pairs[1] == tag:
                tagCount += self.wordCount[pairs]

        return wordCount / tagCount

    """ Return POS production probability"""
    def posProb(self, unknownTag, givenTag):
        return;

    """ Print all bigram counts """
    def printBigrams(self):
        for pairs in self.bigramCount:
            print(pairs, " ", self.bigramCount[pairs])

        return;

    # Return bigram probability
    def bigramProbabilityTag(self, currTag, prevTag):
        bigramCount = 0
        prevCount = 0

        bigramCount = self.bigramCount[(prevTag, currTag)]
        prevCount = self.tagCount[prevTag]

        return (bigramCount + 1) / (prevCount + self.uniqueWords)

    # Return

""" Read the corpus of essays and categorize the words and POS found """

class nGramModel():

    highStats = classStats()
    lowStats = classStats()

    """ Get identifying information from file and load text
        into bigram model"""

    def countbigram(self, line):

        # Open the file and load the essay into memory
        file = open("./essays/" + line[0])
        essay = file.read()

        # Tag the POS
        essay = essay.split()
        tags = nltk.pos_tag(essay)

        # Count the tags
        for tag in tags:
            if "high" in line[2]:
                #print(tag[0] + tag[1])
                self.highStats.addWord(tag[0], tag[1])
            else :
                self.lowStats.addWord(tag[0], tag[1])

        for tag1, tag2 in zip(tags[0:len(tags)-1], tags[1:]):
            if "high" in line[2]:
                self.highStats.countBigram(tag1[1], tag2[1])
            else:
                self.lowStats.countBigram(tag1[1], tag2[1])

        # Now that all words and bigrams have been counted store the probabilities


        return;


    """Load the training essays"""

    def __init__(self):
        """ Import the table of contents """
        toc = open("./index.csv", 'r')

        # Import the table of contents
        lines = toc.readlines()

        # Skip the title line
        lines.pop(0)

        for line in lines:
            line =  line.split(';')
            self.countbigram(line)

        # Print my counts for debugging
        # self.highStats.printAll()
        # self.highStats.printBigrams()

        return;

