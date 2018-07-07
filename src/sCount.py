import nltk
import string
import re
import stanfordcorenlp


# Do the writer's full stops correspond with the end of a sentence?
#   - Run-on sentence
#       - Break this into two thoughts?
#   - Incomplete sentence
#       - Try to combine with downstream ideas?
#
# Does the sentence contain a complete subject / object
#   - Forms of Sentences
#   - S -> NP VP        // Declarative
#   - S -> Aux NP VP    // Yes-No Question
#   - S -> WhAux NP VP  // Wh Question
#   - S -> VP           // Command

# Start with just one sentence

class SentenceCount():

    parser = ""


    def __init__(self):
        self.parser = nltk.CoreNLPParser(url="http://localhost:9000")
        return;

    # Comb through text and ensure that periods and commas have a space after them.
    def preProcess(self, text):
        text = text.replace(".", ". ")
        text = text.replace(",", ", ")
        text = text.replace(" i ", " I ")
        text = text.replace("  ", " ")
        return text;


    def scoreSentenceCount(self, essay):

        clauseCount = 0
        result = 0

        cleanEssay = self.preProcess(essay)
        sentences = nltk.sent_tokenize(cleanEssay)


        for sentence in sentences:
            #print(sentence)
            try:
                (parse, ) = self.parser.raw_parse(sentence)
                #parse.pretty_print()
                clauseCount += self.rec_count(parse)
            except:
                clauseCount = 0
        # Plotted clause count vs High/Low using matplotlib
        # Found no High scoring essays had fewer than 35 clauses
        # Found no Low scoring essays had greater than 60 clauses

        return clauseCount




    def rec_count(self, tree):
        # End recursion at leaf node
        count = 0;
        if type(tree[0]) is str:
            #print(tree[0], " ")
            return 0;

        if tree._label == 'S':
            count = 1;

        for node in tree:
            count += self.rec_count(node)

        return count;



if __name__ == "__main__":

    # Input a sentence
    userSentence = input("Enter a sentence: ")

    # Ensure there are spaces between periods and commas. This may not work so well for elipses,
    # But those shouldn't really be in academic writing...

    sva = SentenceCount()
    print(sva.scoreSentenceCount(userSentence))
    print("goodbye")




