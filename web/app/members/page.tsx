"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Users, UserPlus, Eye, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { membersAPI, programsAPI, groupsAPI } from "@/lib/api";
import type { Member, Program, Group } from "@/lib/types";

interface MemberWithGroups extends Member {
  groups?: any[];
}

export default function MembersPage() {
  const router = useRouter();
  const [members, setMembers] = useState<MemberWithGroups[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isAssignOpen, setIsAssignOpen] = useState(false);
  const [isViewGroupsOpen, setIsViewGroupsOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<MemberWithGroups | null>(null);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  const [assignData, setAssignData] = useState({
    programId: "",
    groupId: "",
    role: "participant" as "facilitator" | "participant" | "observer",
  });

  useEffect(() => {
    loadMembers();
    loadPrograms();
  }, []);

  const loadMembers = async () => {
    try {
      const data = await membersAPI.list();

      // Load groups for each member
      const membersWithGroups = await Promise.all(
        data.members.map(async (member) => {
          try {
            const groupsData = await membersAPI.getGroups(member.id);
            return { ...member, groups: groupsData.groups };
          } catch (error) {
            console.error(`Failed to load groups for member ${member.id}:`, error);
            return { ...member, groups: [] };
          }
        })
      );

      setMembers(membersWithGroups);
    } catch (error) {
      console.error("Failed to load members:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadPrograms = async () => {
    try {
      const data = await programsAPI.list();
      setPrograms(data.programs);
    } catch (error) {
      console.error("Failed to load programs:", error);
    }
  };

  const loadGroupsForProgram = async (programId: string) => {
    try {
      const data = await groupsAPI.listByProgram(parseInt(programId));
      setGroups(data.groups);
    } catch (error) {
      console.error("Failed to load groups:", error);
    }
  };

  const handleCreateMember = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await membersAPI.create(formData);
      setIsCreateOpen(false);
      setFormData({ name: "", email: "" });
      loadMembers();
    } catch (error) {
      console.error("Failed to create member:", error);
      alert("Failed to create member. Email may already exist.");
    }
  };

  const handleAssignToGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMember || !assignData.groupId) return;

    try {
      await membersAPI.assignToGroup(parseInt(assignData.groupId), {
        member_id: selectedMember.id,
        role: assignData.role,
      });
      setIsAssignOpen(false);
      setAssignData({ programId: "", groupId: "", role: "participant" });
      alert("Member assigned to group successfully!");
      loadMembers(); // Reload to show updated groups
    } catch (error) {
      console.error("Failed to assign member:", error);
      alert("Failed to assign member to group");
    }
  };

  const openAssignDialog = (member: MemberWithGroups) => {
    setSelectedMember(member);
    setIsAssignOpen(true);
  };

  const openViewGroupsDialog = (member: MemberWithGroups) => {
    setSelectedMember(member);
    setIsViewGroupsOpen(true);
  };

  const handleRemoveFromGroup = async (groupMemberId: number) => {
    if (!confirm("Are you sure you want to remove this member from the group?")) return;

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
      const response = await fetch(`${API_BASE_URL}/api/group-members/${groupMemberId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to remove member from group');
      }

      alert("Member removed from group successfully!");
      loadMembers();
      if (selectedMember) {
        const updatedMember = await membersAPI.getGroups(selectedMember.id);
        setSelectedMember({ ...selectedMember, groups: updatedMember.groups });
      }
    } catch (error) {
      console.error("Failed to remove member from group:", error);
      alert("Failed to remove member from group");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Members</h1>
          <p className="text-muted-foreground">
            Manage members and group assignments
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Member
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : members.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No members yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Add your first member to get started
            </p>
            <Button onClick={() => setIsCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Member
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>All Members</CardTitle>
            <CardDescription>
              {members.length} member{members.length !== 1 ? "s" : ""} in total
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Groups</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell
                      className="font-medium cursor-pointer hover:text-primary"
                      onClick={() => router.push(`/members/${member.id}`)}
                    >
                      {member.name}
                    </TableCell>
                    <TableCell>{member.email}</TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {member.groups && member.groups.length > 0 ? (
                          <>
                            {member.groups.slice(0, 2).map((gm: any) => (
                              <Badge key={gm.id} variant="secondary" className="text-xs">
                                {gm.groups?.name || "Unknown"}
                              </Badge>
                            ))}
                            {member.groups.length > 2 && (
                              <Badge
                                variant="outline"
                                className="text-xs cursor-pointer"
                                onClick={() => openViewGroupsDialog(member)}
                              >
                                +{member.groups.length - 2} more
                              </Badge>
                            )}
                          </>
                        ) : (
                          <span className="text-sm text-muted-foreground">No groups</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={member.is_active ? "default" : "secondary"}>
                        {member.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex gap-2 justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openViewGroupsDialog(member)}
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View Groups
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openAssignDialog(member)}
                        >
                          <UserPlus className="mr-2 h-4 w-4" />
                          Assign
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Create Member Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <form onSubmit={handleCreateMember}>
            <DialogHeader>
              <DialogTitle>Add New Member</DialogTitle>
              <DialogDescription>
                Add a new member to your platform
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Add Member</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Assign to Group Dialog */}
      <Dialog open={isAssignOpen} onOpenChange={setIsAssignOpen}>
        <DialogContent>
          <form onSubmit={handleAssignToGroup}>
            <DialogHeader>
              <DialogTitle>Assign to Group</DialogTitle>
              <DialogDescription>
                Assign {selectedMember?.name} to a group
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="program">Program</Label>
                <Select
                  value={assignData.programId}
                  onValueChange={(value) => {
                    setAssignData({ ...assignData, programId: value, groupId: "" });
                    loadGroupsForProgram(value);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a program" />
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

              {assignData.programId && (
                <div className="grid gap-2">
                  <Label htmlFor="group">Group</Label>
                  <Select
                    value={assignData.groupId}
                    onValueChange={(value) => setAssignData({ ...assignData, groupId: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a group" />
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

              <div className="grid gap-2">
                <Label htmlFor="role">Role</Label>
                <Select
                  value={assignData.role}
                  onValueChange={(value: any) => setAssignData({ ...assignData, role: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="participant">Participant</SelectItem>
                    <SelectItem value="facilitator">Facilitator</SelectItem>
                    <SelectItem value="observer">Observer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsAssignOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={!assignData.groupId}>
                Assign
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* View Groups Dialog */}
      <Dialog open={isViewGroupsOpen} onOpenChange={setIsViewGroupsOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div>
                <DialogTitle>{selectedMember?.name} - Groups</DialogTitle>
                <DialogDescription>
                  Manage group memberships for this member
                </DialogDescription>
              </div>
              <Button
                size="sm"
                onClick={() => {
                  setIsViewGroupsOpen(false);
                  setTimeout(() => openAssignDialog(selectedMember!), 100);
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Add to Group
              </Button>
            </div>
          </DialogHeader>
          <div className="space-y-2">
            {selectedMember?.groups && selectedMember.groups.length > 0 ? (
              selectedMember.groups.map((gm: any) => (
                <div key={gm.id} className="flex items-center justify-between border rounded-lg p-3">
                  <div>
                    <div className="font-medium">{gm.groups?.name || "Unknown Group"}</div>
                    <div className="text-sm text-muted-foreground">
                      Role: <Badge variant="outline" className="ml-1">{gm.role}</Badge>
                      {gm.groups?.cohort && ` • Cohort: ${gm.groups.cohort}`}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveFromGroup(gm.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-sm text-muted-foreground">
                Not assigned to any groups yet
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
