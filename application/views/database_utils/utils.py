import os
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import precision_score, recall_score, accuracy_score

from ..utils.helper_utils import sigmoid

stopWord = [
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves",'_','__','___','____','_____','______','_______','________','_________','__________','___________','____________',
    '_____________','_____________','_______________','__________________________','___________________','________________',
    '_________________________________________________','______________________________________________________________',
    '_________________________________________________________________','_______________________________________________________________________________',
    '____________________________________________________________________________','__________________________________________________________________________',
    '_____________________________________________________________________','don','ve','doesn','ll','didn','isn','non','won','th',
    'aren','ah','aiu','ax','bhj','bm','bn','bxn','chz','cj','ck','cx','dee','di','ei','fanatism','fpl','fps','fq','gfci'\
    'giz','gk','gq','gy','hj','ihl','iu','kn','lg','lk','mcconkie','mf',\
    'mw','qs','rmw','stephanopoulos','tl','tq','uj','wm','wsh','ww','xmu','yx','zd','','','',]

skip_pair = {
    "restaurant": [33], # cup
    "cafeteria": [33], # cup
    "hygiene": [33], # cup
    "drink": [33], # cup
    "drinks": [33], # cup
    "beverage": [33], # cup
    "beverages": [33], # cup
    "breakfast": [33], # cup
    "toiletries": [33], # cup
    "tea": [33], # cup
    "cuisine": [37], # bowl
    "skateboard": [37], # bowl
}

must_skip = {
    37: ["skateboard"]
}

skip_tuples = [
    "coffee table", "coffee tables", "coffee shop", 
    "coffee maker", "coffee house", "coffee dispenser",
    "toilet bowl", "toilet bowls",
    "skate bowl", "skate bowls", 
]

def GetNoneMeaningWords():
    s = ["like", "just", "good", "know", "say", "year", "papers", "abstract", "introduction", "conclusion",
         "title", "et", "al", "using", "fig", "it", "eq", "ij", "paper", "sec", "ii", "jj", "using", "ji",
         "method", "methods", "datasets", "dataset", "novel", "multiple", "better", "id", "does"]
    return s

def get_count(all_text, gram_min=1, gram_max=1, min_df=3):
    train_count_vectorizer = CountVectorizer(min_df=min_df,stop_words=stopWord+GetNoneMeaningWords(), ngram_range=(gram_min, gram_max))
    train_count_vectorizer.fit(all_text)
    X = train_count_vectorizer.transform(all_text)
    vocals = train_count_vectorizer.get_feature_names()
    return X, vocals

def TFIDFTransform(texts, gram_min=1, gram_max=1):
    X, vocals = get_count(texts, gram_min=gram_min, gram_max=gram_max)
    tfidf_transformer = TfidfTransformer()
    tfidf = tfidf_transformer.fit_transform(X)
    return tfidf, vocals

def rule_based_processing(extracted_labels, suffix="step1"):
    enable_rules = True
    if suffix == "":
        enable_rules = False
    string = extracted_labels["string"]
    # string = [s + " " for s in string]
    # string = "".join(string)
    # string = string[:-1]
    class_num = len(extracted_labels["logits"])
    pred = np.zeros(class_num)
    for act in extracted_labels["activations"]:
        cats = act["cats"]
        skip_cats = skip_pair.get(act["text"], [])
        if enable_rules and (act["idx"]+1) < len(string) and string[act["idx"]] + " " + string[act["idx"]+1] in skip_tuples:
            # import IPython; IPython.embed(); exit()
            continue
        if enable_rules and (act["idx"]) > 0 and string[act["idx"] - 1] + " " + string[act["idx"]] in skip_tuples:
            continue
        for c in cats:
            if enable_rules and c in skip_cats:
                continue
            pred[c] = 1
    
    for cat in must_skip:
        keys = must_skip[cat]
        for k in keys:
            if string.count(k) > 0:
                pred[cat] = 0 

    return pred

def get_precision_and_recall(part):
    preds = []
    labels = []
    for p in part:
        logit = p["rule_logit"]
        label = p["label"]
        pred = sigmoid(np.array(logit)) > 0.5
        # res.append([pred, label])
        preds.append(pred.reshape(-1))
        labels.append(np.array(label).reshape(-1))
    preds = np.array(preds)
    labels = np.array(labels)
    print("preds", preds.shape)
    print("labels", labels.shape)
    p = preds.sum(axis=0) / preds.shape[0]
    pre = []
    rec = []
    for i in range(preds.shape[1]):
        pre.append(precision_score(labels[:,i], preds[:, i]))
        rec.append(recall_score(labels[:,i], preds[:, i]))
    return p, pre, rec

def multiclass_precision(y_true, y_pred):
    pre = []
    for i in range(y_pred.shape[1]):
        pre.append(precision_score(y_true[:, i], y_pred[:, i]))
    pre = np.array(pre)
    return pre

def multiclass_recall(y_true, y_pred):
    recall = []
    for i in range(y_pred.shape[1]):
        recall.append(recall_score(y_true[:, i], y_pred[:, i]))
    recall = np.array(recall)
    return recall

def multiclass_precision_and_recall(y_true, y_pred):
    precision = multiclass_precision(y_true, y_pred)
    recall = multiclass_recall(y_true, y_pred)
    return precision, recall



# encoding set names
def encoding_categories(categories):
    categories = list(set(categories))
    categories.sort()
    strs = [str(i) + "-" for i in categories]
    res = "".join(strs)
    res = res[:-1]
    return res

def decoding_categories(category_str):
    categories = category_str.split("-")
    categories = [int(i) for i in categories]
    return categories