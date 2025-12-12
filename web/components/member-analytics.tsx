"use client";

import { useEffect, useState } from "react";
import { membersAPI } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Target,
  AlertCircle,
  TrendingUp,
  Calendar,
  CheckCircle2,
  XCircle,
} from "lucide-react";

interface MemberAnalyticsProps {
  memberId: number;
}

export function MemberAnalytics({ memberId }: MemberAnalyticsProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{
    goals: any[];
    challenges: any[];
    marketing: any[];
    stucks: any[];
    attendance: any[];
  }>({
    goals: [],
    challenges: [],
    marketing: [],
    stucks: [],
    attendance: [],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [goalsRes, challengesRes, marketingRes, stucksRes, attendanceRes] =
          await Promise.all([
            membersAPI.getGoals(memberId),
            membersAPI.getChallenges(memberId),
            membersAPI.getMarketing(memberId),
            membersAPI.getStucks(memberId),
            membersAPI.getAttendance(memberId),
          ]);

        setData({
          goals: goalsRes.goals || [],
          challenges: challengesRes.challenges || [],
          marketing: marketingRes.marketing || [],
          stucks: stucksRes.stucks || [],
          attendance: attendanceRes.attendance || [],
        });
      } catch (error) {
        console.error("Error fetching member analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [memberId]);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-[100px] w-full" />
        <Skeleton className="h-[300px] w-full" />
      </div>
    );
  }

  const totalGoals = data.goals.length;
  const completedGoals = data.goals.filter((g) => g.is_completed).length;
  const vageGoals = data.goals.filter((g) => g.is_vague).length;
  const attendanceRate =
    data.attendance.length > 0
      ? (
          (data.attendance.filter((a) => a.status === "present").length /
            data.attendance.length) *
          100
        ).toFixed(1)
      : "0";

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Goals</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalGoals}</div>
            <p className="text-xs text-muted-foreground">
              {completedGoals} completed ({vageGoals} vague)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Challenges</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.challenges.length}</div>
            <p className="text-xs text-muted-foreground">Across all sessions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Marketing Activities
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.marketing.length}</div>
            <p className="text-xs text-muted-foreground">Total activities</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Attendance</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{attendanceRate}%</div>
            <p className="text-xs text-muted-foreground">
              {data.attendance.filter((a) => a.status === "present").length} /{" "}
              {data.attendance.length} sessions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Tabs */}
      <Tabs defaultValue="goals" className="space-y-4">
        <TabsList>
          <TabsTrigger value="goals">Goals</TabsTrigger>
          <TabsTrigger value="challenges">Challenges</TabsTrigger>
          <TabsTrigger value="marketing">Marketing</TabsTrigger>
          <TabsTrigger value="stucks">Stuck Detections</TabsTrigger>
          <TabsTrigger value="attendance">Attendance</TabsTrigger>
        </TabsList>

        <TabsContent value="goals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Goals</CardTitle>
              <CardDescription>All goals set by this member</CardDescription>
            </CardHeader>
            <CardContent>
              {data.goals.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No goals recorded yet.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Goal</TableHead>
                      <TableHead>Session</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.goals.map((goal: any) => (
                      <TableRow key={goal.id}>
                        <TableCell className="font-medium">
                          {goal.goal}
                        </TableCell>
                        <TableCell>
                          {goal.sessions?.session_number
                            ? `Session ${goal.sessions.session_number}`
                            : "N/A"}
                        </TableCell>
                        <TableCell>
                          {goal.is_completed ? (
                            <Badge
                              variant="outline"
                              className="bg-green-50 text-green-700 border-green-200"
                            >
                              <CheckCircle2 className="mr-1 h-3 w-3" />
                              Completed
                            </Badge>
                          ) : (
                            <Badge variant="outline">
                              <XCircle className="mr-1 h-3 w-3" />
                              Pending
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          {goal.is_vague ? (
                            <Badge variant="secondary">Vague</Badge>
                          ) : (
                            <Badge variant="outline">Specific</Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="challenges" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Challenges</CardTitle>
              <CardDescription>
                Challenges discussed in sessions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {data.challenges.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No challenges recorded yet.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Description</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Session</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.challenges.map((challenge: any) => (
                      <TableRow key={challenge.id}>
                        <TableCell className="font-medium">
                          {challenge.description}
                        </TableCell>
                        <TableCell>
                          {challenge.category ? (
                            <Badge variant="secondary">
                              {challenge.category}
                            </Badge>
                          ) : (
                            "-"
                          )}
                        </TableCell>
                        <TableCell>
                          {challenge.sessions?.session_number
                            ? `Session ${challenge.sessions.session_number}`
                            : "N/A"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="marketing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Marketing Activities</CardTitle>
              <CardDescription>
                All marketing activities and outcomes
              </CardDescription>
            </CardHeader>
            <CardContent>
              {data.marketing.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No marketing activities recorded yet.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Activity</TableHead>
                      <TableHead>Stage</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Revenue</TableHead>
                      <TableHead>Win</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.marketing.map((activity: any) => (
                      <TableRow key={activity.id}>
                        <TableCell className="font-medium">
                          <Badge variant="outline">{activity.activity}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{activity.stage}</Badge>
                        </TableCell>
                        <TableCell>{activity.quantity || "-"}</TableCell>
                        <TableCell>
                          {activity.revenue
                            ? `$${parseFloat(activity.revenue).toLocaleString()}`
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {activity.is_win ? (
                            <Badge className="bg-green-50 text-green-700 border-green-200">
                              Yes
                            </Badge>
                          ) : (
                            "-"
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stucks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Stuck Detections</CardTitle>
              <CardDescription>
                Moments when member appeared stuck or blocked
              </CardDescription>
            </CardHeader>
            <CardContent>
              {data.stucks.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No stuck detections recorded.
                </p>
              ) : (
                <div className="space-y-4">
                  {data.stucks.map((stuck: any) => (
                    <div
                      key={stuck.id}
                      className="border rounded-lg p-4 space-y-2"
                    >
                      <div className="flex items-start justify-between">
                        <Badge variant="destructive">
                          {stuck.classification}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {stuck.sessions?.session_number
                            ? `Session ${stuck.sessions.session_number}`
                            : "N/A"}
                        </span>
                      </div>
                      <p className="text-sm font-medium">{stuck.stuck_summary}</p>
                      {stuck.exact_quotes && stuck.exact_quotes.length > 0 && (
                        <div className="bg-muted p-2 rounded text-sm italic">
                          "{stuck.exact_quotes[0]}"
                        </div>
                      )}
                      {stuck.potential_next_step && (
                        <div className="text-sm">
                          <span className="font-medium">Next step: </span>
                          {stuck.potential_next_step}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="attendance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Attendance History</CardTitle>
              <CardDescription>
                Session attendance records for this member
              </CardDescription>
            </CardHeader>
            <CardContent>
              {data.attendance.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No attendance records yet.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Session</TableHead>
                      <TableHead>Group</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Notes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.attendance.map((record: any) => (
                      <TableRow key={record.id}>
                        <TableCell>
                          {record.sessions?.session_number
                            ? `Session ${record.sessions.session_number}`
                            : "N/A"}
                        </TableCell>
                        <TableCell>
                          {record.sessions?.groups?.name || "N/A"}
                        </TableCell>
                        <TableCell>
                          {record.status === "present" ? (
                            <Badge className="bg-green-50 text-green-700 border-green-200">
                              Present
                            </Badge>
                          ) : (
                            <Badge variant="secondary">{record.status}</Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {record.notes || "-"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
