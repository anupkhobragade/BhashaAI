# 📘 BhashaAI – भारत का अपना ChatGPT

**BhashaAI** is a free and open AI-powered assistant that simplifies English, legal, or government content into easy-to-understand **regional Indian languages** like Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, and more. Built to empower citizens with language-accessible AI, BhashaAI is mobile-friendly and needs no login.

## 🌟 Features

- 🔤 **Translate & Explain Text or PDFs**  
  Get clear explanations of complex content in your native language.

- 🔊 **Text-to-Speech (TTS)**  
  Hear the translations spoken aloud.

- 🌍 **Supports 10+ Indian Languages**  
  Including Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Urdu, Gujarati, Malayalam, and Odia.

- 📄 **PDF + Text Input**  
  Upload PDFs or directly paste text for instant results.

- 💡 **AI-Powered, Yet 100% Free**  
  No signups, no ads, just useful functionality.

## 📱 Access the App

👉 [Launch BhashaAI on Streamlit](https://bhashaai.streamlit.app/app)


## ⚙️ Keep-Alive on GitHub Actions

If you keep BhashaAI deployed on Streamlit Community Cloud, this repo now includes a GitHub Actions workflow that sends a request to the live app every 5 minutes to reduce the chance of the app going to sleep.

### Workflow details

- Workflow file: `.github/workflows/keep-streamlit-awake.yml`
- Target URL: `https://bhashaai.streamlit.app/app`
- Trigger: every 5 minutes, plus manual `workflow_dispatch`
- Request behavior: sends a browser-like GET request to the Streamlit app URL and fails the workflow if GitHub cannot reach the app successfully

### Setup

1. Push this repository to GitHub.
2. Open the **Actions** tab and enable workflows if GitHub asks.
3. Run **Keep Streamlit app awake** once manually to verify the ping succeeds.
4. Keep GitHub Actions enabled for the repository.

### Important notes

- This is a practical keep-alive approach for the current `bhashaai.streamlit.app` deployment, but it is not a hard uptime guarantee if the hosting platform restarts or changes its hibernation behavior.
- GitHub may disable scheduled workflows in repositories that stay inactive for long periods, so check the Actions tab if the pings ever stop.
- If the workflow starts failing with HTTP 403 or similar access errors, GitHub-hosted runners may be blocked from reaching the app; in that case, switch to a dedicated uptime service or a self-hosted runner.

## ⚙️ Keep-Alive on Render

If you deploy BhashaAI on Render's free or spin-down-prone infrastructure, the web service can go idle after a period of inactivity. This repo now includes a Render cron job that pings the live app every 5 minutes to reduce cold starts.

### Setup

1. Sync `render.yaml` in Render so the new `bhashaai-keepalive` cron job is created.
2. In the Render dashboard, set `KEEP_ALIVE_URL` for the cron job to your live app URL, for example `https://bhashaai.onrender.com/`.
3. Redeploy or trigger the cron job once manually to verify the ping succeeds.

### Important note

This approach helps keep the app warm only if your hosting plan allows periodic external requests to wake and maintain the service. If your hosting tier enforces hard sleeping limits, upgrading the instance plan is the only guaranteed always-on option.

## 🧑‍🤝‍🧑 Who It's For

- 👵 Senior citizens confused by English documents  
- 👨‍🌾 Farmers with government letters  
- 🧾 Citizens receiving legal/government forms  
- 🧑‍🎓 Students with complex academic material

## 📬 Contact

For feedback, suggestions, or collaborations:  
📧 **anupkhobragade@gmail.com**  
🌐 [BhashaAI Blog](https://bhashaai.blogspot.com/)  
📍 Made in Pune, India

## 🛡️ License

This is a public-facing free tool. Attribution appreciated. No commercial use without permission.

---