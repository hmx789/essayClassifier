import sys
sys.path.insert(0, './')
from spelling import Spelling
from subjectVerbAgreement import SubjVerbAgreement as sva
from sCount import SentenceCount
from svaTree import SubjVerbAgreement
from FeatureAnalysis import FeatureAnalysis
from SentenceStructure import SentenceStructure
from Coherence import Coherence
from topic_coherence import Topic_Coherence

import statsmodels.api as sm
import pandas
import numpy
import nltk
import random

# Mapping functions to translate percent scores to specified output scores

def spellMap(pcError):
    if pcError > 5.0:
        return 4;
    elif pcError > 4.0:
        return 3;
    elif pcError > 3.0:
        return 3;
    elif pcError > 2.0:
        return 2;
    elif pcError > 1.0:
        return 1
    else:
        return 0;

def countMap(clauseCount):
    if clauseCount < 35:
        result = 0
    elif (clauseCount < 41):
        result = 1
    elif (clauseCount < 47):
        result = 2
    elif (clauseCount < 53):
        result = 3
    elif (clauseCount < 60):
        result = 4
    else:
        result = 5

    return result


def svaMap(x):
    score = 0
    for i in [0.3, 0.24, 0.18, 0.12, 0.00]:
        score += 1
        if x >= i:
            break
    return score

def vbMap(x):
    score = 0
    for i in [1.5, 1.25, 1.0, 0.75, 0.0]:
        score += 1
        if x >= i:
            break;
    return score

def wellMap(x):
    score = 0
    for i in [0.5, 0.4, 0.3, 0.2, 0.1]:
        score += 1
        if x >= i:
            break;
    return score

def relMap(x):
    score = 0
    for i in [0.9, 1.025, 1.15, 1.275, 1.4]:
        score += 1
        if x <= i:
            break;
    return score

def sumRow(x):
    vals = x.drop(["file_name", "final_score"]).values
    sum = 0
    for val in vals:
        sum += float(val)

    return int(sum)

def translate(x):
    if x == "high":
        return 1;
    return 0;


# Main function for calling essay scorer modules begins here

if __name__ == "__main__":

    # Download required nltk corpora
    try:
        nltk.download('words')
    except:
        print("This program requires nltk and its words corpus to run.")

    # Import the table of contents
    toc = open("../input/testing/index.csv", 'r')

    # Import the table of contents
    lines = toc.readlines()

    # Skip the title line
    lines.pop(0)

    # Get the score from the regression model. This is hard coded from previously done
    # Run the regression model on cached data
    scores = pandas.read_csv("../input/training/results.txt", ";", index_col=0)
    scores = scores.drop(["file_name"], axis=1)

    results = pandas.read_csv("../input/training/index.csv", ";")
    results = results['grade']
    results = results.apply(translate)

    depVar = results.values
    indVar = scores.values

    model = sm.Probit(depVar, indVar)
    result = model.fit()

    params = result.params
    print("Parameters: ", params)
    # Build a list of results
    results = []

    for line in lines:
        line = line.split(';')
        filename = line[0]

        try:
            file = open("../input/testing/essays/"+filename)

        except:
            print(filename + " not found. ")
            continue

        # We can declare classes to run our tests here
        # and then combine the score

        # Read the essay from file, let testers tokenize as necessary.
        essay = file.read()

        spell = Spelling()
        stc = SentenceCount()
        feat = FeatureAnalysis()
        struct = SentenceStructure()
        co = Coherence()
        tc = Topic_Coherence()

        spellingScore = spell.spellCheck(essay)
        sentenceScore = stc.scoreSentenceCount(essay)
        sentenceStruct = struct.scoreFormCounts(essay)

        verbScores = feat.analyze(essay)
        svaScore = verbScores[0]
        verbScore = verbScores[1]
        coherence = co.scoreCoherence(essay);
        relevance = tc.score_topic_coherence(line[1], essay)

        # Add Coherence and Relevance Later
        results.append([filename, spellingScore, sentenceScore, svaScore, verbScore, sentenceStruct, coherence, relevance])


    # Add coherence and relevance later
    resultsdf = pandas.DataFrame(results, columns=["file_name", "spelling", "sentence_count", "subject_verb_agreement",
                                        "verb_usage", "well_formedness", "coherence", "relevance"])

    #print(resultsdf)
    #process = resultsdf.drop("file_name", axis=1)


    resultsdf['final_score'] = resultsdf.apply(lambda x: "High" if model.predict(params=params,
                                                                                 exog=x.drop("file_name").values,
                                                                                 linear=True) > 0
                                               else "Low", axis=1)
    
    # Translate scores to 1 - 5
    
    resultsdf['spelling'] = resultsdf['spelling'].apply(spellMap)
    resultsdf['sentence_count'] = resultsdf['sentence_count'].apply(countMap)
    resultsdf['subject_verb_agreement'] = resultsdf['subject_verb_agreement'].apply(svaMap)
    resultsdf['verb_usage'] = resultsdf['verb_usage'].apply(vbMap)
    resultsdf['well_formedness'] = resultsdf['well_formedness'].apply(wellMap)
    resultsdf['coherence'] = resultsdf['coherence'].apply(lambda x: 1 if x >= 4 else 5 - x )
    resultsdf['relevance'] = resultsdf['relevance'].apply(relMap)

    # Insert Relevance


    # Sum the 1 - 5 Scores
    resultsdf['sum'] = resultsdf.apply(sumRow, axis=1)
    sum = resultsdf['sum']
    resultsdf = resultsdf.drop("sum", axis=1)
    resultsdf.insert(8, 'sum', sum)


    resultsdf.to_csv("../output/results.txt", ";", index=False, header=True)

    # Clean up the file
