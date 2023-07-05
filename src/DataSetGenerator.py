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
    # Get the content length
    content_length = len(tokens)
    # Get the category (e.g., "technology", "business", etc.)
    category = identify_category(content)

    # Create the payload dictionary
    payload = {
        "content": content,
        "type": content_type,
        "style": style,
        "language": language['language'],
        "brand_voice": brand_voice,
        "content_length": content_length,
        "category": category
    }

    return payload

def identify_category(content):
    # Define your categories and corresponding keywords
    category_keywords = {
        "technology": ["technology", "digital", "innovation", "AI", "cloud"],
        "business": ["business", "enterprise", "strategy", "leadership", "finance"],
        "healthcare": ["healthcare", "medical", "wellness", "patient", "pharmaceutical"],
        "education": ["education", "learning", "student", "school", "university"],
        "travel": ["travel", "adventure", "explore", "vacation", "destination"],
        "food": ["food", "recipe", "cooking", "restaurant", "cuisine"],
        "sports": ["sports", "fitness", "exercise", "athlete", "competition"],
        "entertainment": ["entertainment", "movies", "music", "celebrities", "arts"],
        "fashion": ["fashion", "style", "clothing", "trends", "design"],
        "environment": ["environment", "sustainability", "climate", "eco-friendly", "green"]
        # Add more categories and their respective keywords as needed
    }

    # Tokenize the content
    tokens = word_tokenize(content)

    # Initialize the category
    category = "other"

    # Iterate over the categories and check for keyword matches
    for cat, keywords in category_keywords.items():
        if any(keyword.lower() in tokens for keyword in keywords):
            category = cat
            break

    return category

def identify_style(content):
    # Vectorize the content
    X = vectorizer.transform([content])

    # Predict the style using the trained SVM model
    style = svm_model.predict(X)[0]

    # Map the style prediction to the new style types
    style_types = {
        "formal": ["professional", "technical", "precise"],
        "informal": ["casual", "conversational", "engaging"],
        "other": ["neutral", "balanced", "generic"]
    }

    # Determine the best matching style type based on keyword overlap
    style_keywords = style_types.get(style, [])
    tokenized_content = word_tokenize(content.lower())
    style_scores = [sum(token in tokenized_content for token in keywords) for keywords in style_keywords]
    best_style_index = max(range(len(style_keywords)), key=style_scores.__getitem__)
    best_style = style_keywords[best_style_index]

    return best_style

def identify_brand_voice(tokens):
    # Define your brand voice rules or keywords
    brand_voice_keywords = {
        "formal": ["professional", "industry-standard", "authoritative", "polished", "official"],
        "conversational": ["friendly", "approachable", "relatable", "casual", "engaging"],
        "neutral": ["informative", "unbiased", "balanced", "objective", "impartial"]
    }

    # Calculate the relevance scores for each brand voice type based on keyword matches
    brand_voice_scores = {
        brand_voice: sum(token.lower() in keywords for token in tokens)
        for brand_voice, keywords in brand_voice_keywords.items()
    }

    # Determine the best matching brand voice type based on the highest relevance score
    best_brand_voice = max(brand_voice_scores, key=brand_voice_scores.get)

    return best_brand_voice

def GetDataSet(url):
    # blog content
    blog_content = GetArticle(url)
    content_type = ""
    if "blog" in url:
        content_type = "blog"
    elif "newsroom" in url:
        content_type = "pressRelease"
    
    return generate_payload(str(blog_content), content_type)

#print(GetDataSet("https://blogs.infosys.com/digital-experience/emerging-technologies/microsofts-gpt-4-copilot-and-googles-palm.html"))