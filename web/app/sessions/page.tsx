"use client";

import { useEffect, useState } from "react";
import { Plus, Upload, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { programsAPI, groupsAPI, sessionsAPI, membersAPI } from "@/lib/api";
import type { Program, Group, Session, ExtractionResults, GroupMember } from "@/lib/types";

export default function SessionsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [groupMembers, setGroupMembers] = useState<GroupMember[]>([]);

  const [selectedProgram, setSelectedProgram] = useState<string>("");
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [transcript, setTranscript] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractionResults, setExtractionResults] = useState<ExtractionResults | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const [sessionFormData, setSessionFormData] = useState({
    session_date: new Date().toISOString().split('T')[0],
    notes: "",
  });

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
      loadSessions(selectedGroup);
      loadGroupMembers(selectedGroup);
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

  const loadSessions = async (groupId: string) => {
    try {
      const data = await sessionsAPI.listByGroup(parseInt(groupId));
      setSessions(data.sessions);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    }
  };

  const loadGroupMembers = async (groupId: string) => {
    try {
      const data = await membersAPI.listGroupMembers(parseInt(groupId));
      setGroupMembers(data.members);
    } catch (error) {
      console.error("Failed to load group members:", error);
    }
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroup) return;

    try {
      const session = await sessionsAPI.create({
        group_id: parseInt(selectedGroup),
        session_date: sessionFormData.session_date,
        notes: sessionFormData.notes,
      });
      setCurrentSession(session);
      setIsCreateOpen(false);
      loadSessions(selectedGroup);
    } catch (error) {
      console.error("Failed to create session:", error);
      alert("Failed to create session");
    }
  };

  const handleProcessTranscript = async () => {
    if (!currentSession || !transcript) return;

    setIsProcessing(true);
    try {
      const result = await sessionsAPI.processTranscript(currentSession.id, transcript);
      setExtractionResults(result.extraction_results);
    } catch (error) {
      console.error("Failed to process transcript:", error);
      alert("Failed to process transcript");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveExtractions = async () => {
    if (!currentSession || !extractionResults) return;

    try {
      await sessionsAPI.saveExtractions(currentSession.id, extractionResults);
      alert("Extractions saved successfully!");
      setCurrentSession(null);
      setTranscript("");
      setExtractionResults(null);
      loadSessions(selectedGroup);
    } catch (error) {
      console.error("Failed to save extractions:", error);
      alert("Failed to save extractions");
    }
  };

  const updateAttendanceMatch = (index: number, memberId: number) => {
    if (!extractionResults || !extractionResults.attendance) return;

    const updatedAttendance = [...extractionResults.attendance];
    updatedAttendance[index] = {
      ...updatedAttendance[index],
      matched_member_id: memberId,
      needs_manual_review: false,
    };

    setExtractionResults({
      ...extractionResults,
      attendance: updatedAttendance,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sessions</h1>
          <p className="text-muted-foreground">
            Create sessions and process transcripts with AI
          </p>
        </div>
      </div>

      {/* Program and Group Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Group</CardTitle>
          <CardDescription>Choose a program and group to manage sessions</CardDescription>
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

          {selectedGroup && (
            <Button onClick={() => setIsCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Session
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Session Workflow */}
      {currentSession ? (
        <Card>
          <CardHeader>
            <CardTitle>Session #{currentSession.session_number}</CardTitle>
            <CardDescription>
              {new Date(currentSession.session_date).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {!extractionResults ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="transcript">Upload Transcript</Label>
                  <Textarea
                    id="transcript"
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste your session transcript here..."
                    rows={15}
                    className="font-mono text-sm"
                  />
                </div>
                <Button
                  onClick={handleProcessTranscript}
                  disabled={!transcript || isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing with AI...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Process Transcript
                    </>
                  )}
                </Button>
              </>
            ) : (
              <Tabs defaultValue="attendance" className="w-full">
                <TabsList className="grid w-full grid-cols-6">
                  <TabsTrigger value="attendance">Attendance</TabsTrigger>
                  <TabsTrigger value="goals">Goals</TabsTrigger>
                  <TabsTrigger value="challenges">Challenges</TabsTrigger>
                  <TabsTrigger value="marketing">Marketing</TabsTrigger>
                  <TabsTrigger value="stucks">Stucks</TabsTrigger>
                  <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
                </TabsList>

                <TabsContent value="attendance" className="space-y-4">
                  <h3 className="font-semibold">Attendance - Review and Correct</h3>
                  {extractionResults.attendance && extractionResults.attendance.map((record, index) => (
                    <Card key={index}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{record.extracted_name}</p>
                            <Badge>{record.status.replace(/_/g, " ")}</Badge>
                          </div>
                          <div className="flex items-center gap-4">
                            {record.needs_manual_review ? (
                              <>
                                <AlertCircle className="h-5 w-5 text-yellow-500" />
                                <Select
                                  value={record.matched_member_id?.toString() || ""}
                                  onValueChange={(value) => updateAttendanceMatch(index, parseInt(value))}
                                >
                                  <SelectTrigger className="w-[200px]">
                                    <SelectValue placeholder="Select member" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {groupMembers && groupMembers.map((gm) => (
                                      <SelectItem key={gm.member_id} value={gm.member_id.toString()}>
                                        {gm.member?.name || 'Unknown'}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </>
                            ) : (
                              <>
                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                                <span className="text-sm text-muted-foreground">
                                  Matched ({record.confidence_score}% confidence)
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="goals" className="space-y-4">
                  <h3 className="font-semibold">Goals Extracted</h3>
                  {extractionResults.goals?.goals && extractionResults.goals.goals.map((goal, index) => (
                    <Card key={index}>
                      <CardContent className="pt-6">
                        <p className="font-medium">{goal.name}</p>
                        <p className="text-sm text-muted-foreground mt-2">
                          {goal.quantifiable_goal}
                        </p>
                        {goal.is_vague && (
                          <Badge variant="outline" className="mt-2">Vague Goal</Badge>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="challenges" className="space-y-4">
                  <h3 className="font-semibold">Challenges & Strategies</h3>
                  {extractionResults.challenges?.challenges && extractionResults.challenges.challenges.map((individual, personIndex) => (
                    <div key={personIndex} className="space-y-2">
                      <h4 className="font-semibold text-lg">{individual.name}</h4>
                      {individual.challenges.map((challenge, challengeIndex) => (
                        <Card key={challengeIndex}>
                          <CardContent className="pt-6">
                            <p className="text-sm mt-2">{challenge.challenge}</p>
                            <Badge className="mt-2">{challenge.category}</Badge>
                            {challenge.strategies && challenge.strategies.length > 0 && (
                              <div className="mt-4 space-y-2">
                                <p className="text-sm font-medium">Strategies:</p>
                                {challenge.strategies.map((strategy, sIndex) => (
                                  <div key={sIndex} className="text-sm text-muted-foreground pl-4">
                                    • {strategy.summary} (by {strategy.name || 'Unknown'})
                                    <Badge variant="outline" className="ml-2">{strategy.tag}</Badge>
                                  </div>
                                ))}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="marketing" className="space-y-4">
                  <h3 className="font-semibold">Marketing Activities</h3>
                  {extractionResults.marketing_activities?.activities && extractionResults.marketing_activities.activities.map((individual, personIndex) => (
                    <div key={personIndex} className="space-y-2">
                      <h4 className="font-semibold text-lg">{individual.name || 'Unknown'}</h4>
                      {individual.activities.map((activity, activityIndex) => (
                        <Card key={activityIndex}>
                          <CardContent className="pt-6">
                            <div className="mt-2 space-y-1 text-sm">
                              <p>Stage: <Badge>{activity.stage}</Badge></p>
                              <p>Type: {activity.activity}</p>
                              {activity.quanitity && <p>Quantity: {activity.quanitity}</p>}
                              {activity.is_win && <Badge className="ml-2 bg-green-50 text-green-700 border-green-200">Win!</Badge>}
                              {activity.outcome && (
                                <>
                                  <p className="mt-2">Outcomes:</p>
                                  <div className="pl-4 text-muted-foreground">
                                    <p>• Meetings: {activity.outcome.no_of_meetings || 0}</p>
                                    <p>• Proposals: {activity.outcome.no_of_proposals || 0}</p>
                                    <p>• Clients: {activity.outcome.no_of_clients || 0}</p>
                                    {activity.revenue && (
                                      <p>• Revenue: ${activity.revenue}</p>
                                    )}
                                    {activity.outcome.notes && (
                                      <p className="mt-2 italic">Notes: {activity.outcome.notes}</p>
                                    )}
                                  </div>
                                </>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="stucks" className="space-y-4">
                  <h3 className="font-semibold">Stuck Detections</h3>
                  {extractionResults.stuck_detections?.detections && extractionResults.stuck_detections.detections.map((stuck, index) => (
                    <Card key={index}>
                      <CardContent className="pt-6">
                        <p className="font-medium">{stuck.name}</p>
                        <Badge className="mt-2">{stuck.classification}</Badge>
                        <p className="text-sm mt-2">{stuck.stuck_summary}</p>
                        {stuck.exact_quotes && stuck.exact_quotes.length > 0 && (
                          <div className="mt-2 bg-muted p-2 rounded text-sm italic">
                            "{stuck.exact_quotes[0]}"
                          </div>
                        )}
                        {stuck.potential_next_step && (
                          <p className="text-sm text-muted-foreground mt-2">
                            Next step: {stuck.potential_next_step}
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="sentiment" className="space-y-4">
                  <h3 className="font-semibold">Session Sentiment</h3>
                  {extractionResults.sentiment ? (
                    <Card>
                      <CardContent className="pt-6 space-y-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Overall Score</p>
                          <p className="text-3xl font-bold">{extractionResults.sentiment.sentiment_score || 0}/5</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Dominant Emotion</p>
                          <Badge>{extractionResults.sentiment.dominant_emotion || 'N/A'}</Badge>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Rationale</p>
                          <p className="text-sm">{extractionResults.sentiment.rationale || 'No rationale provided'}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ) : (
                    <p className="text-sm text-muted-foreground">No sentiment data available</p>
                  )}
                </TabsContent>
              </Tabs>
            )}

            {extractionResults && (
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline" onClick={() => {
                  setExtractionResults(null);
                  setTranscript("");
                }}>
                  Cancel
                </Button>
                <Button onClick={handleSaveExtractions}>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Save All to Database
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        selectedGroup && sessions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Sessions</CardTitle>
              <CardDescription>Click a session to view or process</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent cursor-pointer"
                    onClick={() => setCurrentSession(session)}
                  >
                    <div>
                      <p className="font-medium">Session #{session.session_number}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(session.session_date).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={session.transcript ? "default" : "outline"}>
                      {session.transcript ? "Processed" : "Pending"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      )}

      {/* Create Session Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <form onSubmit={handleCreateSession}>
            <DialogHeader>
              <DialogTitle>Create New Session</DialogTitle>
              <DialogDescription>
                Create a new coaching session
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="session_date">Session Date</Label>
                <Input
                  id="session_date"
                  type="date"
                  value={sessionFormData.session_date}
                  onChange={(e) => setSessionFormData({ ...sessionFormData, session_date: e.target.value })}
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="notes">Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  value={sessionFormData.notes}
                  onChange={(e) => setSessionFormData({ ...sessionFormData, notes: e.target.value })}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Create Session</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
