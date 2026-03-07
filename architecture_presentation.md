# Pathfinder.Ai: System Architecture

## 🏗️ The Engineering Blueprint

````carousel
![Full Enterprise Cloud Architecture](/C:/Users/amiar/.gemini/antigravity/brain/bf87a8ad-a17f-4250-9a6f-9c280644f308/pathfinder_full_aws_architecture_1772914213982.png)
<!-- slide -->
![Standard AWS Architecture](/C:/Users/amiar/.gemini/antigravity/brain/bf87a8ad-a17f-4250-9a6f-9c280644f308/pathfinder_aws_architecture_standard_1772914142375.png)
<!-- slide -->
![Futuristic Architecture Diagram](/C:/Users/amiar/.gemini/antigravity/brain/bf87a8ad-a17f-4250-9a6f-9c280644f308/pathfinder_architecture_diagram_1772914047214.png)
````

Pathfinder.Ai is built on an enterprise-grade, high-resiliency cloud architecture. It utilizes a **Multi-Tier Distributed System** to ensure 99.9% availability and elite processing speeds.

### 🏢 Architecture Tiers

#### 1. Edge & Delivery (Global Scale)
*   **AWS CloudFront:** Low-latency content delivery for the Vue.js frontend, ensuring fast global load times.
*   **Application Load Balancer (ALB):** Intelligent traffic distribution across multiple backend instances to prevent bottlenecks.

#### 2. The Compute & Intelligence Tier (The Logic)
*   **High-Resiliency Backend:** Flask API hosted on EC2 with **Auto-Scaling Groups** to handle sudden traffic influxes.
*   **Hybrid Brain:**
    *   **AWS Bedrock (Claude 3.5/4.5):** Performs high-complexity generative tasks (LaTeX, Deep Reasoning).
    *   **Groq Cloud (Llama Fallback):** Ultra-low latency inference for real-time interview interactions and system failover.

#### 3. Storage & Sensory Integration
*   **AWS Polly:** Converts complex AI reasoning into human-like speech for a tactile interview experience.
*   **Amazon S3:** Secure, durable object storage for dynamically generated resumes and profile avatars.
*   **Amazon RDS:** Managed PostgreSQL database for transactional data, user profiles, and session tracking.

---

### 🛡️ Resilience & Scaling
By decoupling the "Thinking" (Bedrock) from the "Fast-Response" (Groq), we have created a **Production-Ready Agentic Ecosystem** that is both smarter and more reliable than traditional single-model applications.
