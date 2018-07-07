import matplotlib.pyplot as plt
import nltk

from src.spelling import Spelling

#
#  ScoreSpelling plots all spelling scores against
#  low / high values for essays.
#  It appears that both low and high value essays have
#  Spelling errors of up to 5% misspelled. However,
#  only low scored essays exceed 5%.
#



if __name__ == "__main__":

    spellScores = []

    # Import the table of contents
    toc = open("../input/testing/index.csv", 'r')

    # Import the table of contents
    lines = toc.readlines()

    # Skip the title line
    lines.pop(0)

    for line in lines:
        line = line.split(';')
        file = "../input/testing/essays/" + line[0]
        score = line[2]

        if "high"  in score:
            score = 1
        else:
            score = 0

        essayFile = open(file, 'r')
        essay = essayFile.read()

        spell = Spelling()
        plt.scatter(spell.spellCheck(essay), score)

    plt.show()