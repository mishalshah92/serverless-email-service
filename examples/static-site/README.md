# Static Site Example

This Bootstrap example submits contact and booking forms with `fetch`.
Open `index.html` directly, or serve the folder with:

```sh
python -m http.server 8080
```

Public JavaScript may contain only public values:

- API URL
- public site identifier
- Turnstile site key

It must not contain SMTP credentials, SES credentials, destination addresses, sender identities, template IDs, or provider settings.
