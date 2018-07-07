#from __future__ import print_function
import numpy as np
import statsmodels.api as sm
import pandas

# Lambda functions for working with data frame

def translate(x):
    if x == "high":
        return 1;
    return 0;

def compositeScore(x):
    if model.predict(params=params, exog=x.values, linear=True) > 0:
        return 1
    return 0

def truePositive(x):
    if x['human_score'] == 1 and x['computer_score'] == 1:
        return 1
    return 0

def falsePositive(x):
    if x['human_score'] == 0 and x['computer_score'] == 1:
        return 1
    return 0

def falseNegative(x):
    if x['human_score'] == 1 and x['computer_score'] == 0:
        return 1
    return 0;

scores = pandas.read_csv("../input/training/results2.txt", ";", index_col=0)
scores = scores.drop(["file_name"], axis=1)


results = pandas.read_csv("../input/training/index.csv", ";")
results = results['grade']
results = results.apply(translate)

depVar = results.values
indVar = scores.values


model = sm.Probit(depVar, indVar)
result = model.fit()

params = result.params

print(params)

# Calculate Fit Statistics

scores['computer_score'] = scores.apply(compositeScore, axis=1)
scores['human_score'] = results
scores['true_positive'] = scores.apply(truePositive, axis=1)
scores['false_positive'] = scores.apply(falsePositive, axis=1)
scores['false_negative'] = scores.apply(falseNegative, axis=1)

tp = scores['true_positive'].sum()
fp = scores['false_positive'].sum()
fn = scores['false_negative'].sum()

precision = tp / (tp + fp)
recall = tp / (tp + fn)

print("Precision: ", precision)
print("Recall: ", recall)


print("Goodbye")

