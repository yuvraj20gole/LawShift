"use client";

import { ChatEntry } from "@/components/ChatEntry";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { AttachDocument } from "@/components/dashboard/AttachDocument";
import { PageHead } from "@/components/dashboard/DashParts";

export default function WorkspacePage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);

  return (
    <>
      <PageHead title={C.wsTitle} lede={C.wsLede} />
      <AttachDocument />
      <ChatEntry hideCounter hideExamples unlimited />
    </>
  );
}
