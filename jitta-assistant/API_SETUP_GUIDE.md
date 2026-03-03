# 🔑 Jitta Assistant API Setup Guide

This guide will help you obtain the necessary API keys to unlock Jitta's full potential in **Crypto Analysis** and **Social Media Management**.

---

## 1. CoinGecko API (for Crypto Analysis)

Jitta uses CoinGecko to fetch real-time crypto prices, market caps, and trends.

### Option A: Free Demo Account (Recommended for Testing)
1.  Go to **[CoinGecko API Pricing](https://www.coingecko.com/en/api/pricing)**.
2.  Scroll down to the **"Demo"** plan (Free) and click **"Get Started"**.
3.  Sign up for a CoinGecko account (or log in).
4.  Once logged in to the [Developer Dashboard](https://www.coingecko.com/en/developers/dashboard):
    *   Click **"Add New Key"**.
    *   Give it a name (e.g., `Jitta-Assistant`).
    *   **Copy the API Key**.
5.  Open `jitta-assistant/.env` and paste it:
    ```dotenv
    COINGECKO_API_KEY=CG-YourGeneratedKeyHere
    ```

### Option B: Pro Account
If you have a paid plan, follow the same steps but select your Pro plan.

---

## 2. Facebook Graph API (for Social Media Tools)

Jitta needs a "Page Access Token" to post updates or read comments on your managed Facebook Page.

### Step 1: Create a Meta App
1.  Go to **[Meta for Developers](https://developers.facebook.com/)**.
2.  Click **"My Apps"** > **"Create App"**.
3.  Select **"Other"** > **"Next"**.
4.  Select **"Business"** (managing a Page) > **"Next"**.
5.  Enter an **App Name** (e.g., `PeaceScript-Jitta`) and your email. Click **"Create App"**.

### Step 2: Add "Facebook Login for Business" Product
1.  In your new App Dashboard, scroll to "Add products to your app".
2.  Find **"Facebook Login for Business"** and click **"Set up"**.
3.  Save changes (you don't need to configure settings yet).

### Step 3: Get a User Access Token (Graph API Explorer)
*For development/testing, we use the Explorer to get a token quickly.*

1.  Go to **[Graph API Explorer](https://developers.facebook.com/tools/explorer/)**.
2.  Select your **Meta App** in the "Meta App" dropdown.
3.  In "User or Page", select **"Get User Access Token"**.
4.  **Permissions**: Add these permissions in the "Add a Permission" dropdown:
    *   `pages_show_list`
    *   `pages_read_engagement`
    *   `pages_manage_posts`
    *   `public_profile`
5.  Click **"Generate Access Token"** and approve the login pop-up.

### Step 4: Get the Page Access Token
1.  In the Explorer URL bar, change `me?fields=id,name` to:
    `me/accounts`
2.  Click **"Submit"**.
3.  You will see a JSON list of your Pages. Find the Page you want Jitta to manage.
4.  Copy the long string under **`access_token`** for that specific page.
    *   *Note: This is the Page Token, not the User Token.*

### Step 5: Save to .env
Open `jitta-assistant/.env` and paste:

```dotenv
FB_ACCESS_TOKEN=EAA... (Your Long Page Token)
FB_APP_ID=123456... (From App Dashboard > Settings > Basic)
FB_APP_SECRET=abcdef... (From App Dashboard > Settings > Basic)
```

---

## 3. Restart Jitta
After saving `.env`, restart the server to apply changes:

```powershell
cd jitta-assistant
python server.py
```
