"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { programsAPI, groupsAPI, membersAPI } from "@/lib/api";
import type { Program } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    programs: 0,
    groups: 0,
    members: 0,
    sessions: 0,
    loading: true,
  });

  const [recentPrograms, setRecentPrograms] = useState<Program[]>([]);

  useEffect(() => {
    async function loadStats() {
      try {
        // Load all data
        const [programsData, membersData] = await Promise.all([
          programsAPI.list(),
          membersAPI.list(),
        ]);

        // Count groups across all programs
        const groupCounts = await Promise.all(
          programsData.programs.map(p => groupsAPI.listByProgram(p.id))
        );
        const totalGroups = groupCounts.reduce((sum, { groups }) => sum + groups.length, 0);

        setStats({
          programs: programsData.programs.length,
          groups: totalGroups,
          members: membersData.members.length,
          sessions: 0, // Will calculate from all groups
          loading: false,
        });

        setRecentPrograms(programsData.programs.slice(0, 5));
      } catch (error) {
        console.error("Failed to load stats:", error);
        setStats(prev => ({ ...prev, loading: false }));
      }
    }

    loadStats();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your peer coaching platform
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Programs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.loading ? "..." : stats.programs}
            </div>
            <p className="text-xs text-muted-foreground">
              Active coaching programs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Groups</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.loading ? "..." : stats.groups}
            </div>
            <p className="text-xs text-muted-foreground">
              Active groups
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.loading ? "..." : stats.members}
            </div>
            <p className="text-xs text-muted-foreground">
              Total members
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.loading ? "..." : stats.sessions}
            </div>
            <p className="text-xs text-muted-foreground">
              Total sessions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Programs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Programs</CardTitle>
          <CardDescription>
            Your most recently created programs
          </CardDescription>
        </CardHeader>
        <CardContent>
          {stats.loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : recentPrograms.length > 0 ? (
            <div className="space-y-4">
              {recentPrograms.map((program) => (
                <div key={program.id} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                  <div>
                    <p className="font-medium">{program.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {program.slug}
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {program.is_active ? (
                      <span className="text-green-600">Active</span>
                    ) : (
                      <span className="text-gray-400">Inactive</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No programs yet. Create your first program to get started!
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
