# Stridecraft web

Vite + React + TypeScript (journal/0014). Needs the API running on :8000.

```
npm install
npm run dev        # http://localhost:5173
npm run gen:api    # regenerate src/api/schema.d.ts from the running API
npm run lint && npm run typecheck && npm test
```

Log in through `/login`; the dashboard is `/`, onboarding is `/adopt` and the journey map is `/voyage`
(journal/0018).
`VITE_API_URL` overrides the API URL.
