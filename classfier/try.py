import MeCab
import pickle
def ev():
    print("テキストを入力")
    text=input()
    toke=[]
    tagger= MeCab.Tagger('-Ochasen')
    result=tagger.parseToNode(text)                  
    while result:
        pos=result.feature.split(',')[0]
        pos2=result.feature.split(',')[1]
        if ((pos=="形容詞" or pos=="名詞" or pos=="動詞") and pos2!="数"and pos2!="固有名詞"): 
            toke.append(result.surface)
        result = result.next
    tokes=" ".join(toke)
    print(tokes)
    vectorizer= pickle.load(open(f'models/vectorizer.pickle','rb'))
    loaded_model = pickle.load(open(f'models/svm.pickle', 'rb'))

    result = vectorizer.transform([tokes])
    if loaded_model.predict(result)==1:
        print("不祥事")
    if loaded_model.predict(result)==-1:
        print("不祥事でない")
ev()