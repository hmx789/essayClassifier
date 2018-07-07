import nltk
import string
import re
import stanfordcorenlp

# Reference:
# Yuzhu Wang, Hai Zhao, and Dan Shi. 2015. "A Light Rule-based Approach to English Subject-Verb Agreement Errors
#       on the Third Person Singular Forms." PACLIC 29 345-353

# Identify subject verb agreement
# Identify complete sentences

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

class SubjVerbAgreement():

    def __init__(self):
        return;

    # Comb through text and ensure that periods and commas have a space after them.
    def preProcess(self, text):
        text = text.replace(".", ". ")
        text = text.replace(",", ", ")
        text = text.replace(" i ", " I ")
        text = text.replace("  ", " ")
        return text;

    # Dec agreement by tracking subjects and then first occurance of verb

    def decAgreement(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        pos = nltk.pos_tag(tokens)
        #print(pos)

        subjects= []
        headVerb = False
        agreement = True

        for tag in pos:
            print(tag)
            tag = (tag[0].casefold(), tag[1])

            if tag[1] == "NN" or tag[1] == "NNP" or  tag[1] == "NNS" or \
                    tag[1] == "NNPS" or tag[1] == "PRP":
                subjects.insert(0, tag)

            if tag[1] == "VBG":
                subjects.insert(0, tag)

            # For the second half of a compound sentence clear and check agreement again.
            if tag[1] == "CC" or tag[1] == "IN" or tag[1] == "," and headVerb:
                subjects.clear()
                headVerb = False

            if tag[1] == "VBD":
                headVerb = True
                if len(subjects) is 0:
                    return False;

            if tag[1] == "VBZ":
                headVerb = True
                # If there is more than one subject, this should be plural
                if len(subjects) > 1 or len(subjects) == 0:
                    return False

                # Check for third person
                for subject in subjects:
                    if subject[0] == "i" or subject[0] == "we" or subject[0] == "they":
                        return False;

            # Non Third Person Singular
            if tag[1] == "VBP":
                headVerb = True
                if len(subjects) is 0:
                    return False;
                if tag[0] == "am" and not subjects[0][0] == "i" and len(subjects) > 1:
                    return False;
                if tag[0] == "are" and subjects[0][0] == "i" and len(subjects) == 1:
                    return False;
                if "s" in tag[0][-1]:
                    return False;


        return agreement

    def scoreAgreement(self, essay):

        sentenceCount = 0
        errorCount = 0

        cleanEssay = self.preProcess(essay)
        sentences = nltk.sent_tokenize(cleanEssay)


        for sentence in sentences:
            print(sentence)

            sentenceCount += 1
            if not self.decAgreement(sentence):
                errorCount += 1
                print("bad sentence")
            else:
                print("good sentence")

        return float(errorCount / sentenceCount)


if __name__ == "__main__":

    # Input a sentence
    userSentence = input("Enter a sentence: ")

    # Ensure there are spaces between periods and commas. This may not work so well for elipses,
    # But those shouldn't really be in academic writing...

    sva = SubjVerbAgreement()
    sva.scoreAgreement(userSentence)
