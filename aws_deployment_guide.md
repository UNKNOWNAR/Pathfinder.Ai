# AWS Deployment Guide: Pathfinder.Ai

This document outlines the step-by-step process for deploying the Pathfinder.Ai application (Flask backend, Vue.js frontend, and PostgreSQL database) entirely to AWS infrastructure.

**Important Note regarding AI Semantic Search:**
We have chosen to **not** migrate to Amazon Bedrock and AWS RDS `pgvector` for now. The application will deploy using the current architecture: a standard PostgreSQL database for relational data, and a persistent local **ChromaDB** directory on the backend server for semantic vector search.

---

## Architecture Overview
1. **Database:** Amazon RDS (PostgreSQL 15+)
2. **Backend Engine:** Amazon EC2 (Ubuntu 22.04 LTS) running Gunicorn + Nginx + ChromaDB
3. **Frontend Application:** AWS Amplify (Vue.js static hosting)

---

## 1. Provisioning the Database (AWS RDS)
*This handles our users, jobs, and relational data.*

1. Log into the AWS Management Console and navigate to **RDS**.
2. Click **Create database**.
3. Choose **Standard create** and select **PostgreSQL**.
4. **Templates:** Select **Free tier** (or Dev/Test if using credits).
5. **Settings:**
   - DB instance identifier: `pathfinder-db`
   - Master username: `postgres`
   - Master password: *Create a strong password and save it.*
6. **Instance configuration:** `db.t3.micro` is sufficient.
7. **Storage:** 20 GiB (General Purpose SSD). Disable storage autoscaling for cost control.
8. **Connectivity:**
   - Public access: **Yes** (to allow your local machine to run migrations, or **No** if you prefer to only connect via EC2).
   - Create a new VPC security group: `pathfinder-db-sg`.
9. Click **Create database**.
10. **Post-Creation:** Once available, click the database, locate the **Endpoint** URL. Update your EC2 `.env` file with this connection string:
    `SQLALCHEMY_DATABASE_URI="postgresql://postgres:<PASSWORD>@<ENDPOINT>:5432/postgres"`

---

## 2. Deploying the Backend (AWS EC2)
*This hosts our Python Flask API, Harvester Engine, and local ChromaDB files.*

1. Navigate to **EC2** and click **Launch Instances**.
2. **Name:** `pathfinder-backend`.
3. **AMI:** Select **Ubuntu Server 22.04 LTS** (64-bit x86).
4. **Instance Type:** `t2.medium` or `t3.medium`.
   *(Note: ChromaDB and sentence-transformers require at least 2GB-4GB of RAM to load the ML models into memory without crashing. Do not use t2.micro).*
5. **Key Pair:** Create a new RSA key pair (`pathfinder-key.pem`), download it, and keep it safe.
6. **Network Settings:**
   - Create a new security group.
   - Allow **SSH traffic** from anywhere.
   - Allow **HTTP/HTTPS traffic** from anywhere.
   - Allow Custom TCP on port `5000` (optional, for direct Gunicorn testing).
7. **Storage:** Increase the Root volume to **16 GiB** (ChromaDB vectors take space).
8. Click **Launch instance**.

### Configuring the EC2 Server
Once the instance is running, SSH into it:
```bash
ssh -i "pathfinder-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
```

Run the following setup commands:
```bash
# 1. Update system & install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx libpq-dev -y

# 2. Clone the repository
git clone https://github.com/YOUR_USERNAME/Pathfinder.Ai.git
cd Pathfinder.Ai/backend

# 3. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python requirements
pip install -r requirements.txt
pip install gunicorn psycopg2

# 5. Create .env file
nano .env
```
Paste your production variables into `.env`:
```ini
FLASK_ENV=production
SECRET_KEY=your_super_secret_key
SQLALCHEMY_DATABASE_URI=postgresql://postgres:<PASSWORD>@<ENDPOINT>:5432/postgres
JWT_SECRET_KEY=your_jwt_secret_key
HF_TOKEN=your_huggingface_token
# Add your RapidAPI keys here (JSEARCH, etc.)
```

### Running the Backend with Gunicorn
To keep the server running continuously, use `systemd`:
```bash
sudo nano /etc/systemd/system/pathfinder.service
```
Add the following configuration:
```ini
[Unit]
Description=Gunicorn instance to serve Pathfinder.Ai
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Pathfinder.Ai/backend
Environment="PATH=/home/ubuntu/Pathfinder.Ai/backend/venv/bin"
# ChromaDB requires a writable persistent directory
Environment="CHROMA_DB_DIR=/home/ubuntu/Pathfinder.Ai/backend/chroma_db"
ExecStart=/home/ubuntu/Pathfinder.Ai/backend/venv/bin/gunicorn --workers 3 --bind unix:pathfinder.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start pathfinder
sudo systemctl enable pathfinder
```

### Configuring Nginx (Reverse Proxy)
```bash
sudo nano /etc/nginx/sites-available/pathfinder
```
```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP; # Or your domain name

    location / {
        proxy_pass http://unix:/home/ubuntu/Pathfinder.Ai/backend/pathfinder.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/pathfinder /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

## 3. Deploying the Frontend (AWS Amplify)
*This globally hosts our Vue.js SPA.*

1. Push all your latest changes to your GitHub repository.
2. Navigate to **AWS Amplify** in the AWS Console.
3. Click **Host web app** -> **GitHub**.
4. Authorize AWS and select the `Pathfinder.Ai` repository and your working branch (`prototype` or `master`).
5. Check the box indicating your app is a Monorepo. Enter `frontend` as the root directory.
6. **Build Settings:**
   Click "Edit" on the build settings YAML and ensure it looks like this:
   ```yaml
   version: 1
   applications:
     - frontend:
         phases:
           preBuild:
             commands:
               - npm ci
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: dist
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
       appRoot: frontend
   ```
7. **Environment Variables:**
   In the "Advanced settings", add:
   - Key: `VUE_APP_API_URL`
   - Value: `http://<YOUR_EC2_PUBLIC_IP>` (The URL to your Nginx EC2 server).
8. **Redirects for Vue Router:**
   Once deployed, go to **Hosting -> Rewrites and redirects** in Amplify. Add this rule so Vue Router works correctly on page reloads:
   - Source address: `</^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|ttf|map|json)$)([^.]+$)/>`
   - Target address: `/index.html`
   - Type: `200 (Rewrite)`
9. Click **Save and deploy**.

### Final Verification
1. Access your AWS Amplify URL.
2. Register a new user to test the RDS database connection.
3. Update the user profile with skills and a summary.
4. Check the EC2 logs (`sudo journalctl -u pathfinder -f`) to ensure ChromaDB successfully generates and saves the embedding vector.

**Deployment Complete!**