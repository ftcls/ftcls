import numpy as np
from sklearn.svm import SVC
import MeCab
import pickle
from sklearn.svm import LinearSVC
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import pandas as pd
from sklearn.linear_model import LogisticRegressionCV
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectFromModel
from imblearn.under_sampling import RandomUnderSampler
import csv
from sklearn.feature_selection import SelectPercentile, f_regression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import sklearn.preprocessing as sp
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import gensim
from sklearn.naive_bayes import  MultinomialNB
from sklearn.model_selection import GridSearchCV
import cloudpickle


class fasttext_vectorizer():
    def __init__(self,fasttext):
        self.fasttext=fasttext

    def fasttext_vectorizer_pre(self,sentence):
        bag_of_centroids = np.zeros(300)
        for word in sentence:
            try:
                temp = self.fasttext[word]
            except:
                continue
            bag_of_centroids += temp  
        bag_of_centroids =  bag_of_centroids / len(sentence)
        return bag_of_centroids

    def transform(self,sentences):
        vector=[self.fasttext_vectorizer_pre(text) for text in sentences]
        return vector

class preprocessing():
    def __init__(self,Proper=False):
        self.Proper=Proper

    def process(self,text):
        tagger= MeCab.Tagger('-Ochasen')     
        result=tagger.parseToNode(text)
        toke=[]
        while result:                
            pos=result.feature.split(',')[0]
            pos2=result.feature.split(',')[1]
            if ((pos=="形容詞" or pos=="名詞" or pos=="動詞"or pos=="副詞") and pos2!="数" and (pos2!="固有名詞" or self.Proper)):
                toke.append(result.surface)      
            result = result.next
        preprocessed_text=" ".join(toke)
        return preprocessed_text
        
class vectorize_classifier():

    def __init__(self):
        self.preprocessing=preprocessing()
        self.parameters ={}
        self.sampler = RandomUnderSampler(random_state=0)              
        self.label=["__label__1","__label__2"]
        self.model=None
        self.vectorizer=None
        self.gscv=None    
    
    def model_fit(self,texts,targets,vectorizer_fit=True,preproces=True):
        if preproces:
            processed_texts=[self.preprocessing.process(text) for text in texts]
        else:
            processed_texts=texts
        target_vector=[1 if target==self.label[1] else -1 for target in targets]
        if vectorizer_fit:
            vector=self.vectorizer.fit_transform(processed_texts)
        else:
            vector=self.vectorizer.transform(processed_texts)
        self.model.fit(vector,target_vector)
    

    def model_fit_grid(self,texts,targets,vectorizer_fit=True,preproces=True):     
        if preproces:
            processed_texts=[self.preprocessing.process(text) for text in texts]
        else:
            processed_texts=texts
        target_vector=[1 if target==self.label[1] else -1 for target in targets]
        if vectorizer_fit:
            vector=self.vectorizer.fit_transform(processed_texts)
        else:
            vector=self.vectorizer.transform(processed_texts)
        self.gscv.fit(vector,target_vector)
        self.model=self.gscv.best_estimator_

    def predict(self,texts):
        processed_texts=[self.preprocessing.process(text) for text in texts]
        vector=self.vectorizer.transform(processed_texts)
        ans=self.model.predict(vector)
        return ans
    
    def next_text_pool(self,pool):
        processed_texts=[self.preprocessing.process(text) for text in pool]
        vector=self.vectorizer.transform(processed_texts)
        probs=self.model.predict_proba(vector)
        p=[abs(prob[1]-prob[0]) for prob in probs]
        index=np.argmin(np.array(p))
        return pool[index],probs[index]

    def next_text_stream(self,pool,P):
        for text in pool:           
            processed_text=self.preprocessing.process(text)
            vector=self.vectorizer.transform([processed_text])
            probs=self.model.predict_proba(vector)
            print(probs)
            if abs(probs[:,0]-probs[:,1])<P:
                yield text,probs

    def evaluate(self,test_texts,test_targets):
        processed_texts=[self.preprocessing.process(text) for text in test_texts]
        test_target=[1 if test_target==self.label[1] else -1 for test_target in test_targets]
        vector=self.vectorizer.transform(processed_texts)
        Y_pred=self.model.predict(vector)
        print('confusion matrix = \n', confusion_matrix(y_true=test_target, y_pred=Y_pred))
        self.accuracy=accuracy_score(y_true=test_target, y_pred=Y_pred)
        self.precision=precision_score(y_true=test_target, y_pred=Y_pred)
        self.recall=recall_score(y_true=test_target, y_pred=Y_pred)
        self.f1=f1_score(y_true=test_target, y_pred=Y_pred)

    def prob(self,pool):
        processed_texts=[self.preprocessing.process(text) for text in pool]
        vector=self.vectorizer.transform(processed_texts)
        probs=self.model.predict_proba(vector)
        return probs

    def miss(self,text,targets):
        ans=self.predict(text)
        target=[1 if target==self.label[1] else -1 for target in targets]
        for i in range(len(text)):
            if target[i]!=ans[i]:
                print(target[i],text[i])

class count_logistic(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.model=LogisticRegressionCV(class_weight="balanced",n_jobs=-1)
        self.vectorizer=CountVectorizer(decode_error="ignore")

class count_logistic3(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.model=LogisticRegressionCV(class_weight="balanced",scoring="f1",n_jobs=-1)
        self.vectorizer=CountVectorizer(decode_error="ignore")

class count_GB(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters= {
    "loss":["deviance"],
    "learning_rate": [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2],
    "min_samples_split": np.linspace(0.1, 0.5, 12),
    "min_samples_leaf": np.linspace(0.1, 0.5, 12),
    "max_depth":[3,5,8],
    "max_features":["log2","sqrt"],
    "criterion": ["friedman_mse",  "mae"],
    "subsample":[0.5, 0.618, 0.8, 0.85, 0.9, 0.95, 1.0],
    "n_estimators":[10]
    }
        self.model=GradientBoostingClassifier()
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2)

class tfidf_logistic(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.model=LogisticRegressionCV(class_weight="balanced",scoring="f1",n_jobs=-1)
        self.vectorizer=TfidfVectorizer(decode_error="ignore")

    def model_fit(self,texts,targets,vectorizer_fit=True,preproces=True):
        if preproces:
            processed_texts=[self.preprocessing.process(text) for text in texts]
        else:
            processed_texts=texts
        target_vector=[1 if target==self.label[1] else -1 for target in targets]
        if vectorizer_fit:
            vector=self.vectorizer.fit_transform(processed_texts)
            vector=np.linalg.norm(vector)
        else:
            vector=self.vectorizer.transform(processed_texts)
        self.model.fit(vector,target_vector)

class count_logistic2(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters={"C":[0.01,0.1,1,10,50,100,1000,10000,50000],"l1_ratio":[0,0.2,0.4,0.6,0.8,1.0]}
        self.model=LogisticRegression(class_weight="balanced",n_jobs=-1)
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2, return_train_score=True)

    def model_fit_grid(self,texts,targets,vectorizer_fit=True,preproces=True):     
        if preproces:
            processed_texts=[self.preprocessing.process(text) for text in texts]
        else:
            processed_texts=texts
        target_vector=[1 if target==self.label[1] else -1 for target in targets]
        if vectorizer_fit:
            vector=self.vectorizer.fit_transform(processed_texts)
        else:
            vector=self.vectorizer.transform(processed_texts)
        self.gscv.fit(vector,target_vector)
        print(self.gscv.best_score_)
        self.model=self.gscv.best_estimator_ 

class count_logistic4(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()        
        self.parameters={"l1_ratios":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]}
        self.model=LogisticRegressionCV(class_weight="balanced",n_jobs=-1)
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, verbose=2)

    def model_fit_grid(self,texts,targets,vectorizer_fit=True,preproces=True):     
        if preproces:
            processed_texts=[self.preprocessing.process(text) for text in texts]
        else:
            processed_texts=texts
        target_vector=[1 if target==self.label[1] else -1 for target in targets]
        if vectorizer_fit:
            vector=self.vectorizer.fit_transform(processed_texts)
        else:
            vector=self.vectorizer.transform(processed_texts)
        self.gscv.fit(vector,target_vector)
        self.model=self.gscv.best_estimator_

class count_NB(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters={"alpha":np.logspace(-5, 0, 6)}
        self.model=MultinomialNB()
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2)

class fasttext_logistic(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.fasttext = gensim.models.KeyedVectors.load_word2vec_format('model.vec', binary=False)     
        self.model=LogisticRegressionCV()
        self.vectorizer=fasttext_vectorizer(self.fasttext)
        

class count_randomforest(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters=={"max_depth":[3, 5, 10, 15, 20, 25, 30, 40, 50, 100]
        ,"min_samples_split":[3, 5, 10]
        ,"max_features":[5, 10, 15, 20,100,200,500,800]
        ,'random_state'      : [250]
        ,"n_estimators":[5, 10, 20, 30, 50, 100, 300]}
        self.model=RandomForestClassifier()
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2)

class count_svm(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters={"C":[0.01,0.1,1,10,50,100,1000,10000,50000]}
        self.model=LinearSVC()
        self.vectorizer=CountVectorizer(decode_error="ignore")
        self.gscv = GridSearchCV(self.model, self.parameters, cv=3, verbose=2,)

class fasttext_svm(vectorize_classifier):
    def __init__(self):
        self.preprocessing=preprocessing()
        self.parameters={"C":[0.01,0.1,1,10,100],
                        "gamma":[0.01,0.1,0.5,1,2,3,10]}
        self.fasttext = gensim.models.KeyedVectors.load_word2vec_format('model.vec', binary=False)
        super().__init__()
        self.model=SVC(kernel='rbf')
        self.vectorizer=fasttext_vectorizer(self.fasttext)
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2)

class fasttext_linearsvm(vectorize_classifier):
    def __init__(self):
        super().__init__()
        self.preprocessing=preprocessing()
        self.parameters={"C":[0.01,0.1,1,10,100]}
        self.fasttext = gensim.models.KeyedVectors.load_word2vec_format('model.vec', binary=False)      
        self.model=LinearSVC()
        self.vectorizer=fasttext_vectorizer(self.fasttext)
        self.gscv = GridSearchCV(self.model, self.parameters, cv=4, verbose=2)


