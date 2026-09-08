import { Application, Router } from "oak";

const app = new Application();
const router = new Router();

const PYTHON_API = Deno.env.get("PYTHON_API") || "http://localhost:8000";

router.get("/", (ctx) => {
  ctx.response.body = `
    <html dir="rtl" lang="fa">
    <head><meta charset="utf-8"><title>HDP Local RAG</title></head>
    <body style="font-family:sans-serif;max-width:600px;margin:auto;padding:20px">
      <h1>🧠 HDP Local RAG</h1>
      <p>سیستم هوش مصنوعی محلی هرمزگان</p>
      <form id="f">
        <input id="q" placeholder="سؤال بپرسید..." style="width:80%;padding:10px">
        <button type="submit">بپرس</button>
      </form>
      <pre id="r"></pre>
      <script>
        document.getElementById('f').onsubmit = async (e) => {
          e.preventDefault();
          const q = document.getElementById('q').value;
          const res = await fetch('/ask', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({query: q})
          });
          const data = await res.json();
          document.getElementById('r').textContent = JSON.stringify(data, null, 2);
        };
      </script>
    </body></html>
  `;
  ctx.response.type = "text/html";
});

router.post("/ask", async (ctx) => {
  const body = await ctx.request.body.json();
  const res = await fetch(`${PYTHON_API}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  ctx.response.body = await res.json();
});

router.get("/health", (ctx) => {
  ctx.response.body = { status: "ok", deno: true };
});

app.use(router.routes());
app.use(router.allowedMethods());

const port = parseInt(Deno.env.get("DENO_PORT") || "3000");
console.log(`🚀 Deno server running on http://localhost:${port}`);
await app.listen({ port });
