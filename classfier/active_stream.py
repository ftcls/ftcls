from pymongo import MongoClient
from datetime import datetime
from vec_cla import count_logistic2
import random
import csv
import warnings
warnings.filterwarnings('ignore')
def main():
    classifier=count_logistic2()
    clint = MongoClient()
    db =clint["husyouji"]
    collection1 = db['balanced_train']
    collection = db['labeled']
    texts_pool=[post["text"] for post in collection1.find()]
    random.shuffle(texts_pool)
    texts=[]
    #need at least 3 text in each label
    if collection.count({"tag":"__label__1"})>3 and collection.count({"tag":"__label__2"})>3:
        collection = db['labeled']  
        texts=[post["text"] for post in collection.find()]
        target=[post["tag"] for post in collection.find()]
        classifier.model_fit_grid(texts,target)
        
        for text1,p in classifier.next_text_stream(texts_pool,0.1):
            
            collection = db['labeled']  
            texts=[post["text"] for post in collection.find()]
            target=[post["tag"] for post in collection.find()]
            classifier.model_fit_grid(texts,target)
            print(text1,p)

            tag_=input("is this __label__1 ? [y/n]-->")
            if tag_=="y":
                collection.insert({"tag":"__label__1","text":text1})
                texts_pool.remove(text1)
            elif tag_=="n":
                collection.insert({"tag":"__label__2","text":text1})
                texts_pool.remove(text1)
    # at first choose text randomly
    else:
        for text in texts_pool:                
            if text in texts:
                texts_pool.remove(text)
            else:
                print(text)
                tag_=input("is this __label__1 ? [y/n]-->")
                if tag_=="y":
                    collection.insert({"tag":"__label__1","text":text})
                    texts_pool.remove(text)
                elif tag_=="n":
                    collection.insert({"tag":"__label__2","text":text})
                    texts_pool.remove(text)

if __name__ == "__main__":
    main()