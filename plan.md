# Pathfinder.Ai: Future AWS Evolution Plan

This roadmap outlines the steps to transition Pathfinder.Ai from a traditional monolith to a **Modern AWS AI-Native Architecture** to meet the highest technical evaluation standards.

## 🚀 Phase 1: Generative AI Layer (Amazon Bedrock)
*Goal: Move beyond simple vector matching to deep semantic reasoning.*

1.  **Personalized Career Coach:**
    *   Integrate **Amazon Bedrock (Claude 3.5 Sonnet)**.
    *   Send student profile + top 3 job matches to Bedrock.
    *   Generate a custom "Strategy Report" for the student.
2.  **AI-Tailored Cover Letter Generator:**
    *   Add a "Generate Cover Letter" button on each job listing.
    *   Use Bedrock to draft a professional letter that maps student skills directly to job requirements.

## ☁️ Phase 2: Serverless Transformation (AWS Lambda)
*Goal: Implement cost-effective, auto-scaling backend patterns.*

1.  **Serverless Harvester:**
    *   Decouple the `Harvester` service from the main Flask API.
    *   Deploy the scraper logic to **AWS Lambda**.
    *   Set up an **Amazon EventBridge** trigger to run the Lambda every 6–12 hours automatically.
2.  **API Gateway Integration:**
    *   Expose specific backend endpoints (like health checks or harvesters) via **Amazon API Gateway** to follow AWS-native API patterns.

## 📂 Phase 3: Stateless Infrastructure (Amazon S3)
*Goal: Decouple storage from the server to ensure high availability.*

1.  **Distributed File Storage:**
    *   Create an **Amazon S3** bucket named `pathfinder-user-assets`.
    *   Modify the profile service to upload resumes and profile photos to S3 instead of the local filesystem.
    *   Serve these assets via authenticated S3 URLs.

## 📊 Phase 4: Observability & Logging (AWS CloudWatch)
*Goal: Improve reliability and monitoring.*

1.  **Centralized Logging:**
    *   Configure the EC2 instance and Lambda functions to stream all logs to **AWS CloudWatch**.
    *   Set up Alarms for whenever the Harvester fails or a database connection times out.

## 📝 Phase 5: Technical Evaluation Submission
*Goal: Prepare the documentation required for the AWS challenge.*

1.  **Why AI is Required:** Explain the shift from keyword-search to semantic-intent matching.
2.  **AWS Architecture Diagram:** Visualize the flow from Amplify -> API Gateway -> Lambda/EC2 -> Bedrock -> RDS (pgvector).
3.  **Value Add:** Document how the "AI Career Coach" specifically improves the student landing rate.
