from emoticons import EMOTICONS_EMO as emoticons_dict
from chatwords import chat_words_map_dict
import emoji
import re
import contractions
from cleantext import clean
from spellchecker import SpellChecker
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

class TextCleaner:
    def __init__(self):
        self.chat_words_list = set(chat_words_map_dict.keys())
        self.spell_checker = SpellChecker()
        self.stopwords_list = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV}
    
    def clean(self, text: str) -> str:
        text = text.lower()

        # Replace emoticons with their meaning
        for emot, meaning in emoticons_dict.items():
            text = text.replace(emot, meaning)

        # Replace emojis with their meaning
        text = emoji.demojize(text).replace(":", "").replace("_", " ")
        
        # Replace frequent chat words (i.e., IMO) with actual words
        new_text = []
        for w in text.split():
            if w in self.chat_words_list:
                new_text.append(chat_words_map_dict[w])
            else:
                new_text.append(w)
        text = " ".join(new_text)

        # Convert contractions (i.e., i'm) to full form
        text = contractions.fix(text)

        text = clean(text,
            fix_unicode=True,              # fix various unicode errors
            to_ascii=True,                 # transliterate to closest ASCII representation
            lower=True,                    # lowercase text
            no_line_breaks=True,           # fully strip line breaks as opposed to only normalizing them
            no_urls=True,                  # replace all URLs with a special token
            no_emails=True,                # replace all email addresses with a special token
            no_phone_numbers=True,         # replace all phone numbers with a special token
            no_numbers=True,               # replace all numbers with a special token
            no_digits=True,                # replace all digits with a special token
            no_currency_symbols=True,      # replace all currency symbols with a special token
            no_punct=True,                 # remove punctuations
            replace_with_punct="",         # instead of removing punctuations you may replace them
            replace_with_url="",
            replace_with_email="",
            replace_with_phone_number="",
            replace_with_number="",
            replace_with_digit="",
            replace_with_currency_symbol="",
            lang="en"                       # set to 'de' for German special handling
        )

        # Correct spelling
        corrected = []
        misspelled = self.spell_checker.unknown(text.split()) # Store mispelled words
        for word in text.split():
            if word in misspelled:
                corrected_word = self.spell_checker.correction(word)
                if corrected_word != None:
                    corrected.append(corrected_word) # Append with corected word
            else:
                corrected.append(word)
        text = " ".join(corrected)

        # Remove stopwords (i.e., small, frequent words that dont contribute to meaning)
        text = " ".join([word for word in text.split() if word not in self.stopwords_list])

        # Lemmatize (find root of each word)
        pos_tagged_text = nltk.pos_tag(text.split()) # Find part of speech of each word
        text = " ".join([self.lemmatizer.lemmatize(word, self.wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])
        
        # Remove extra spaces
        text = re.sub(' +', ' ', text)

        return text
