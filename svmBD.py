from svm import *
from nltk.probability import *
import nltk
import sys
import string
import re
import operator

"""

errors = 0
for i in range(size):
    prediction = model.predict(samples[i]) #classifica
    d = model.predict_values(samples[i])
    print "era pra dar: ",
    print labels[i]
    print "predicao: ",
    print prediction
    probability = model.predict_probability #diz probabilidade de estar certo
    if (labels[i] != prediction):                   #verifica se errou ou acertou
        errors = errors + 1
print "##########################################"
print " kernel %s: error rate = %d / %d" % (kname[param.kernel_type], errors, size)
print "##########################################"

"""



class QueueClassifier(object):
    """Trains a classifier using the docs from the context graph, and uses that to classify new docs into Queues"""
    def __init__(self,list_docs_base=None):
        #list_docs_base = context_graph_docs
        str_stop_words = "a about above according accordingly across actual added after against ahead all almost alone along already also although among amongst an and and-or and/or anon another any anyone apparently are arise as asaside at award away be became because become becomes been before behind being below best better between beyond birthday both briefly but by came can cannot certain certainly come comes coming completely concerning consider considered considering consisting could de department der despite did different discussion do does doesn't doing done down dr du due during each either else enough especially et etc ever every few following for forward found from further gave get gets give given gives giving gone got had hardly has have having here his honor how however i if immediately in inside instead into is it items its itself just keep kept largely let lets like little look looks made mainly make makes making many meet meets might more most mostly much mug must my near nearly necessarily next no none nor nos not noted now obtain obtained of off often on only onto or other ought our out outside over overall owing particularly past per perhaps please possibly predominantly present previously probably prompt promptly pt put quite rather ready really regarding regardless relatively reprinted respectively said same seem seen several shall should show showed shown shows similarly since slightly so so-called some sometime sometimes somewhat soon spp strongly studies study substantially successfully such take taken takes taking than that the their theirs them then there therefore therefrom these they this those though through throughout thus to together too toward towards under undergoing unless until up upon upward used usefully using usually various versus very via vol vols vs was way ways we were what whats when where whether which while whither who whom whos whose why widely will with within without would you"
        self.set_stop_words = set(str_stop_words.split(' '))
        str_docs_base = ""
        icount = 0


        for layer in list_docs_base:
            jcount = 0
            for doc in layer:
                list_docs_base[icount][jcount] = self.cleanString(list_docs_base[icount][jcount])
                jcount = jcount + 1
            str_docs_base = str_docs_base+' '+' '.join(list_docs_base[icount])
            icount = icount + 1
        self.vector_vocabulary = []
        tuple_dic_vector = self.tokenize(str_docs_base)
        dic_vocabulary = tuple_dic_vector[0]
        self.dic_vocabulary = dic_vocabulary
        self.vector_vocabulary = tuple_dic_vector[1]
        self.labels = []
        self.samples = []
        count_layers = 0
        for layer in list_docs_base:
            for doc in layer:
                vector_tf = self.discretize(dic_vocabulary,doc)
                self.labels.append(count_layers)
                self.samples.append(vector_tf)
                #set_doc_terms.clear()
                for term in self.vector_vocabulary:
                    dic_vocabulary[term] = 0
            count_layers = count_layers + 1

        self.model = self.training(self.labels,self.samples)
        #print self.labels
        #print self.samples



    def training(self,labels,samples):
        """treina e salva o modelo"""
        #model = svm_model('test.model') carrega a base ja treinada
        problem = svm_problem(labels,samples) # Aqui ja passou a base de treino
        size = len(samples)

        #parametros do treino
        kernels = [LINEAR, POLY, RBF]
        kname = ['linear','polynomial','rbf']

        param = svm_parameter(C = 10, probability=1)#,nr_weight = 2,weight_label = [1,0],weight = [10,1])

        param.kernel_type = kernels[0]; #kernel linear
        model = svm_model(problem,param) #criou o modelo
        model.save('model_'+kname[param.kernel_type])
        return model

    def discretize(self,dic_vocabulary=None,doc=None):
        """------------------------faz a discretizacao de cada documento no formato de um vetor de TFs dos termos----------------------"""
        set_doc_terms = set()
        tuples_doc_terms = []
        vector_tf = []
        doc_tokenized = nltk.word_tokenize(doc)
        icount = 0
        for token in doc_tokenized:
            doc_tokenized[icount] = token.lower()
            icount = icount + 1
        for token in doc_tokenized:
            if (token in set_doc_terms)==False and (token in self.set_stop_words)==False:
                tuples_doc_terms.append((token,doc_tokenized.count(token)))
                set_doc_terms.add(token)
        tuples_doc_terms = sorted(tuples_doc_terms,key=operator.itemgetter(1),reverse=True)
        for ituple in range(4,len(tuples_doc_terms)):
            tuples_doc_terms[ituple] = (tuples_doc_terms[ituple][0],0)
        for tuple in tuples_doc_terms:
            dic_vocabulary[tuple[0]] = tuple[1]
        for term in self.vector_vocabulary:
            vector_tf.append(dic_vocabulary[term])
        return vector_tf

    def tokenize(self,str_docs_base=None):
        """-------------------tokeniza a string formada pela concatenacao de todos os documentos, para formar o vocabulario----------------------"""
        tokenized = nltk.word_tokenize(str_docs_base)
        icount = 0
        for token in tokenized:
            tokenized[icount] = token.lower()
            icount = icount + 1

        list_vocabulary = []
        for token in tokenized:
            if (token in self.set_stop_words)==False:
                list_vocabulary.append(token)
        set_vocabulary = set(list_vocabulary)


        dic_vocabulary = {}
        vector_vocabulary = []
        for term in set_vocabulary:
            dic_vocabulary[term] = 0
            vector_vocabulary.append(term)
        vector_vocabulary.sort()
        tuple_dic_vector = (dic_vocabulary,vector_vocabulary)
        return tuple_dic_vector

    def cleanString(self,document=None):
        """retira todos os caracteres de pontuacao e numeros"""
        #pode ser que o metodo string.maketrans juntamente com o string.translate seja lento, entao deixo as seguintes opcoes que possuem o mesmo efeito
        #exclude = set(string.punctuation)
        #regex = re.compile('[%s]' % re.escape(string.punctuation))
        #text = regex.sub('', s)
        table = string.maketrans("","")
        #retira os caracteres de pontuacao efetivamente
        document = document.translate(table, string.punctuation)
        #retira os numeros
        document = ''.join([letter for letter in document if not letter.isdigit()])
        return document

    def predictQueue(self,doc=None):
        """from a doc(string), clean, discretize and predicts which queue it belongs"""
        vector_tf = self.discretize(self.dic_vocabulary,doc)
        #prediction = self.model.predict(vector_tf)
        #return prediction
        prediction_label, prediction_probabilities = self.model.predict_probability(vector_tf)
        prediction = (prediction_label,prediction_probabilities[prediction_label])
        return prediction

if __name__ == "__main__":
    """-----------------------------------------recebe a lista de textos---------------------------------------------"""
    list_docs_base = [["@AntonioPizzonia: Bonjour Paris! Junt landed in Paris :) going to Monaco next. Still got a flight to Nice..",
                     "@waynesutton: I everyone receives their google wave account tomorrow. If so I can be reached on wave at:",
                     "@moonfrye: Question of the night. If you had a crystal ball and could ask it one question, what would it be?"],
                    ["@NelsonPiquet: Thank you guys or everything. You are amazing... Talk to you later! Take care!",
                     "@moonfrye: We are so close to the finish line! You guys are the best, This T.O. is tough. GO #TeamSoleil",
                     "@NelsonPiquet: And remember: We have a new promo when we reach 100.000: A small helmet, signed!"],
                    ["@tgosingtian: RT @ANCALERTS: Stay tuned for PAGASA's press conference on Typhoon Pepeng. ANC will air that live at 11am today.",
                     "@Schwarzenegger: http://twitpic.com/jsfsv - Talking with Gov Kulongoski during a break. He is a huge baseball fan!",
                     "@moonfrye: OH NO!!! Terrell Owens has the lead. Help me!!! It is twitter war."]]
    classifier = QueueClassifier(list_docs_base)
    print 'prediction: ', classifier.predictQueue(list_docs_base[2][2])

