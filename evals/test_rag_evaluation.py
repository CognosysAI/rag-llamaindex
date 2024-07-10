import pytest
import pandas as pd
import requests
from datasets import Dataset
import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from dotenv import load_dotenv
import random

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["RAG_API_URL"] = os.getenv("RAG_API_URL")

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

def assert_in_range(score: float, value: float, plus_or_minus: float):
    """
    Check if computed score is within the range of value +/- max_range
    """
    assert value - plus_or_minus <= score <= value + plus_or_minus, f"Score {score} is not within {value} ± {plus_or_minus}"

@pytest.fixture(scope="module")
def dataset():
    df = pd.read_csv('rag-eval-dataset-1.csv', header=None)
    
    questions = df[0].tolist()[:10]
    user_ids = df[1].tolist()[:10]
    ground_truths = df[3].tolist()[:10]

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

    data_samples = {
        'question': questions,
        'answer': answers,
        'contexts': contexts,
        'ground_truth': ground_truths
    }

    return Dataset.from_dict(data_samples)

def test_rag_evaluation(dataset):
    result = evaluate(
        dataset,
        metrics=[answer_relevancy, faithfulness, context_recall, context_precision],
        in_ci=True,
    )
    
    print("\nDetailed Evaluation Results:")
    for metric, score in result.items():
        print(f"{metric}: {score:.4f}")
    
    assert result["answer_relevancy"] >= 0.8, f"Answer Relevancy ({result['answer_relevancy']:.4f}) is below threshold (0.8)"
    assert result["context_recall"] >= 0.8, f"Context Recall ({result['context_recall']:.4f}) is below threshold (0.8)"
    assert result["context_precision"] >= 0.8, f"Context Precision ({result['context_precision']:.4f}) is below threshold (0.8)"
    assert_in_range(result["faithfulness"], value=0.8, plus_or_minus=0.1)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])