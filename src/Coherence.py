
import nltk
import sys
import string
import re
import stanfordcorenlp
from nltk.corpus import names       # need to do nltk.download('names')
import random
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import inflect
inflect = inflect.engine()


class Coherence():

    depparser = ""

    def preProcess(self, text):
        # text = text.replace(".", ". ")     # This will cause an error when parsing
        text = text.replace(",", ", ")
        text = text.replace(" i ", " I ")
        text = text.replace("  ", " ")
        return text;

    def __init__(self):
        self.depParser = nltk.CoreNLPDependencyParser(url="http://localhost:9000")


    def gender_features(self,word):
        return {'last_letter': word[-1]};

    def theClassifier(self):        # Used this from the nltk library(http://www.nltk.org/book/ch06.html)
        labeled_names = ([(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
        random.shuffle(labeled_names)
        featuresets = [(self.gender_features(n), gender) for (n, gender) in labeled_names]
        train_set, test_set = featuresets[500:], featuresets[:500]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        return classifier;

    def lemming(self,word):
        Lem = WordNetLemmatizer()
        lemword = Lem.lemmatize(word)
        print (lemword )

    def scoreCoherence(self,essay):
        sentenceLists = []
        score = 0
        processedEssay = self.preProcess(essay)
        sentences = nltk.sent_tokenize(processedEssay)
        processedList = [[]]

        for sentence in sentences:
            parse = self.depParser.raw_parse(sentence)
            classifier = self.theClassifier()
            dep = next(parse)
            processedList = list(dep.triples())
            subjectList = []
            sawFemale = 0
            sawMale = 0
            plural = 0

            # Making a list of new subjects for this sentence and if need be getting rid of old ones
            for tag in processedList:
                if tag[2][1] in ['NNP'] and tag[1] != 'nmod':           # making sure we dont get subject of prepositional phrase
                    genderID = classifier.classify(self.gender_features(tag[2][0]))
                    tup = tag[2] + (genderID,)
                    subjectList.append(tup)

                if tag[1] == 'nsubj' and tag[2][1] != 'PRP':
                    genderID = classifier.classify(self.gender_features(tag[2][0]))
                    tup = tag[2] + (genderID,)
                    subjectList.append(tup)

            sentenceLists.append(subjectList)
            for sentence in sentenceLists:          #Checking if a sentence is empty
                if not sentence:
                    sentenceLists.remove(sentence)

            if len(sentenceLists) == 4:
                sentenceLists.remove(sentenceLists[0])


            # Going through all the tags and checking if there are proper subjects in place
            for tag in processedList:
                if tag[2][0] in ['She','she','hers','Hers','her','Her']:
                    for sentence in sentenceLists:
                        for subject in sentence:
                            if subject[2] == 'female':
                                sawFemale = sawFemale + 1
                                break;
                    if sawFemale == 0:                      # if we do not see any female subjects than error
                        score = score + 1

                elif tag[2][0] in ['he', 'He', 'his','His','him', 'Him']:
                    for sentence in sentenceLists:
                        for subject in sentence:
                            if subject[2] == 'male':
                                sawMale = sawMale + 1
                                break;
                    if sawMale == 0:                        # if we don't see any male subjects then error
                        score = score + 1

                elif tag[2][0] in ['They', 'they', 'Them', 'them', 'their', 'Their']:
                    mscount = 0
                    for sentence in sentenceLists:
                        for subject in sentence:
                            if subject[1] in ['NNS','NNPS']:        # If plural subjects then it is ok
                                plural = 1
                            if subject[1] in ['NNP','NN']:
                                mscount + 1
                    if mscount > 1:                             # if their is more than 1 singular noun then it is plural
                        plural = 1
                    if plural == 0:
                        score = score + 1



        return score





# if __name__ == "__main__":
#     # Input a sentence
#     userSentence = raw_input("Enter a sentence: ")
#
#     # Ensure there are spaces between periods and commas. This may not work so well for elipses,
#     # But those shouldn't really be in academic writing...
#     sCoherence = Coherence()
#     coherenceCount = sCoherence.scoreCoherence(userSentence)
#     print ("Coherence errors:",coherenceCount)
#     print ( "Exited" )


if __name__ == "__main__":

    # Input a sentence
    #userSentence = raw_input("Enter a sentence: ")

    # Ensure there are spaces between periods and commas. This may not work so well for elipses,
    # But those shouldn't really be in academic writing...
    sCoherence = Coherence()

    toc = open("../input/testing/index.csv", 'r')

    # Import the table of contents
    lines = toc.readlines()

    # Skip the title line
    lines.pop(0)

    for line in lines:
         line = line.split(';')
         print(line)
         file = "../input/testing/essays/" + line[0]
         score = line[2]
         print (line[0])

         if "high" in score:
             score = 1
         else:
             score = 0

         essayFile = open(file, 'r')
         essay = essayFile.read()
         count = sCoherence.scoreCoherence(essay)
         print (count)


    print("Exited")





