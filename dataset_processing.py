import pandas as pd
import nltk
nltk.download('punkt')

def clean_text(text):
    return text.replace('[', '').replace(']', '').replace('"', '').replace('.,', '.')

def is_valid_recipe(recipe):
    sentences = nltk.sent_tokenize(recipe)
    return len(sentences) >= 3


df = pd.read_csv("recipes_data.csv", nrows=10000)

df['NER'] = df['NER'].apply(clean_text)
df['directions'] = df['directions'].apply(clean_text)
df = df[df['directions'].apply(is_valid_recipe)]

df = df.rename(columns={'NER': 'input_ingredients', 'directions': 'output_recipe'})

with open("processed_recipes_data.txt", "w") as f:
    for index, row in df.iterrows():
        f.write(f'[Q] Ingredients: {row["input_ingredients"]}\n[A] {row["output_recipe"]}\n\n')