from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

candidate_labels = ['news', 'business', 'sports', 'commentaries', 'letters', 'interviews', 'feature', 'scroll bars', 'notices', 'opeds', 'stocks']

def classifyText(sequence_to_classify):
    candidate_labels = ['travel', 'cooking', 'dancing', 'exploration']
    res = classifier(sequence_to_classify, candidate_labels, multi_label=True)
    
    {'sequence': 'one day I will see the world', 'labels': ['travel', 'exploration', 'dancing', 'cooking'], 'scores': [0.9945111274719238, 0.9383890628814697, 0.005706155207008123, 0.001819303841330111]}
    
    return {
        "labels": res['labels'],
        "scores": res['scores']
    }