# classifer_training(text,target,way_of_vectorize="tfidf",down_sample=True,way_of_split="skf",metrics="ac")

it use Bayesian Optimization　for hyperparameter turnig each svm machine,random forest, logistic reguration
and it output model and vectorizer as picklefile and output score of each metircs as csvfile



## text and target 
text input as list of ward
target is [1,1,-1......]

## vecotrize={"tfidf","count","LSA"}
I recomnd tfidf 
LSA is way of Dimensional compression but it take time but dosent wark well
count is just count ward

## down_sample={True,Fales}

you can choose do down_sample or not

## way_of_split={"skf","kf"}

it detarmin way of KFold test 

## metrics_={"ac","f1","recall","pre"}
determing metrics of hyperparameter tunig




and you can use Scandal detection trained model in try.py 


