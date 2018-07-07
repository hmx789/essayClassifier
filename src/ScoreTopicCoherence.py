import matplotlib.pyplot as plt1
import nltk
import pandas

from src.topic_coherence import Topic_Coherence




if __name__ == "__main__":

    tpc = Topic_Coherence()

    # Import the table of contents
    toc = open("../input/testing/index.csv", 'r')

    # Import the table of contents
    lines = toc.readlines()

    #  Import the previous results dataframe
    result = pandas.read_csv("../input/training/results.txt", ";")
    result = result.drop("relevance", axis=1)
    scores = []

    # Skip the title line
    lines.pop(0)

    for line in lines:
        line = line.split(';')
        print(line)
        file = "../input/testing/essays/" + line[0]
        score = line[2]
        prompt = line[1]

        if "high"  in score:
            score = 1
        else:
            score = 0

        essayFile = open(file, 'r')
        essay = essayFile.read()

        count = tpc.score_topic_coherence(prompt, essay)
        scores.append(count)


        plt1.scatter(count, score)

    plt1.show()
    result['relevance'] = pandas.Series(scores)
    result.to_csv("../input/training/results2.txt", ";", index=False, header=True)