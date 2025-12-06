# PKI + TOTP 2FA Microservice (FastAPI / Python)

Follow assignment spec. Key files to commit:
- student_private.pem (REQUIRED)
- student_public.pem (REQUIRED)
- instructor_public.pem (REQUIRED)

Do NOT commit:
- encrypted_seed.txt

Build & run (local Docker):
1. Generate keys (see keys/ or use `openssl`).
2. Create public GitHub repo and note exact URL.
3. Request encrypted seed from instructor API and save as `encrypted_seed.txt` (do NOT commit).
4. `docker-compose build`
5. `docker-compose up -d`
6. Test endpoints (see spec).

Ports:
- API: 8080 (HTTP)

Volumes:
- /data -> seed persistence
- /cron -> cron logs
