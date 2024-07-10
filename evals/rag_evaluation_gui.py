import random
import pandas as pd
import requests
from datasets import Dataset 
import os
from ragas import evaluate
from pandasgui import show
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["RAG_API_URL"] = os.getenv("RAG_API_URL")

def extract_info(content):
    questions = []
    ground_truths = []
    filenames = []
    
    lines = content.split('\n')
    for line in lines:
        if '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                question = parts[0]
                filename = parts[1].strip('*') + '.pdf'
                ground_truth = parts[-1].split('SOURCE(S):')[0].strip()
                
                questions.append(question)
                ground_truths.append(ground_truth)
                filenames.append(filename)
    
    return questions, ground_truths, filenames

def upload_file(filename):
    random_number = random.randint(10000, 99999)
    user_id = f"test-doc-{random_number}"
    api_url = f'{os.environ["RAG_API_URL"]}/management/files?user_id={user_id}'
    file_url = f"https://storage.googleapis.com/eval-public-files/10q-dataset/{filename}"
    payload = {
        "url": file_url,
        "fileName": filename
    }
    response = requests.post(api_url, json=payload)
    return response.json(), user_id

def query_app(question, user_id):
    api_url = f'{os.environ["RAG_API_URL"]}/chat/request?user_id={user_id}'
    payload = {
        "messages": [
            {
                "content": question,
                "role": "user"
            }
        ]
    }
    response = requests.post(api_url, json=payload)
    return response.json()

df = pd.read_csv('rag-eval-dataset-1.csv', header=None)

questions = df[0].tolist()
user_ids = df[1].tolist()
ground_truths = df[3].tolist()


# Upload files (only need to do this once for each unique file)
# uploaded_files = {}
# for filename in set(filenames):
#     upload_response, user_id = upload_file(filename)
#     print(f"File upload response for {filename}:", upload_response)
#     uploaded_files[filename] = user_id

answers = []
contexts = []

for question, user_id in zip(questions, user_ids):
    query_response = query_app(question, user_id)
    
    # Extract answer
    answer = query_response['result']['content']
    answers.append(answer)
    
    # Extract contexts
    question_contexts = []
    for node in query_response['nodes']:
        question_contexts.append(node['text'])
    contexts.append(question_contexts)

# Now you have all the data for your dataset
data_samples = {
    'question': questions,
    'answer': answers,
    'contexts': contexts,
    'ground_truth': ground_truths
}

# Create the dataset
dataset = Dataset.from_dict(data_samples)

# Evaluate the dataset
score = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
df = score.to_pandas()
show(df)