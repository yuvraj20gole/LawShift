import type { NextRequest } from "next/server";
import { redirectWithCookies, updateSession } from "@/lib/supabase/middleware";

export async function middleware(request: NextRequest) {
  const { response, signedIn } = await updateSession(request);
  const { pathname, search } = request.nextUrl;

  const isDashboard = pathname === "/dashboard" || pathname.startsWith("/dashboard/");
  if (isDashboard && !signedIn) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    url.searchParams.set("next", pathname + search);
    return redirectWithCookies(url, response);
  }

  // /reset-password and /forgot-password are deliberately not gated: the reset email lands on
  // /reset-password with a ?code= and a recovery session that is "signed in" once exchanged.
  if (signedIn && (pathname === "/login" || pathname === "/register")) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard/workspace";
    url.search = "";
    return redirectWithCookies(url, response);
  }

  return response;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|icon.svg|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)",
  ],
};
