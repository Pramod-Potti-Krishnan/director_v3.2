# Security Guide - Director Agent v3.3

## 🔐 Authentication Architecture

This application uses **Application Default Credentials (ADC)** for secure Google Cloud authentication, eliminating the security risks associated with static API keys.

### Why ADC is More Secure

| Aspect | Old (v3.1) | New (v3.3 ADC) |
|--------|-----------|----------------|
| **Credential Type** | Static API key | Rotatable service account |
| **Breach Risk** | High (key exposed = permanent access) | Low (keys can be instantly revoked) |
| **Auditability** | Limited | Full GCP audit logs |
| **Permissions** | API-level only | Fine-grained IAM roles |
| **Key Rotation** | Manual, risky | Standard GCP procedures |
| **Exposure Risk** | Keys in env vars, logs, errors | Credentials never in code/logs |

---

## 🏗️ Architecture Overview

### Dual-Environment Design

The same codebase works in both local and production environments without code changes:

```
┌─────────────────────────────────────────────────────────────┐
│                    Director Agent v3.3                      │
│                                                              │
│  ┌────────────────────┐          ┌────────────────────┐   │
│  │  LOCAL DEVELOPMENT │          │  RAILWAY PRODUCTION │   │
│  ├────────────────────┤          ├────────────────────┤   │
│  │ gcloud auth ADC    │          │ Service Account    │   │
│  │ Personal credentials│          │ GCP_SERVICE_       │   │
│  │ No env var needed  │          │ ACCOUNT_JSON       │   │
│  └─────────┬──────────┘          └──────────┬─────────┘   │
│            │                                 │              │
│            └────────────┬────────────────────┘              │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                      │
│              │  Vertex AI SDK       │                      │
│              │  (google-cloud-      │                      │
│              │   aiplatform)        │                      │
│              └──────────────────────┘                      │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                      │
│              │  Google Cloud        │                      │
│              │  Vertex AI API       │                      │
│              │  (deckster-xyz)      │                      │
│              └──────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Local Development Setup

### Prerequisites
1. **gcloud CLI** installed
2. **Google Cloud account** with access to `deckster-xyz` project
3. **Vertex AI API** enabled in the project

### Step-by-Step Setup

#### 1. Install gcloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

#### 2. Authenticate with Google Cloud

```bash
# Login with your Google account
gcloud auth application-default login

# Set the project
gcloud config set project deckster-xyz

# Verify authentication
gcloud auth application-default print-access-token
```

This will:
- Open a browser for Google authentication
- Store credentials in `~/.config/gcloud/application_default_credentials.json`
- Allow the application to access GCP services as YOU

#### 3. Verify Setup

```bash
# Check which account is active
gcloud auth list

# Verify project is set
gcloud config get-value project

# Test Vertex AI access
gcloud ai models list --region=us-central1
```

#### 4. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure `GCP_ENABLED=true` in your `.env`:
```bash
GCP_ENABLED=true
GCP_PROJECT_ID=deckster-xyz
GCP_LOCATION=us-central1
# DO NOT set GCP_SERVICE_ACCOUNT_JSON for local development
```

#### 5. Start the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

You should see:
```
✓ Vertex AI initialized successfully with ADC
  Project: deckster-xyz, Location: us-central1
```

---

## 🚀 Railway Production Setup

### Prerequisites
1. **Service Account** created in GCP Console
2. **Service Account JSON key** downloaded
3. **Railway project** set up

### Step-by-Step Setup

#### 1. Create Service Account in GCP

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=deckster-xyz
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Fill in details:
   - **Name**: `director-agent-production`
   - **Description**: `Production service account for Director Agent v3.3`
4. Click **"CREATE AND CONTINUE"**
5. Grant roles:
   - Add role: **Vertex AI User** (`roles/aiplatform.user`)
   - **DO NOT** grant Editor or Owner roles (least privilege principle)
6. Click **"CONTINUE"** then **"DONE"**

#### 2. Create Service Account Key

1. Click on the newly created service account
2. Go to **"KEYS"** tab
3. Click **"ADD KEY"** → **"Create new key"**
4. Select **"JSON"** format
5. Click **"CREATE"**
6. **SAVE THE DOWNLOADED JSON FILE SECURELY**
7. **DO NOT** commit this file to version control

#### 3. Configure Railway Environment Variables

1. Go to your Railway project
2. Navigate to **"Variables"** tab
3. **DELETE** old insecure variables:
   - `GOOGLE_API_KEY` ❌ (if exists)
4. **ADD** new secure variable:
   - **Name**: `GCP_SERVICE_ACCOUNT_JSON`
   - **Value**: **Copy the ENTIRE contents of the downloaded JSON file**
   - Example:
     ```json
     {"type":"service_account","project_id":"deckster-xyz","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"director-agent-production@deckster-xyz.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
     ```

5. Ensure these variables are set:
   ```
   GCP_ENABLED=true
   GCP_PROJECT_ID=deckster-xyz
   GCP_LOCATION=us-central1
   GCP_SERVICE_ACCOUNT_JSON=<FULL JSON CONTENT>
   ```

#### 4. Deploy and Verify

1. Deploy your application to Railway
2. Check logs for successful initialization:
   ```
   🔐 Initializing Vertex AI with service account (Production mode)
   ✓ Vertex AI initialized successfully with service account: director-agent-production@deckster-xyz.iam.gserviceaccount.com
   ```

---

## 🛡️ Security Best Practices

### 1. API Quotas and Cost Controls

Set conservative quotas to prevent runaway costs:

1. Go to: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas?project=deckster-xyz
2. Find **"Generate content requests per day per project"**
3. Click **"EDIT QUOTAS"**
4. Set to reasonable daily limit (e.g., 10,000 requests/day)
5. Set up **Billing Alerts** in GCP Console:
   - Navigation Menu → Billing → Budgets & alerts
   - Create alert at 50%, 80%, 100% of expected budget

### 2. Railway Security

**Enable Multi-Factor Authentication (MFA):**
1. Go to Railway account settings
2. Enable 2FA using authenticator app
3. **ENFORCE** MFA for all project collaborators

**Use Private Networking:**
- For database connections, use Railway's private networking
- Never expose internal services to public internet

**Environment Variable Security:**
- Use Railway's secrets for sensitive values
- Never log or print environment variables
- Regularly rotate service account keys (every 90 days)

### 3. Service Account Permissions

**Principle of Least Privilege:**
- ✅ Grant ONLY `Vertex AI User` role
- ❌ NEVER grant `Editor`, `Owner`, or `Admin` roles
- ❌ NEVER grant `Service Account Token Creator` unless absolutely necessary

**Audit Permissions Regularly:**
```bash
# List service account permissions
gcloud projects get-iam-policy deckster-xyz \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:director-agent-production@deckster-xyz.iam.gserviceaccount.com"
```

### 4. Credential Management

**DO:**
- ✅ Store service account JSON in secure environment variables only
- ✅ Rotate service account keys every 90 days
- ✅ Use different service accounts for dev/staging/prod
- ✅ Enable Cloud Audit Logs for all Vertex AI API calls
- ✅ Monitor service account usage regularly

**DO NOT:**
- ❌ Commit service account JSON to version control
- ❌ Share service account keys via email, Slack, etc.
- ❌ Hardcode credentials in application code
- ❌ Use the same service account for multiple environments
- ❌ Grant unnecessary permissions to service accounts

### 5. Monitoring and Auditing

**Enable Cloud Audit Logs:**
1. Go to: https://console.cloud.google.com/iam-admin/audit?project=deckster-xyz
2. Find **"AI Platform (Vertex AI)"**
3. Enable:
   - ✅ Admin Read
   - ✅ Data Read
   - ✅ Data Write

**Review Logs Regularly:**
```bash
# View Vertex AI audit logs
gcloud logging read "resource.type=aiplatform.googleapis.com AND protoPayload.authenticationInfo.principalEmail=director-agent-production@deckster-xyz.iam.gserviceaccount.com" --limit 50
```

**Set Up Alerts:**
- Unusual API usage patterns
- Failed authentication attempts
- Quota approaching limits

---

## 🔄 Credential Rotation

### When to Rotate

- **Scheduled**: Every 90 days (recommended)
- **Compromised**: Immediately if credentials are exposed
- **Team Changes**: When team members leave

### How to Rotate Service Account Keys

1. **Create new key** (follow Railway setup steps above)
2. **Update Railway** with new `GCP_SERVICE_ACCOUNT_JSON`
3. **Deploy** updated configuration
4. **Verify** new credentials working
5. **Delete old key** in GCP Console:
   ```bash
   gcloud iam service-accounts keys delete KEY_ID \
     --iam-account=director-agent-production@deckster-xyz.iam.gserviceaccount.com
   ```

---

## 🚨 Incident Response

### If Credentials Are Compromised

**Immediate Actions (within 5 minutes):**
1. **Disable the service account**:
   ```bash
   gcloud iam service-accounts disable director-agent-production@deckster-xyz.iam.gserviceaccount.com
   ```
2. **Delete all keys**:
   ```bash
   gcloud iam service-accounts keys list \
     --iam-account=director-agent-production@deckster-xyz.iam.gserviceaccount.com

   # Delete each key
   gcloud iam service-accounts keys delete KEY_ID \
     --iam-account=director-agent-production@deckster-xyz.iam.gserviceaccount.com
   ```
3. **Review audit logs** for unauthorized access

**Follow-Up Actions (within 24 hours):**
1. Create new service account with fresh credentials
2. Update Railway environment variables
3. Conduct security review to identify breach source
4. Document incident and update procedures

### If Unusual Activity Detected

1. **Check audit logs**:
   ```bash
   gcloud logging read "resource.type=aiplatform.googleapis.com" --limit 100
   ```
2. **Review API usage**:
   - Go to GCP Console → APIs & Services → Dashboard
   - Look for unexpected spikes in Vertex AI API calls
3. **Verify service account permissions** haven't been escalated
4. **Contact security team** if suspicious activity confirmed

---

## 📊 Cost Monitoring

### Set Up Budget Alerts

1. Navigate to: https://console.cloud.google.com/billing?project=deckster-xyz
2. Click **"Budgets & alerts"**
3. Create budget:
   - **Name**: `Vertex AI Monthly Budget`
   - **Amount**: Set appropriate monthly limit
   - **Thresholds**: 50%, 80%, 90%, 100%
   - **Actions**: Email alerts to team

### Monitor Usage

**Check current month's spending:**
```bash
gcloud billing accounts list

# View detailed costs (requires billing admin role)
gcloud alpha billing accounts projects link deckster-xyz
```

**View Vertex AI usage metrics:**
- Go to: GCP Console → Vertex AI → Dashboard
- Review request counts, latency, error rates

---

## ❓ Troubleshooting

### Error: "FATAL: Cannot initialize Vertex AI with ADC"

**Local Development:**
```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials file exists
ls ~/.config/gcloud/application_default_credentials.json

# Check project is set
gcloud config get-value project
```

**Railway Production:**
- Verify `GCP_SERVICE_ACCOUNT_JSON` environment variable is set
- Check JSON is valid and complete
- Ensure service account has `Vertex AI User` role

### Error: "Service account credentials invalid"

1. **Verify JSON format**:
   - Must be valid JSON (no line breaks in middle of values)
   - Must include all required fields
2. **Check service account status**:
   ```bash
   gcloud iam service-accounts describe director-agent-production@deckster-xyz.iam.gserviceaccount.com
   ```
3. **Verify IAM permissions**:
   - Ensure `Vertex AI User` role is granted
   - Check for any deny policies

### Error: "Permission denied on Vertex AI API"

1. **Check API is enabled**:
   ```bash
   gcloud services list --enabled | grep aiplatform
   ```
2. **Enable if needed**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```
3. **Verify service account permissions**

---

## 📚 Additional Resources

- **GCP IAM Best Practices**: https://cloud.google.com/iam/docs/best-practices
- **Vertex AI Documentation**: https://cloud.google.com/vertex-ai/docs
- **Service Account Key Management**: https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys
- **Cloud Audit Logs**: https://cloud.google.com/logging/docs/audit

---

## 📝 Checklist: Security Compliance

Use this checklist to verify security compliance:

### Initial Setup
- [ ] Service account created with minimal permissions
- [ ] `Vertex AI User` role granted (and ONLY this role)
- [ ] Service account key downloaded and secured
- [ ] `GCP_SERVICE_ACCOUNT_JSON` added to Railway
- [ ] Old `GOOGLE_API_KEY` removed from Railway
- [ ] MFA enabled on Railway account

### Regular Maintenance (Monthly)
- [ ] Review GCP audit logs for anomalies
- [ ] Check Vertex AI API usage and costs
- [ ] Verify no unauthorized permission changes
- [ ] Confirm budget alerts are working

### Quarterly
- [ ] Rotate service account keys
- [ ] Review and update IAM permissions
- [ ] Audit all service accounts in project
- [ ] Update security documentation

### Incident Response Ready
- [ ] Incident response plan documented
- [ ] Emergency contacts established
- [ ] Backup authentication method available
- [ ] Rollback procedure tested

---

**Version**: v3.3
**Last Updated**: 2025-01-31
**Next Security Review**: 2025-04-30
