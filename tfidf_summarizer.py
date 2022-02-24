import nltk
nltk.download('all')
import random
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import warnings
from nltk.corpus import stopwords

# Handicap is a variable that will take values from zero to one and will let us increase or decrease the final threshold
# Bigger the Handicap, shorter the summary
HANDICAP = 0.7

# Function to set handicap based on length of text, if needed
# def set_handicap(text):
#     if (len(text) > 2000):
#         HANDICAP = 0.7
#     ...
#     return HANDICAP

# Function to remove slang from text, if needed
# def remove_slang(text):
#     ...
#     return text


def remove_punctuation_marks(text) :
    punctuation_marks = dict((ord(punctuation_mark), None) for punctuation_mark in string.punctuation)
    return text.translate(punctuation_marks)

def get_lemmatized_tokens(text) :
    normalized_tokens = nltk.word_tokenize(remove_punctuation_marks(text.lower()))
    return [nltk.stem.WordNetLemmatizer().lemmatize(normalized_token) for normalized_token in normalized_tokens]

def get_average(values) :
    greater_than_zero_count = total = 0
    for value in values :
        if value != 0 :
            greater_than_zero_count += 1
            total += value
    return total / greater_than_zero_count

def get_threshold(tfidf_results) :
    i = total = 0
    while i < (tfidf_results.shape[0]) :
        total += get_average(tfidf_results[i, :].toarray()[0])
        i += 1
    return total / tfidf_results.shape[0]

def get_summary(documents, tfidf_results) :
    summary = ""
    i = 0
    while i < (tfidf_results.shape[0]) :
        if (get_average(tfidf_results[i, :].toarray()[0])) >= get_threshold(tfidf_results) * HANDICAP :
                summary += ' ' + documents[i]
        i += 1
    return summary

def run_summarization(text):
    # Tokenizing the text
    documents = nltk.sent_tokenize(text)

    # Get TF-IDF values
    tfidf_results = TfidfVectorizer(tokenizer = get_lemmatized_tokens, stop_words = stopwords.words('english')).fit_transform(documents)

    # Return final summary
    return get_summary(documents, tfidf_results)




# Sample text to test summarizer
# text = """
# Louis Daniel Armstrong (August 4, 1901 – July 6, 1971), nicknamed "Satchmo",[a] "Satch",
# and "Pops",[2] was an American trumpeter, composer, vocalist, and actor who was among the most influential
# figures in jazz. His career spanned five decades, from the 1920s to the 1960s, and different eras in the
# history of jazz.[3] In 2017, he was inducted into the Rhythm & Blues Hall of Fame. Armstrong was born and raised in New Orleans.
# Coming to prominence in the 1920s as an inventive trumpet and cornet player, Armstrong was a foundational influence in jazz,
# shifting the focus of the music from collective improvisation to solo performance.[4] Around 1922, he followed his mentor,
# Joe "King" Oliver, to Chicago to play in the Creole Jazz Band. In Chicago, he spent time with other popular jazz musicians,
# reconnecting with his friend Bix Beiderbecke and spending time with Hoagy Carmichael and Lil Hardin. He earned a reputation
# at "cutting contests", and relocated to New York in order to join Fletcher Henderson's band. With his instantly recognizable rich,
# gravelly voice, Armstrong was also an influential singer and skillful improviser, bending the lyrics and melody of a song.
# He was also skilled at scat singing. Armstrong is renowned for his charismatic stage presence and voice as well as his trumpet
# playing. By the end of Armstrong's career in the 1960s, his influence had spread to popular music in general. Armstrong was one
# of the first popular African-American entertainers to "cross over" to wide popularity with white (and international) audiences.
# He rarely publicly politicized his race, to the dismay of fellow African Americans, but took a well-publicized stand for
# desegregation in the Little Rock crisis. He was able to access the upper echelons of American society at a time when this
# was difficult for black men.
# """