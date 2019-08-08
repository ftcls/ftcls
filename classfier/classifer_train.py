from sklearn import svm
from sklearn.svm import SVC
from gensim import corpora, models, similarities
import copy
import sys
import time
import MeCab
import os
from sklearn.decomposition import TruncatedSVD
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import multiprocessing as mp
import pandas as pd
import GPy, GPyOpt
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.preprocessing import Imputer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectFromModel
from imblearn.under_sampling import RandomUnderSampler
import csv
import pickle
from sklearn.datasets import load_boston
from sklearn.feature_selection import SelectPercentile, f_regression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import sklearn.preprocessing as sp
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class model_for_opt():
    def __init__(self,vector,target,num_of_split=10,model="svm",way_of_split="skf"):
        self.vector=vector
        self.target=target
        self.num_of_splits=num_of_split
        self.way_of_split=way_of_split
        self.model=model
        self.metrics="f1"
    def model_output(self,x):
        if self.model=="svm":
            c=float(x[:,0])       
            m=SVC(kernel='linear',C=c, random_state=None)
        if self.model=="lr":
            c=float(x[:,0])
            m= LogisticRegression(C=c)
        if self.model=="randomforest":
            MD=float(x[:,0])
            MS=float(x[:,1])
            MF=float(x[:,2])
            NE=int(x[:,3])
            m= RandomForestClassifier(max_depth=MD,min_samples_split=MS,max_features=MF,n_estimators=NE,random_state=0)
        ac=0
        recall=0
        f1=0
        pre=0  
        if self.way_of_split=="skf":
            s=StratifiedKFold(n_splits=self.num_of_splits, shuffle=True)
        elif self.way_of_split=="kf":
            s= KFold(n_splits=self.num_of_splits)  
        for train_index, val_index in s.split(self.vector, self.target):   
            m.fit(self.vector[train_index],self.target[train_index])
            Y_pred = m.predict(self.vector[val_index])
            ac+=accuracy_score(y_true=self.target[val_index], y_pred=Y_pred)
            pre+=precision_score(y_true=self.target[val_index], y_pred=Y_pred)
            recall+=recall_score(y_true=self.target[val_index], y_pred=Y_pred)
            f1+=f1_score(y_true=self.target[val_index], y_pred=Y_pred)
        if self.metrics=="f1":
            return f1/self.num_of_splits
        elif self.metrics=="ac":
            return ac/self.num_of_splits
        elif self.metrics=="pre":
            return pre/self.num_of_splits
        elif self.metrics=="recall":
            return recall/self.num_of_splits

def classifer_training(text,target,way_of_vectorize="tfidf",down_sample=True,way_of_split="skf"):
    target=np.array(target)
    logs=[]
    svm_iter=5
    RF_iter=30
    lr_iter=5
    # way of vectorize
    if way_of_vectorize=="count":
        vectorizer = CountVectorizer( min_df=1,decode_error="ignore")            
        vector= sp.normalize(vectorizer.fit_transform(text), norm='l2')     
    elif way_of_vectorize=="tfidf":
        vectorizer=TfidfVectorizer(decode_error="ignore")
        vector=vectorizer.fit_transform(text)
    elif way_of_vectorize=="LSA":
        print("lsa......")
        lsa = TruncatedSVD(n_components=500)
        vector= lsa.fit_transform(vectorizer.fit_transform(text),target)
    #save vedtorizer
    if not os.path.exists('models'):
        os.mkdir('models')
    filename = 'models/vectorizer.pickle'
    pickle.dump(vectorizer, open(filename, 'wb'))
    #down sampling
    if down_sample:
        sampler = RandomUnderSampler(random_state=0)
        vector,target=sampler.fit_resample(vector,target)
    
    vector,test_vector,target,test_target=train_test_split(vector,target,test_size = 0.2, random_state = 0)
    #turnig hyperparameter
    print("turnig hyperparameter...")
    c=model_for_opt(vector,target,num_of_split=10,model="svm",way_of_split=way_of_split)  
    bounds =[{'name': 'c', 'type': 'continuous',  'domain':(0.001,1000.0)}]  
    opt_mnist_svm = GPyOpt.methods.BayesianOptimization(f=c.model_output,domain=bounds,maximize=True)
        
    c=model_for_opt(vector,target,num_of_split=10,model="randomforest",way_of_split=way_of_split)  
    bounds=[{'name': 'MD', 'type': 'continuous',  'domain':(0.001,1.0)}
            ,{'name': 'MS', 'type': 'continuous',  'domain':(0.001,0.99)}
            ,{'name': 'MF', 'type': 'continuous',  'domain':(0.01,0.99)}
            ,{'name': 'NE', 'type': 'discrete',  'domain':(10,20,30,40,50,60,70,80,90,100)}]
    opt_mnist_RF = GPyOpt.methods.BayesianOptimization(f=c.model_output,domain=bounds,maximize=True)
    
    c=model_for_opt(vector,target,num_of_split=10,model="lr",way_of_split=way_of_split)
    bounds =[{'name': 'c', 'type': 'continuous',  'domain':(0.001,1000.0)}]
    opt_mnist_LR = GPyOpt.methods.BayesianOptimization(f=c.model_output,domain=bounds,maximize=True)      
 
    opt_mnist_svm.run_optimization(max_iter=svm_iter)
    opt_mnist_RF.run_optimization(max_iter=RF_iter)
    opt_mnist_LR.run_optimization(max_iter=lr_iter)
    print("evaluation...")
    svm=SVC(kernel='linear',C=opt_mnist_svm.x_opt[0], random_state=None)

    RF= RandomForestClassifier(max_depth=opt_mnist_RF.x_opt[0],min_samples_split=opt_mnist_RF.x_opt[1],max_features=opt_mnist_RF.x_opt[2],n_estimators=int(opt_mnist_RF.x_opt[3]),random_state=0)
    
    LR= LogisticRegression(C=opt_mnist_LR.x_opt[0])
    svm.fit(vector,target)
    RF.fit(vector,target)
    LR.fit(vector,target)
    filename = 'models/svm.pickle'
    pickle.dump(svm, open(filename, 'wb'))
    filename = 'models/RF.pickle'
    pickle.dump(RF, open(filename, 'wb'))
    filename = 'models/LR.pickle'
    pickle.dump(LR, open(filename, 'wb'))

    Y_pred = svm.predict(test_vector)
    ac=accuracy_score(y_true=test_target, y_pred=Y_pred)
    pre=precision_score(y_true=test_target, y_pred=Y_pred)
    recall=recall_score(y_true=test_target, y_pred=Y_pred)
    f1=f1_score(y_true=test_target, y_pred=Y_pred)
    log={"accuracy":ac,"pre":pre,"recall":recall,"f1":f1}
    logs.append(log)

    Y_pred = RF.predict(test_vector)
    ac=accuracy_score(y_true=test_target, y_pred=Y_pred)
    pre=precision_score(y_true=test_target, y_pred=Y_pred)
    recall=recall_score(y_true=test_target, y_pred=Y_pred)
    f1=f1_score(y_true=test_target, y_pred=Y_pred)
    log={"accuracy":ac,"pre":pre,"recall":recall,"f1":f1}
    logs.append(log)

    Y_pred = LR.predict(test_vector)
    ac=accuracy_score(y_true=test_target, y_pred=Y_pred)
    pre=precision_score(y_true=test_target, y_pred=Y_pred)
    recall=recall_score(y_true=test_target, y_pred=Y_pred)
    f1=f1_score(y_true=test_target, y_pred=Y_pred)
    log={"accuracy":ac,"pre":pre,"recall":recall,"f1":f1}
    # save score
    logs.append(log)
    db=pd.DataFrame(logs)
    db.to_csv("score.csv")
