import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { safeNext } from "@/lib/safeNext";

/** Email-confirmation link target: exchanges the code for a session, then enters the dashboard. */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(`${origin}${safeNext(searchParams.get("next")) ?? "/dashboard/workspace"}`);
    }
  }
  return NextResponse.redirect(`${origin}/login`);
}
