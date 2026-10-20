# Stridecraft web

Vite + React + TypeScript (journal/0014). Needs the API running on :8000.

```
npm install
npm run dev        # http://localhost:5173
npm run gen:api    # regenerate src/api/schema.d.ts from the running API
npm run lint && npm run typecheck && npm test
```

`/dev/picker` (dev only) shows the breed picker with fake breeds. `VITE_API_URL` overrides the API URL.
