// Cloudflare Pages Function - runs before every request to this Pages
// project, gating the whole site behind HTTP Basic Auth. AUTH_USER/AUTH_PASS
// are Pages secrets (set via `wrangler pages secret put`), never committed.
export async function onRequest(context) {
  const authHeader = context.request.headers.get("Authorization");

  if (!isAuthorized(authHeader, context.env)) {
    return new Response("Authentication required.", {
      status: 401,
      headers: { "WWW-Authenticate": 'Basic realm="Mood Search", charset="UTF-8"' },
    });
  }

  return context.next();
}

function isAuthorized(authHeader, env) {
  if (!authHeader || !authHeader.startsWith("Basic ")) return false;
  const decoded = atob(authHeader.slice(6));
  const sepIndex = decoded.indexOf(":");
  if (sepIndex === -1) return false;
  const user = decoded.slice(0, sepIndex);
  const pass = decoded.slice(sepIndex + 1);
  return user === env.AUTH_USER && pass === env.AUTH_PASS;
}
