import nltk


# A feature struct class. Start with desired attributes.
# TO DO: Merge / Union Methods?
class FeatureStruct():
    word = ""
    person = ""
    specialVerb = ""
    tag = ""
    plural = ""
    parseRule = ""
    headVerb = ""
    verbTag = ""
    verb = False
    noun = 0
    svaError = 0
    verbError = 0
    tense = ""

    # Printing the FS for debugging purposes
    def print(self):
        print(self.word)
        print(self.headVerb)

    def build(self, leaf):
        if not type(leaf[0]) is str:
            return

        # General Cases
        self.word = leaf[0].casefold()
        self.tag = leaf._label
        self.noun = 0

        # Information Inferred from Tags
        # NN, NNP, and PRP Are singular except special cases below
        if self.tag in ["NN", "NNP", "PRP"]:
            self.plural = 0
            self.noun = 1
            self.person = 3

        # Mark Plural Nouns
        if self.tag in ["NNS", "NNPS"]:
            self.plural = 1
            self.noun = 1
            self.person = 3

        # Mark Verbs
        if self.tag == "VBP":
            self.person = 1
            self.plural = 0
            self.tense = "present"
            self.headVerb = "VBP"

        if self.tag == "VBZ":
            self.person = 1
            self.tense = "present"
            self.headVerb = "VBZ"

        if self.tag == "VBD":
            self.tense = "past"
            self.headVerb = "VBD"

        if self.tag == "VB":
            self.headVerb = "VB"
            self.tense = "ambiguous"

        if self.tag in ["VB", "VBD", "VBN", "VBG", "VBZ", "VBP"]:
            self.verb = True
            self.verbTag = self.tag

        # Special Cases
        if self.word == "i":
            self.plural = 0;
            self.person = 1;

        if self.word == "you":
            self.plural = 0;
            self.person = 2;

        if self.word in ["we", "they"]:
            self.plural = 1;
            self.person = 2;

        if self.word in ["has", "have", "had"]:
            self.specialVerb = "HAVE"

        if self.word in ["are", "am", "be", "is", "was"]:
            if self.word == "are":
                self.person = 2
            if self.word == "am":
                self.person = 1
            if self.word == "is":
                self.person = 3

            self.specialVerb = "BE"

        return;

    # Merge feature structures as recursion ends. Count SVA and Verb Errors As you Go
    def merge(self, parent, labels):

        fs = FeatureStruct()
        fs.tag = parent._label

        # Merge general data from feature structure
        # Build a string of words analyzed so far
        # Count Subject Verb Agreement and Verb Errors Encountered so far
        for label in labels:
            fs.word += (" " + label.word)
            fs.svaError += label.svaError
            fs.verbError += label.verbError

        # Things that should merge every time
        for label in labels:
            if not label.tense == "":
                fs.tense = label.tense
                break

        # If this is a noun phrase, determine the right plural, person
        if fs.tag == "NP":
            fs.plural = 0
            fs.person = 3
            nounCount = 0
            thirdPerson = True
            theNoun = ""

            for label in labels:
                nounCount += label.noun
                if label.noun == 1:
                    theNoun = label
                if label.plural == 1:
                    fs.plural = 1
                if label.person in [1, 2]:
                    thirdPerson = False
                    fs.person = label.person

            if nounCount == 1:
                fs.plural = theNoun.plural
                fs.person = theNoun.person

            if nounCount > 1:
                fs.plural = 1
                # Handle cases with I, like "you and I" or "the Dog and I"
                if not thirdPerson:
                    fs.person = 2

        # For Verb Phrases identify head verb, plural person
        elif fs.tag == "VP":
            if len(labels) == 1:
                labels[0].svaError = fs.svaError
                labels[0].verbError = fs.verbError
                labels[0].word = fs.word
                fs = labels[0]


            # If there is more than one label, skip over the non verb labels
            for label in labels:
                if label.verb == True:
                    copyLabel = label
                    copyLabel.svaError = fs.svaError
                    copyLabel.verbError = fs.verbError
                    copyLabel.word = fs.word
                    copyLabel.tag = fs.tag
                    copyLabel.tense = fs.tense
                    fs = copyLabel
                    break

            # Check for matching tense
            if not fs.tense == "":
                for label in labels:
                    if not label.tense == "":
                        if not label.tense == fs.tense:
                            fs.verbError += 1

            # fs.verbError += 1
            # Check for verb errors
            if fs.specialVerb == "HAVE":
                for i in range(1, len(labels)):
                    if labels[i-1].specialVerb == "HAVE":
                        for j in range(i, len(labels)):
                            if labels[j].tag == "NP" or labels[j].verbTag == "VBN":
                                return fs;

                        fs.verbError += 1

            if fs.specialVerb == "BE":
                for i in range(1, len(labels)):
                    if labels[i-1].specialVerb == "BE":
                        for j in range(i, len(labels)):
                            if labels[j].tag == "NP" or labels[j].tag == "ADJP" or labels[j].verbTag == "VBG":
                                return fs

                        fs.verbError += 1



        # For S and others Merge what is left
        else:

            np = ""
            vp = ""

            if len(labels) < 1:
                labels[0].tag = parent._tag
                return labels[0]

            # Find the NP and VP in S->NP VP
            for i in range(1,len(labels)):
                if(labels[i-1].tag == "NP" and labels[i].tag in ["VP", "VBP", "VBD", "VBZ", "VBN", "VB", "VBG"]):
                    np = labels[i-1]
                    vp = labels[i]
                    break

            # Check subject verb agreement
            if np == "" or vp == "":
                return fs

            # Handle Be - verbs
            if vp.specialVerb == "BE":
                # I must come with am
                if vp.person == 1:
                    if np.person != 1:
                        fs.svaError += 1

                # Are must come with second person or 3rd person plural
                if vp.person == 2:
                    if np.person == 3 and np.plural == 0:
                        fs.svaError += 1
                    if np.person == 1:
                        fs.svaError += 1

                # 3rd person plural is
                if vp.person == 3:
                    if np.person != 3:
                        fs.svaError += 1
                    elif np.plural == 1:
                        fs.svaError += 1


            # Check that verb matches person agreement
            elif vp.headVerb == "VBZ":
                if not np.person == 3:
                    fs.svaError += 1
                elif np.plural == 1:
                    fs.svaError += 1

            elif vp.headVerb == "VBP":
                if np.person == 3:
                    fs.svaError += 1

            # Handle Head Verbs that shouldn't be there.
            elif vp.headVerb == "":
                fs.verbError += 1

            # Verb Error TO DO
            # Handle Past Participals - eg Have Eaten
            #   - Have Verb preceeds VBN
            # Handle Present Participals - Am eating
            #   - Be Verb preceeds Gerund or Noun

        return fs


class FeatureAnalysis():
    parser = ""
    depParser = ""

    def __init__(self):
        self.parser = nltk.CoreNLPParser(url="http://localhost:9000")
        #self.depParser = nltk.CoreNLPDependencyParser(url="http://localhost:9000")
        return;

    # Comb through text and ensure that periods and commas have a space after them.
    def preProcess(self, text):
        text = text.replace(".", ". ")
        text = text.replace(",", ", ")
        text = text.replace(" i ", " I ")
        text = text.replace("  ", " ")
        return text;

    # Entry point to class. Analyze takes raw text, splits to sentences
    # Parses sentences using stanford core nlp.
    # Sends parse trees out to recursively build feature structures.
    #
    # Returns a feature structure with count of Subject Verb Agreement
    # and Verb Usage Errors
    def analyze(self, essay):

        # Ensure that punctuation has proper spacing
        cleanEssay = self.preProcess(essay)
        sentences = nltk.sent_tokenize(cleanEssay)
        svaCount = 0
        verbCount = 0

        for sentence in sentences:
            #print(sentence)
            (parse, ) = self.parser.raw_parse(sentence)
            #depParse, = self.depParser.raw_parse(sentence)

            #print(depParse.to_conll(4))
            # Now we have a parse tree. We can check subject verb agreement for
            # Every S->NP VP in the tree.
            #parse.pretty_print()
            try:
                fs = self.buildFeature(parse)
                svaCount += fs.svaError
                verbCount += fs.verbError
            except:
                # If the file times out the server then fail 'em
                svaCount = 5
                verbCount = 5
            #print("SVA Error: ", svaCount)
            #print("Verb Error: ", verbCount)
            score = 0

        retValues = []
        """
        for i in [0.3, 0.24, 0.18, 0.12, 0.00]:
            score += 1
            if svaCount / len(sentences) >= i:
                retValues.append(score)
                break;

        score = 0
        for i in [1.5, 1.25, 1.0, 0.75, 0.0]:
            score += 1
            if verbCount / len(sentences) >= i:
                retValues.append(score)
                break;
        """
        retValues.append(svaCount/len(sentences))
        retValues.append(verbCount/len(sentences))

        return retValues

    # Take a parse tree and recursively build feature structures
    def buildFeature(self, tree):

        # Base Case - Recursion has found a leaf
        if type(tree[0]) == str:
            fs = FeatureStruct()
            fs.build(tree)
            return fs

        # Recursively analyze children
        structures = []
        for node in tree:
            structures.append(self.buildFeature(node))

        # Merge feature structures using rules in FeatureStructure
        fs = FeatureStruct()
        fs = fs.merge(tree, structures)

        #fs.print()
        return fs;

if __name__ == "__main__":

    # Input a sentence
    userSentence = input("Enter a sentence: ")

    # Ensure there are spaces between periods and commas. This may not work so well for elipses,
    # But those shouldn't really be in academic writing...
    feature = FeatureAnalysis()
    fs = feature.analyze(userSentence)
    print("Errors: ", fs)
    print("goodbye")

