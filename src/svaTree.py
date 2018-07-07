import nltk

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

class featureStruct():
    word = ""
    person = ""
    specialVerb = ""
    tag = ""
    plural = ""


class SubjVerbAgreement():

    parser = ""
    svaError = 0
    verbError = 0


    def __init__(self):
        self.parser = nltk.CoreNLPParser(url="http://localhost:9000")
        self.svaError = 0
        self.verbError = 0
        return;

    # Comb through text and ensure that periods and commas have a space after them.
    def preProcess(self, text):
        text = text.replace(".", ". ")
        text = text.replace(",", ", ")
        text = text.replace(" i ", " I ")
        text = text.replace("  ", " ")
        return text;


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

    def rec_agreement(self, tree):
        # End recursion at leaf node

        verb = featureStruct()
        noun = featureStruct()
        errorCount = 0

        if type(tree[0]) is str:
            return 0;


        for node in tree:
            if node._label == "NP":
                noun = self.getNounAgreement(node)

            elif node._label == "VP":
                verb = self.getVerbAgreement(node)

            else:
                self.rec_agreement(node)

        if verb == "":
            return;

        if verb.tag in ["VB", "VBD", "MD"]:
            return;

        if verb.specialVerb == "BE":
            if (noun.tag == "I" and verb.word == "am") or noun.person != 1 and verb.word == "are" :
                return;

        if verb == "VBP":
            if noun.tag in ["2NN", "I", "2NNS"]:
                return;

        if verb == "VBZ":
            if noun.tag == "NN":
                return;

        if noun.tag == "":
            return;

        if verb.tag == "":
            return;

        #tree.pretty_print()
        self.svaError += 1
        return;

    def getNounAgreement(self, tree):

        labels = []
        count = 0

        # Base case - Handle PRPs otherwise return whatever.
        if type(tree[0]) is str:
            word = tree[0].casefold()
            fs = featureStruct()
            fs.word = word
            fs.tag = tree._label
            fs.person = 3

            if word == "i":
                fs.person = 1
                fs.plural = 0
                fs.tag = "I"

            elif word == "you":
                fs.person = 2
                fs.plural = 0

            elif word in ["we", "they"]:
                fs.person = 2
                fs.plural = 1

            elif tree._label == "PRP":
                fs.person = 3
                fs.plural = 0

            return fs

        for node in tree:
            labels.append(self.getNounAgreement(node))

        if len(labels) == 1:
            return labels[0]

        for label in labels:
            if label.tag in ["NNS", "NNPS"]:
                return label

            if label.tag in ["NNP", "NN", "I"]:
                count += 1

        if count == 1:
            return labels[0]

        fs = featureStruct()
        for label in labels:
            if "NN" in label.tag:
                fs.word += label.word

        fs.tag = "NNS"
        fs.plural = 1

        return fs


    def getVerbAgreement(self,tree):

        labels = []
        countError = 0

        if type(tree[0]) is str:
            word = tree[0].casefold()
            fs = featureStruct()
            fs.word = word
            fs.tag = tree._label

            if word == "am":
                fs.specialVerb = "BE"
                return fs

            if tree[0] == "are":
                fs.specialVerb = "BE"
                return fs

            if tree[0] in ["has", "have", "had"]:
                fs.specialVerb = "HAVE"
                return fs

            return fs

        for node in tree:
            if node._label == "S":
                 self.rec_agreement(node)
            else:
                verb = self.getVerbAgreement(node)
                labels.append(verb)

        try:
            # Check for modal errors. Verbs following modal should be root
            if labels[0] == "MD":
                if len(labels) > 1:
                    if labels[1].tag in ["VBZ", "VBP", "AM", "VBD"]:
                        self.verbError += 1
                        return labels[1]

            # Past participal Errors
            if len(labels) > 1:
                if labels[1].tag == "VBN":
                    if labels[0].tag is "RB":
                        return labels[1]
                    elif not labels[0].specialVerb == "HAVE":
                        self.verbError += 1

            return labels[0]

        except:

            return ""

    def treeAgreement(self, essay):

        sentenceCount = 0
        errorCount = 0
        self.svaError = 0
        self.verbError = 0
        # Ensure that punctuation has proper spacing
        cleanEssay = self.preProcess(essay)
        sentences = nltk.sent_tokenize(cleanEssay)

        for sentence in sentences:
            #print(sentence)
            (parse, ) = self.parser.raw_parse(sentence)
            # Now we have a parse tree. We can check subject verb agreement for
            # Every S->NP VP in the tree.
            #parse.pretty_print()
            self.rec_agreement(parse)
            #print("svaError: ", self.svaError)
            #print("verbError: ", self.verbError)

        return self.svaError / len(sentences)


if __name__ == "__main__":

    # Input a sentence
    userSentence = input("Enter a sentence: ")

    # Ensure there are spaces between periods and commas. This may not work so well for elipses,
    # But those shouldn't really be in academic writing...

    sva = SubjVerbAgreement()
    print("Errors: ", sva.treeAgreement(userSentence))
    #sva.scoreAgreement(userSentence)
    print("goodbye")




