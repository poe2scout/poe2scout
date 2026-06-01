type PagesFunctionContext = {
  request: Request;
  env: {
    API_ORIGIN?: string;
  };
};

const HOP_BY_HOP_HEADERS = [
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
];

function buildTargetUrl(requestUrl: string, apiOrigin: string) {
  const incomingUrl = new URL(requestUrl);
  const targetUrl = new URL(apiOrigin);
  const originPath = targetUrl.pathname.replace(/\/$/, "");
  const apiPath = incomingUrl.pathname.replace(/^\/api(?=\/|$)/, "") || "/";

  targetUrl.pathname = `${originPath}${apiPath}`;
  targetUrl.search = incomingUrl.search;

  return targetUrl;
}

function buildProxyHeaders(request: Request, targetUrl: URL) {
  const headers = new Headers(request.headers);
  const clientIp = headers.get("cf-connecting-ip");
  const forwardedFor = headers.get("x-forwarded-for");

  for (const header of HOP_BY_HOP_HEADERS) {
    headers.delete(header);
  }

  headers.delete("host");
  headers.set("x-forwarded-host", new URL(request.url).host);
  headers.set("x-forwarded-proto", new URL(request.url).protocol.replace(":", ""));
  headers.set("x-forwarded-prefix", "/api");
  headers.set("x-forwarded-server", targetUrl.host);

  if (clientIp) {
    headers.set("cf-connecting-ip", clientIp);
    headers.set("x-forwarded-for", forwardedFor ? `${forwardedFor}, ${clientIp}` : clientIp);
  }

  return headers;
}

function buildProxyResponse(response: Response) {
  const headers = new Headers(response.headers);

  for (const header of HOP_BY_HOP_HEADERS) {
    headers.delete(header);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export async function onRequest(context: PagesFunctionContext) {
  const apiOrigin = context.env.API_ORIGIN;

  if (!apiOrigin) {
    return new Response("API_ORIGIN is not configured", { status: 500 });
  }

  const targetUrl = buildTargetUrl(context.request.url, apiOrigin);
  const method = context.request.method.toUpperCase();
  const response = await fetch(targetUrl, {
    method,
    headers: buildProxyHeaders(context.request, targetUrl),
    body: method === "GET" || method === "HEAD" ? undefined : context.request.body,
    redirect: "manual",
  });

  return buildProxyResponse(response);
}
