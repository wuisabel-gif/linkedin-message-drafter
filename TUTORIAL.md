# Tutorial

## 1. Run the draft-only version

```bash
cd ~/linkedin-message-drafter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$PWD/src"
python -m linkedin_message_drafter.cli src/linkedin_message_drafter/examples/prospect.json
```

Edit the JSON to describe a real prospect using information you are allowed to use. Review the generated text for accuracy, relevance, and tone before manually pasting it into LinkedIn. Do not include sensitive personal data.

## 2. Configure LinkedIn access yourself

1. Sign in to LinkedIn and review the current **Developer** documentation and applicable platform terms.
2. Create or select an application in the LinkedIn developer portal.
3. Configure the exact redirect URL for your local app (for example, `http://localhost:8000/oauth/callback`) if your approved product requires OAuth.
4. Request only the products/scopes your use case needs. Messaging permissions are not automatically available to every application; use the official approval process.
5. Keep the client secret server-side. Put secrets in environment variables or a local secret manager—never in this repository, JSON input, screenshots, or Git history.
6. Complete OAuth using LinkedIn’s documented authorization-code flow. Your application should display the requested scopes and let the user cancel.
7. Store tokens securely, honor expiry/revocation, and provide a disconnect/delete-data action.

This scaffold intentionally does not guess LinkedIn endpoints or permissions. Those change by product and approval status. The plug-in boundary is `src/linkedin_message_drafter/linkedin.py`.

## 3. Add an approved adapter

Implement `LinkedInClient.send_message` only after LinkedIn has explicitly approved the relevant API capability. Keep these safeguards:

- Require an explicit user click/confirmation for every send.
- Send only to a selected recipient; do not add bulk loops or unattended scheduling.
- Respect rate limits, opt-outs, and applicable privacy/marketing laws.
- Record the approval timestamp and the final text sent.
- Fail closed when permission, recipient identity, or consent is unclear.

A safe application flow is:

```text
prospect data -> draft -> user edits -> user confirms -> approved adapter -> one send
```

## 4. Publish your repository

```bash
cd ~/linkedin-message-drafter
git init
git add .
git commit -m "Initial draft-first LinkedIn message assistant"
git branch -M main
# Create an empty private GitHub repository first, then:
git remote add origin git@github.com:YOUR_ACCOUNT/linkedin-message-drafter.git
git push -u origin main
```

Use a private repository while developing. Before publishing, confirm that `.env`, access tokens, and generated drafts are excluded from Git.
