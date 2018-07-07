import nltk
from nltk import wordnet
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from scipy import spatial
import numpy
import pandas

# Part d.ii - Topic Coherence
#
# Reference:
# Crossley and McNamara, "Text Coherence and Judgements of Essay Quality: Models of Quality and Coherence" 2011
# http://alsl.gsu.edu/files/2014/03/Text-coherence-and-judgments-of-essay-quality-Models-of-quality-and-coherence.pdf
#
# Strategy: Create a measure of similarity between words in the essay and the essay prompt. Use a thesaurus-based
#           algorithm.
#           Utilize the Similarity functionality of WordNet
#           1.  Measure the similarity of the entire essay with the prompt
#           2.  Measure the similarity of the essay with itself via a sliding window
#

class Topic_Coherence():

    def __init__(self):
        return;

    def maxSimilarity(self, synset1, synset2):
        min = 5.0
        for syn in synset1:
            for syn2 in synset2:
                try:
                    sim = syn.lch_similarity(syn2)
                except:
                    continue

                try:
                    if sim < min:
                        min = sim
                except:
                    continue;
        return min;

    def similarityMatrix(self, dict1, dict2):
        matrix = []
        for e in dict1:
            row = []
            for f in dict2:
                if e == f:
                    row.append(0)
                else:
                    row.append(self.maxSimilarity(dict1[e], dict2[f]))
            matrix.append(row)
        return matrix

    def score_topic_coherence(self, prompt, essay):
        # Build a list of relevant words to check for coherence
        keyWordsCount = {}
        essayWordsCount = {}
        keyWordsSyn = {}
        essayWordsSyn = {}

        prompt = nltk.word_tokenize(prompt)
        prompt = nltk.pos_tag(prompt)
        essay = nltk.word_tokenize(essay)
        essay = nltk.pos_tag(essay)

        #print(prompt)
        lemma = WordNetLemmatizer()

        for word in prompt:
            # For words in the prompt, also collect words from the synset
            if word[1] in ["NNS", "NNP", "NN", "NNPS", "JJR", "JJ"]:
                stripped = lemma.lemmatize(word[0]).casefold()
                if not stripped in keyWordsCount:
                    # Count the first occurence of the word
                    keyWordsCount[stripped] = 1

                    # Record the synset for the word
                    keyWordsSyn[stripped] = wn.synsets(stripped)
                else:
                    keyWordsCount[stripped] = 1 + keyWordsCount[stripped]

        for word in essay:
            if word[1] in ["NNS", "NNP", "NN", "NNPS", "JJR", "JJ"]:
                stripped = lemma.lemmatize(word[0]).casefold()
                if not stripped in essayWordsCount:
                    # Count the first occurrence of the word
                    essayWordsCount[stripped] = 1
                    # Record the synset for the word
                    essayWordsSyn[stripped] = wn.synsets(stripped)
                else:
                    essayWordsCount[stripped] = 1 + essayWordsCount[stripped]

        # From the dictionaries build arrays of counts
        qCount = []
        aCount = []

        for word in essayWordsCount:
            if not word in keyWordsCount:
                qCount.append(0)
            else:
                qCount.append(keyWordsCount[word])
            aCount.append(essayWordsCount[word])

        #print(qCount)
        #print(aCount)

        matrix = self.similarityMatrix(keyWordsSyn, essayWordsSyn)

        # print(matrix)
        # Find a measure of similarity:
        # Cosine Similarity doesn't show a huge gap between high and low essays
        #
        # Percentage shows a large gap, but this seems to be more a measure of word count.
        #

        #cosineSimilarity = 1 - spatial.distance.cosine(qCount, aCount)

        percentage = sum(qCount) / sum(aCount)

        distanceMean = numpy.mean(matrix)
        #print(distanceMean)

        return distanceMean / sum(aCount)


if __name__ == "__main__":

    # We will require the prompt and the essay for this module. Given a filename, import the
    # Prompt and the essay and pass to the module.

    filename = input("Enter a file to grade for topic coherence: ")

    try:
        file = open("../input/testing/essays/"+filename)
        prompts = pandas.read_csv("../input/testing/index.csv", ";")

    except:
        print("Invalid filename - Goodbye")
        quit()

    # Read the essay file
    essay = file.read()

    # Isolate the question of the prompt for the specific filename
    prompt = prompts.loc[prompts['filename'] == filename]['prompt'].max()
    prompt = nltk.sent_tokenize(prompt)[1]

    score = Topic_Coherence()
    score.score_topic_coherence(prompt, essay)
