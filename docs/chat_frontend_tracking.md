# Chat Frontend Tracking Integration

This document explains how to collect visitor data in the browser and send it to the backend chat API.

## Goals
- Send identity (name/email/phone) when available.
- Auto-track context (URL, referrer, UTM, device info).
- Keep payload small and safe.

## Data to Collect (Client)
- `name` (optional, from a form)
- `email` (optional, from a form)
- `phone` (optional, from a form)
- `sourceUrl` (current page URL)
- `referrer` (previous page URL)
- `utmSource`, `utmMedium`, `utmCampaign` (from URL)
- `timezone`
- `language`
- `browser`, `os`, `device` (best-effort from user agent)
- `lastPage` (current path)

## Example JS Snippet
```js
function getUtmParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    utmSource: params.get("utm_source"),
    utmMedium: params.get("utm_medium"),
    utmCampaign: params.get("utm_campaign"),
  };
}

function getDeviceInfo() {
  const ua = navigator.userAgent || "";
  const isMobile = /Mobi|Android/i.test(ua);
  return {
    browser: ua.includes("Chrome") ? "Chrome" : ua.includes("Safari") ? "Safari" : "Other",
    os: ua.includes("Windows") ? "Windows" : ua.includes("Mac") ? "Mac" : "Other",
    device: isMobile ? "Mobile" : "Desktop",
  };
}

function buildVisitorPayload({ name, email, phone }) {
  const { utmSource, utmMedium, utmCampaign } = getUtmParams();
  const { browser, os, device } = getDeviceInfo();
  return {
    name,
    email,
    phone,
    sourceUrl: window.location.href,
    referrer: document.referrer || null,
    utmSource,
    utmMedium,
    utmCampaign,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    language: navigator.language,
    browser,
    os,
    device,
    lastPage: window.location.pathname,
  };
}
```

## Create Conversation (Frontend)
```js
const visitor = buildVisitorPayload({
  name: form.name,
  email: form.email,
  phone: form.phone,
});

const res = await fetch("/api/v1/chat/conversations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    businessId: 1,
    visitor,
  }),
});

const data = await res.json();
const conversationId = data.data.id;
```

## Update Visitor Profile (Frontend)
```js
const form = new FormData();
form.append("name", "Sokha");
form.append("email", "sokha@gmail.com");
form.append("phone", "+85512345678");
form.append("lastPage", window.location.pathname);

await fetch(`/api/v1/chat/visitors/${visitorId}`, {
  method: "PATCH",
  body: form,
});
```

## Update Visitor Avatar (Admin)
```js
const form = new FormData();
form.append("avatar", fileInput.files[0]);

await fetch(`/api/v1/chat/visitors/${visitorId}/avatar`, {
  method: "POST",
  headers: { Authorization: `Bearer ${adminToken}` },
  body: form,
});
```

## Notes
- The backend will also store `ip`, `country`, and `city` if you add GeoIP on the server.
- For privacy, avoid collecting more than you need and disclose tracking to users.
