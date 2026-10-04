import { redirect } from "next/navigation";

/** /dashboard lands on Workspace; the logo still points here. */
export default function DashboardIndex() {
  redirect("/dashboard/workspace");
}
