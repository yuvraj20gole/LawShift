"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

/** `email`: the signed-in address, or null when anonymous. `ready` once the first check is done. */
export function useSession() {
  const [state, setState] = useState<{ email: string | null; ready: boolean }>({
    email: null,
    ready: false,
  });
  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getSession().then(({ data }) =>
      setState({ email: data.session?.user.email ?? null, ready: true }),
    );
    const { data: sub } = supabase.auth.onAuthStateChange((_e, session) =>
      setState({ email: session?.user.email ?? null, ready: true }),
    );
    return () => sub.subscription.unsubscribe();
  }, []);
  return state;
}
