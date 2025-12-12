"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { programsAPI, groupsAPI } from "@/lib/api";
import type { Program, Group } from "@/lib/types";

export default function AnalyticsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedProgram, setSelectedProgram] = useState<string>("");
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    loadPrograms();
  }, []);

  useEffect(() => {
    if (selectedProgram) {
      loadGroups(selectedProgram);
    }
  }, [selectedProgram]);

  useEffect(() => {
    if (selectedGroup) {
      loadAnalytics(selectedGroup);
    }
  }, [selectedGroup]);

  const loadPrograms = async () => {
    try {
      const data = await programsAPI.list();
      setPrograms(data.programs);
    } catch (error) {
      console.error("Failed to load programs:", error);
    }
  };

  const loadGroups = async (programId: string) => {
    try {
      const data = await groupsAPI.listByProgram(parseInt(programId));
      setGroups(data.groups);
    } catch (error) {
      console.error("Failed to load groups:", error);
    }
  };

  const loadAnalytics = async (groupId: string) => {
    try {
      setLoading(true);
      const data = await groupsAPI.getAnalytics(parseInt(groupId));
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeVariant = (riskLevel: string) => {
    switch (riskLevel) {
      case "high_risk":
        return "destructive";
      case "medium_risk":
        return "default";
      case "crushing_it":
        return "outline";
      default:
        return "secondary";
    }
  };

  const getRiskLabel = (riskLevel: string) => {
    switch (riskLevel) {
      case "high_risk":
        return "High Risk";
      case "medium_risk":
        return "Medium Risk";
      case "crushing_it":
        return "Crushing It";
      default:
        return "On Track";
    }
  };

  // Calculate aggregate stats
  const totalGoals = analytics?.members.reduce((sum: number, m: any) => sum + m.stats.total_goals, 0) || 0;
  const totalChallenges = analytics?.members.reduce((sum: number, m: any) => sum + m.stats.challenges, 0) || 0;
  const avgAttendance = analytics?.members.length > 0
    ? (analytics.members.reduce((sum: number, m: any) => sum + m.stats.attendance_rate, 0) / analytics.members.length).toFixed(1)
    : "0";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Track performance and identify at-risk members
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Select Group</CardTitle>
          <CardDescription>Choose a group to view analytics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Program</Label>
              <Select value={selectedProgram} onValueChange={setSelectedProgram}>
                <SelectTrigger>
                  <SelectValue placeholder="Select program" />
                </SelectTrigger>
                <SelectContent>
                  {programs.map((program) => (
                    <SelectItem key={program.id} value={program.id.toString()}>
                      {program.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedProgram && (
              <div className="space-y-2">
                <Label>Group</Label>
                <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select group" />
                  </SelectTrigger>
                  <SelectContent>
                    {groups.map((group) => (
                      <SelectItem key={group.id} value={group.id.toString()}>
                        {group.name} {group.cohort && `(${group.cohort})`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {selectedGroup && loading && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <Skeleton className="h-[100px]" />
            <Skeleton className="h-[100px]" />
            <Skeleton className="h-[100px]" />
            <Skeleton className="h-[100px]" />
          </div>
          <Skeleton className="h-[300px]" />
        </div>
      )}

      {selectedGroup && !loading && analytics && (
        <>
          {/* Overview Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.total_sessions}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Attendance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{avgAttendance}%</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Goals Set</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalGoals}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Challenges</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalChallenges}</div>
              </CardContent>
            </Card>
          </div>

          {/* Member Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Member Performance</CardTitle>
              <CardDescription>
                Track individual member engagement and risk levels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.members.map((member: any) => (
                  <div key={member.member_id} className="flex items-center justify-between border-b pb-4 last:border-0">
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-sm text-muted-foreground">{member.role}</p>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <div className="text-center">
                        <p className="text-muted-foreground">Sessions</p>
                        <p className="font-semibold">{member.stats.total_sessions}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-muted-foreground">Goals</p>
                        <p className="font-semibold">{member.stats.completed_goals}/{member.stats.total_goals}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-muted-foreground">Attendance</p>
                        <p className="font-semibold">{member.stats.attendance_rate}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-muted-foreground">Wins</p>
                        <p className="font-semibold">{member.stats.wins}</p>
                      </div>
                      <Badge variant={getRiskBadgeVariant(member.risk_level)} className={member.risk_level === "crushing_it" ? "bg-green-50 text-green-700 border-green-200" : ""}>
                        {getRiskLabel(member.risk_level)}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Risk Criteria Info */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Rating Criteria</CardTitle>
              <CardDescription>
                How we determine member risk levels
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Badge variant="destructive" className="mb-2">High Risk</Badge>
                <p className="text-sm text-muted-foreground">
                  • 2+ missed sessions without communication<br />
                  • No goals set for 2+ weeks<br />
                  • Stuck in same challenge for multiple sessions
                </p>
              </div>
              <div>
                <Badge className="mb-2">Medium Risk</Badge>
                <p className="text-sm text-muted-foreground">
                  • 1 missed session<br />
                  • 1 week without goals<br />
                  • No meetings scheduled
                </p>
              </div>
              <div>
                <Badge variant="secondary" className="mb-2">On Track</Badge>
                <p className="text-sm text-muted-foreground">
                  • Regular attendance<br />
                  • Consistent goal setting<br />
                  • Active participation
                </p>
              </div>
              <div>
                <Badge variant="outline" className="mb-2 bg-green-50">Crushing It</Badge>
                <p className="text-sm text-muted-foreground">
                  • Proposals out<br />
                  • Clients closed<br />
                  • Revenue generated
                </p>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
