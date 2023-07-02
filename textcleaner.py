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
        self.emoticon_set = set(emoticons_dict.keys())
    
    def clean(self, text: str, spell_check= True) -> str:
        text = text.lower()
        
        # Remove hashtags and mentions
        text = re.sub(r"#\w+", "", text) # Maybe hashtags shouldn't be removed
        text = re.sub(r"@\w+", "", text)
        
        # Replace emoticons with their meaning
        for emot, meaning in emoticons_dict.items():
            text = text.replace(emot, meaning)

        # Handle cases such as "haaaappy" -> "happy"
        text = re.sub(r'(.)\1{2,}', lambda match: match.group(1), text)

        # Convert contractions (i.e., i'm) to full form
        text = contractions.fix(text)

        # Replace chat/slang words
        tok_list = text.split()
        new_list = []
        for tok in tok_list:
            if tok in chat_words_map_dict:
                new_list.extend(chat_words_map_dict[tok].split())
            else:
                new_list.append(tok)
        tok_list = new_list
               
        tok_list = [clean(tok,
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
        ) for tok in tok_list] 

        if spell_check:
            # Correct spelling
            corrected = []
            misspelled = self.spell_checker.unknown(tok_list) # Store mispelled words
            for word in tok_list:
                if word in misspelled:
                    corrected_word = self.spell_checker.correction(word)
                    if corrected_word != None:
                        corrected.append(corrected_word) # Append with corected word
                else:
                    corrected.append(word)
            tok_list = corrected

        # Remove stopwords (i.e., small, frequent words that dont contribute to meaning)
        tok_list = [word for word in tok_list if word not in self.stopwords_list]

        # Lemmatize (find root of each word)
        pos_tagged_text = nltk.pos_tag(tok_list) # Find part of speech of each word
        text = " ".join([self.lemmatizer.lemmatize(word, self.wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])
        
        # Remove non alphanumeric characters
        text = re.sub('[^a-zA-Z ]', '', text)

        return text
