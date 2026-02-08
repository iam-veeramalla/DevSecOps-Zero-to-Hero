# AppSec for Beginners - Learn SAST, SCA & DAST

---

## Focus

This guide helps **absolute beginners** understand:
- What **SAST**, **SCA**, and **DAST** are
- Why we need *all three*
- How security tools actually find vulnerabilities
- How attackers exploit insecure applications
- How developers should fix issues

You will **build**, **scan**, **attack** a real application.

---

## Core Concepts (Before Touching Tools)

### What is SAST?
**Static Application Security Testing**
- Scans **source code**
- Does **not** run the application
- Finds insecure coding patterns
- Best used **early** (IDE / Pull Requests)

Examples:
- Hardcoded secrets
- SQL injection patterns
- Command execution risks
- Insecure Deserialization (pickle)
- Arbitrary Code Execution (eval/exec)
- Unsafe YAML Loading (yaml.load)
- Path Traversal (tarfile.extractall)
- Insecure SSL/TLS (verify=False)
- Weak Cryptography (MD5/SHA1 usage)
- Insecure Temp Files (tempfile.mktemp)

#### Detailed Information
- Hardcoded secrets: Storing sensitive data like passwords or API keys directly in your code where anyone who sees the file can steal them.
- SQL injection patterns: Building database queries by gluing strings together, which lets hackers "trick" your database into deleting data or leaking secrets.
- Command execution risks: Passing user input directly to your operating system, allowing a hacker to run any command (like format C:) on your server.
- Insecure Deserialization (pickle): Using the pickle tool on data from the internet, which can automatically run hidden malicious code the moment the file is opened.
- Arbitrary Code Execution (eval/exec): Using functions that turn text into live code, effectively giving a stranger the keyboard to your application.
- Unsafe YAML Loading (yaml.load): Opening configuration files in a way that allows the file itself to trigger Python commands during the reading process.
- Path Traversal (tarfile.extractall): Unzipping files without checking their names, which can let a malicious file overwrite important system files outside your project folder.
- Insecure SSL/TLS (verify=False): Turning off "security checks" for internet connections, making it easy for hackers to spy on your encrypted data.
- Weak Cryptography (MD5/SHA1 usage): Using "broken" mathematical formulas to hide data that modern computers can crack in seconds.
- Insecure Temp Files (tempfile.mktemp): Creating a temporary file name without instantly "locking" it, creating a tiny window of time for a hacker to swap it with a malicious file. 


---

### What is SCA?
**Software Composition Analysis**
- Scans **dependencies**
- Matches versions against **known CVEs**
- Answers: *“Are we using vulnerable packages?”*

> Even perfect code can be insecure because of vulnerable libraries.

---

### What is DAST?
**Dynamic Application Security Testing**
- Attacks a **running application**
- No access to source code
- Simulates real attackers
- Finds **exploitable vulnerabilities**

---

## Why We Need All Three

| Tool | Code | Dependencies | Running App |
|----|----|----|----|
| SAST | ✅ | ❌ | ❌ |
| SCA | ❌ | ✅ | ❌ |
| DAST | ❌ | ❌ | ✅ |

👉 **No single tool is enough.**

---

## Lab Overview

We will:
1. Build a vulnerable Python app
2. Run **SAST** using SonarQube
3. Run **SCA** using pip-audit
4. Run **DAST** using OWASP ZAP
5. Compare findings
6. Understand how to fix them

---

## 🏗️ Project Structure

```
vulnerable-app/
├── app.py
├── requirements.txt
├── users.db
└── sonar-project.properties
```

---

## Step 1: Vulnerable Application

### app.py
```python
from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)

DATABASE = "users.db"


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/")
def home():
    return "User Management Service"


@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    conn = get_db()
    cursor = conn.cursor()

    query = f"SELECT id, username FROM users WHERE id = '{user_id}'"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user[0], "username": user[1]})


@app.route("/token")
def generate_token():
    token = str(random.random())
    return jsonify({"token": token})


@app.route("/admin/calc")
def admin_calculate():
    expr = request.args.get("expr")
    result = eval(expr)
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)
```

---

## 📦 Step 2: Vulnerable Dependencies

### requirements.txt
```text
flask==1.0
requests==2.19.1
```

---

## 🔍 Step 3: SAST with SonarQube

### Start SonarQube
```bash
docker run -d -p 9000:9000 --name sonarqube sonarqube:9.9-community
```

Open http://localhost:9000  
Login: `admin / admin`

---

### sonar-project.properties
```properties
sonar.projectKey=vulnerable-python-app
sonar.projectName=Vulnerable Python App
sonar.sources=.
sonar.language=py
sonar.python.version=3
```

---

### Install Sonar Scanner

Follow the Instructions provided here:

https://docs.sonarsource.com/sonarqube-server/10.8/analyzing-source-code/scanners/sonarscanner

### Run Scan
```bash
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=<TOKEN>
```

### Expected Findings
- Hardcoded secrets
- SQL injection risks
- Command injection risks
- Debug mode enabled

---

## Step 4: SCA with pip-audit

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Expected Findings
- Vulnerable Flask version
- Vulnerable Requests version

---

## 🌐 Step 5: Run the App

```bash
pip install -r requirements.txt
python app.py
```

Application runs at http://localhost:5000

---

## 🕷️ Step 6: DAST with OWASP ZAP

Run the Juice Shop Application

```bash
docker run -d \
  --name juice-shop \
  -p 3000:3000 \
  bkimminich/juice-shop
```

Open in browser:

```
localhost:3000
```

Scan target by running ZAP from cli

```
docker run --rm \                                                                                      ✔  8509  15:33:58
  -v "$(pwd):/zap/wrk" \
  -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
  -t http://host.docker.internal:3000 \
  -r zap-report.html
```

Scan target by running ZAP from UI

```
docker run -it \                                                                             SIGINT(2) ↵  8509  15:36:05
  -p 8080:8080 \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-webswing.sh
```

Open Zap UI:

```
http://localhost:8080/zap
```

---

## Compare Results

| Issue | SAST | SCA | DAST |
|----|----|----|----|
| Hardcoded Secret | ✅ | ❌ | ❌ |
| Vulnerable Library | ❌ | ✅ | ❌ |
| SQL Injection | ✅ | ❌ | ✅ |
| Command Injection | ✅ | ❌ | ✅ |

---

## 🛠️ What to Fix Next

- Use parameterized SQL queries
- Remove `shell=True`
- Move secrets to environment variables
- Upgrade dependencies
- Disable debug mode

Re-run scans and observe improvements 🚀

---

