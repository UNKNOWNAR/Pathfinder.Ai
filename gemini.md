# Current Context: Pathfinder.Ai AWS Bedrock Integration

## Objective
The goal was to fix the "Internal Server Error" occurring when trying to use the AI Interviewer and Resume Generator features on `https://pathfinderai.me`. The features rely on AWS Bedrock to call Anthropic Claude models.

## Current State & The Problem
We attempted to use a long-term "Bedrock API Key" provided by the user. However, standard AWS Bedrock endpoints (`bedrock-runtime.us-east-1.amazonaws.com`) **do not accept `X-Api-Key` headers**. They strictly require AWS Signature Version 4 (IAM Credentials).

When the key authentication inevitably failed (returning a `403`), our backend code correctly fell back to using standard `boto3` with the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` stored in the `.env` file.

However, the `boto3` fallback hit the **real, underlying issue**:
```text
botocore.errorfactory.ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the InvokeModel operation: Model use case details have not been submitted for this account. Fill out the Anthropic use case details form before using the model. If you have already filled out the form, try again in 15 minutes.
```

## What This Means
1. The AWS IAM credentials in the `.env` file are partially working (they are successfully reaching AWS).
2. However, the specific AWS Account hosting these models has **not** been fully authorized to use `Claude 4.5 Haiku` (or potentially other Anthropic models) because the mandatory **"Use case details" form** has not been submitted or approved in the AWS Bedrock Console.

## What has been done in the code
1. The backend has been updated to use the correct model ID for Claude 4.5 Haiku in US-East-1: `us.anthropic.claude-haiku-4-5-20251001-v1:0` (Requires the `us.` Inference Profile prefix).
2. The code in `backend/services/agent_service.py` and `backend/services/llm_service.py` is fully functional and correctly falls back to `boto3`.
3. All changes have been pushed to the `master` branch and deployed to the EC2 instance `65.0.4.84` via `deploy.sh`.
4. Fixed a minor bug where `logger` was used instead of `logging`.

## Next Steps to Fix the Issue
The issue is purely infrastructural at this point, not code-related.
1. The user must log into their AWS Management Console.
2. Navigate to **Amazon Bedrock -> Model access**.
3. Complete the **"Submit use case details"** requirement for Anthropic models.
4. Wait for AWS approval (usually instantaneous up to a few hours). 
5. Once approved, the existing deployed code will automatically start working. No further code changes should be necessary for Bedrock invocation.
