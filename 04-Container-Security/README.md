# Securing Containers

This repository is a **hands-on, beginner-friendly guide** to securing containers.

We intentionally start with **insecure defaults**, then **progressively harden**
the container so each concept builds naturally on the previous one.

---

## What You Will Learn

- Why running containers as **root** is dangerous
- How to run containers as a **non-root user**
- Why `.dockerignore` is critical
- How **multi-stage builds** reduce attack surface
- Why **distroless images** are more secure
- How to **harden containers at runtime**

---

## Repository Structure

```text
sample-app/
├── app.js
├── package.json
└── README.md
```

---

## Sample Application

We use a **very small Node.js application** so the focus stays on
**container behavior and security**, not application complexity.

The app prints the **user ID** running inside the container, which makes
root vs non-root immediately visible.

---

## STEP 1: Insecure Container

This is how many people **first learn Docker**.
It works, but it is **not safe for production**.

---

### Dockerfile

```dockerfile
FROM node:25

WORKDIR /app
COPY . .

RUN npm install

EXPOSE 3000
CMD ["npm", "start"]
```

---

### 🚨 What’s Wrong Here?

| Issue | Why It’s a Problem |
|------|-------------------|
| Runs as root | App compromise = full container control |
| Single-stage build | Build tools stay in runtime |
| Copies everything | Secrets & junk may leak |
| Writable filesystem | Easy persistence |
| No limits | Container can impact host |

---

### ▶️ Build & Run

```bash
docker build -f Dockerfile -t insecure-app .
docker run -p 3000:3000 insecure-app
```

Output:

```
User ID: 0
```

👉 **User ID 0 means root**.

---

## STEP 2: Run as Non-Root User (Reduce Blast Radius)

Before optimizing images, the **first real security fix** is to
**stop running applications as root**.

### Why Non-Root Matters

If an attacker exploits your app:
- Root user → full container control
- Non-root user → **limited permissions**

This significantly reduces damage.

---

### Dockerfile.nonroot

```dockerfile
FROM node:25

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . .
RUN npm install

# Switch to non-root user
USER appuser

EXPOSE 3000
CMD ["npm", "start"]
```

---

### ▶️ Build & Run (Non-Root)

```bash
docker build -f Dockerfile -t nonroot-app .
docker run -p 3000:3000 nonroot-app
```

Output:

```
User ID: 1000
```

👉 The app now runs as a **non-root user**.

⚠️ Still not secure:
- Image is large
- Build tools remain
- OS utilities exist

---

## STEP 3: Add `.dockerignore` 

Now that we fixed **who runs the app**, we fix **what gets copied**.

### Why `.dockerignore` Is Important

Without it:
- `.git` history gets baked in
- `.env` files may leak secrets
- `node_modules` bloats images

---

### .dockerignore

```dockerignore
.git
.gitignore
node_modules
.env
Dockerfile*
README.md
```

---

### ✅ Benefits

| Benefit | Why It Matters |
|------|----------------|
| Smaller image | Faster builds, fewer CVEs |
| No secrets | Prevents accidental leaks |
| Clean context | Easier security review |

---

## STEP 4: Multi-Stage Builds (Reduce Attack Surface)

Next, we separate **build-time** and **runtime** concerns.

### What Multi-Stage Builds Do

- Build app in one image
- Run app in another
- Copy only what is needed

---

### Dockerfile.multistage

```dockerfile
# -------- Build Stage --------
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .

# -------- Runtime Stage --------
FROM node:25-slim

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "app.js"]
```

---

### ✅ Improvements

- Smaller runtime image
- Fewer tools for attackers
- Cleaner separation

---

## STEP 5: Distroless Images (Minimal & Secure)

Now we remove **almost the entire operating system**.

### Why Distroless Works

Distroless images have:
- No shell
- No package manager
- No OS tools

Attackers have very little to work with.

---

### Dockerfile (Multi-Stage + Distroless)

```dockerfile
# -------- Build Stage --------
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .

# -------- Runtime Stage --------
FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["app.js"]
```

---

### ▶️ Run (Distroless)

```
User ID: 65532
```

👉 Non-root by default, no shell available.

---

## STEP 6: Harden the Runtime (Defense in Depth)

Even secure images need runtime protection.

---

### Hardened Run Command

```bash
docker run \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 100 \
  --memory 256m \
  --cpus 0.5 \
  -p 3000:3000 \
  secure-app
```

---

## Final Takeaway

> **Secure container = Secure image + Hardened runtime**

Fix:
1. Who runs the app
2. What goes into the image
3. What stays in the image
4. What tools exist
5. What the app can do at runtime

---
