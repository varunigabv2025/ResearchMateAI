import { redirect } from "next/navigation";

// Redirect /workspace/papers to /workspace
export default function PapersPage() {
  redirect("/workspace");
}
