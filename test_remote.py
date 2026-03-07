import boto3
import json
import os
from botocore.exceptions import ClientError

def check_models():
    # Assume environment variables are loaded or available to boto3
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    models_to_test = [
        # Amazon Nova
        'amazon.nova-micro-v1:0',
        'amazon.nova-lite-v1:0',
        # Amazon Titan
        'amazon.titan-text-lite-v1',
        # Meta Llama
        'meta.llama3-8b-instruct-v1:0',
        # Mistral
        'mistral.mistral-7b-instruct-v0:2',
        # Qwen (Alibaba)
        'qwen.qwen3-coder-30b-a3b-instruct-v1:0',  # Guessing based on Qwen3 pattern
        'qwen2.5-coder-32b-instruct-v1:0'
    ]

    print("Testing Bedrock Models Access...")
    for model_id in models_to_test:
        print(f"\n--- Testing {model_id} ---")
        try:
            # Using the converse API, which abstracts away the payload details
            response = bedrock.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Hello, are you there?"}]
                    }
                ],
            )
            print(f"✅ SUCCESS! Response: {response['output']['message']['content'][0]['text'][:50]}...")
        except ClientError as e:
            err_code = e.response['Error']['Code']
            err_msg = e.response['Error']['Message']
            print(f"❌ FAILED: [{err_code}] {err_msg}")
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")

if __name__ == "__main__":
    check_models()
