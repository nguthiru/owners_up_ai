import { notFound } from "next/navigation";
import { membersAPI } from "@/lib/api";
import { MemberAnalytics } from "@/components/member-analytics";

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function MemberPage({ params }: PageProps) {
  const { id } = await params;
  const memberId = parseInt(id);

  if (isNaN(memberId)) {
    notFound();
  }

  try {
    const member = await membersAPI.get(memberId);

    if (!member) {
      notFound();
    }

    return (
      <div className="space-y-6">
        <div className="border-b pb-4">
          <h1 className="text-3xl font-semibold">{member.name}</h1>
          <p className="text-muted-foreground">{member.email}</p>
        </div>

        <MemberAnalytics memberId={memberId} />
      </div>
    );
  } catch (error) {
    console.error("Error fetching member:", error);
    notFound();
  }
}
