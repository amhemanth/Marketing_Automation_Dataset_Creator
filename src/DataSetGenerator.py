import nltk
import spacy
import spacy
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from BlogContent import GetArticle
from spacy.language import Language
from spacy_language_detection import LanguageDetector

# Download NLTK resources
nltk.download('punkt')

def get_lang_detector(nlp, name):
    return LanguageDetector(seed=42)

# Load English language model in spaCy
nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)

# Define the training data for style identification
style_training_data = [
    {"text": "This is a formal document with technical language.", "style": "formal"},
    {"text": "Hey, check out this cool blog post!", "style": "informal"},
    {"text": "Greetings, esteemed colleagues. I am writing to propose a new initiative.", "style": "formal"},
    {"text": "OMG, you won't believe what just happened! It's insane!", "style": "informal"},
    {"text": "Dear Sir/Madam, I am writing to express my concerns regarding the recent policy changes.", "style": "formal"},
    {"text": "Hey guys, wanna grab some pizza and chill?", "style": "informal"},
    {"text": "I hereby declare my utmost appreciation for your gracious hospitality.", "style": "formal"},
    {"text": "Sup, fam? Let's hit the beach and have a blast!", "style": "informal"},
    {"text": "To whom it may concern, I am writing to inquire about the job vacancy at your company.", "style": "formal"},
    {"text": "Yo, dude! You have to watch this awesome video I found!", "style": "informal"},
    {"text": "The symposium will commence promptly at 9:00 AM in the main auditorium.", "style": "formal"},
    {"text": "Hey peeps, let's meet up at the park for a picnic!", "style": "informal"},
    {"text": "I am deeply grateful for your invaluable assistance in this matter.", "style": "formal"},
    {"text": "Guess what? I got tickets to the concert! It's gonna be epic!", "style": "informal"},
    {"text": "I am writing to inform you of the upcoming changes to our company policies.", "style": "formal"},
    {"text": "OMG, I just binge-watched the entire series in one day. It's so addictive!", "style": "informal"},
    {"text": "Please be advised that the deadline for submission is approaching.", "style": "formal"},
    {"text": "Hey, wanna grab some coffee and catch up?", "style": "informal"},
    {"text": "I am pleased to inform you that you have been selected for the scholarship.", "style": "formal"},
    {"text": "Hey y'all, let's have a barbecue party this weekend!", "style": "informal"},
]

# Train a LinearSVC model for style identification
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform([data["text"] for data in style_training_data])
y_train = [data["style"] for data in style_training_data]
svm_model = LinearSVC()
svm_model.fit(X_train, y_train)

def generate_payload(content, content_type):
    # Tokenize the content
    tokens = word_tokenize(content)

    # Style identification
    style = identify_style(content)

    # Brand voice identification
    brand_voice = identify_brand_voice(tokens)

    doc = nlp(content)
    # Get the language of the document 
    language = doc._.language
    # Create the payload dictionary
    payload = {
        "content": content,
        "type": content_type,
        "style": style,
        "language": language['language'],
        "brand_voice": brand_voice
    }

    return payload

def identify_style(content):
    # Vectorize the content
    X = vectorizer.transform([content])

    # Predict the style using the trained SVM model
    style = svm_model.predict(X)[0]

    return style

def identify_brand_voice(tokens):
    # Define your brand voice rules or keywords
    # Example: Formal brand voice
    formal_keywords = ["professional", "industry-standard", "enterprise"]

    # Count the occurrences of formal keywords in the tokens
    formal_keyword_count = sum(token.lower() in formal_keywords for token in tokens)

    # Identify the brand voice based on the keyword count
    brand_voice = "formal" if formal_keyword_count >= 2 else "casual"

    return brand_voice

def GetDataSet(url):
    # blog content
    blog_content = GetArticle(url)
    content_type = ""
    if "blog" in url:
        content_type = "blog"
    elif "newsroom" in url:
        content_type = " "
    
    return generate_payload(str(blog_content), content_type)

#print(GetDataSet("https://blogs.infosys.com/digital-experience/emerging-technologies/microsofts-gpt-4-copilot-and-googles-palm.html"))