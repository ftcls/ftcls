from pymongo import MongoClient
from datetime import datetime
from vec_cla import count_logistic
import random
import warnings
warnings.filterwarnings('ignore')
def main():
    classifier=count_logistic()
    clint = MongoClient()
    db =clint["husyouji"]
    collection1 = db['pool']
    collection = db['labeled']
    #id_=[post["_id"] for post in collection1.find()]
    texts_pool=[post["text"] for post in collection1.find()]

    while True:
        texts=[]
        collection = db['labeled']
        random.shuffle(texts_pool)
        if collection.count({"tag":"__label__1"})>3 and collection.count({"tag":"__label__2"})>3:
            texts=[post["text"] for post in collection.find()]
            target=[post["tag"] for post in collection.find()]
            classifier.model_fit(texts,target)
            text,p=classifier.next_text_pool(texts_pool)
            print(text,p)        
        else:
            text=random.choice(texts_pool)                    
            print(text) 
                   
        if text in texts:
            texts_pool.remove(text)
        else:
            tag_=input("is this __label__1 ? [y/n]-->")
            if tag_=="y":
                collection.insert({"tag":"__label__1","text":text})
                texts_pool.remove(text)
            elif tag_=="n":
                collection.insert({"tag":"__label__2","text":text})
                texts_pool.remove(text)

if __name__ == "__main__":
    main()