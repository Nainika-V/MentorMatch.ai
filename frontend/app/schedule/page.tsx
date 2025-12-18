"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { CalendarIcon, Clock, Video, Edit, Trash2, Save } from "lucide-react"
import DashboardLayout from "@/components/dashboard-layout"
import { useSearchParams } from "next/navigation"

export default function SchedulePage() {
  // Set to null initially
  const [activeTab, setActiveTab] = useState<string | null>(null)
  const [userRole, setUserRole] = useState<"mentor" | "mentee">("mentee")
  const [userName, setUserName] = useState("")
  const [userEmail, setUserEmail] = useState("")
  const [mentees, setMentees] = useState<{ id: string; name: string }[]>([])
  const [meetings, setMeetings] = useState<any[]>([])
  const [pastMeetings, setPastMeetings] = useState<any[]>([])
  const [currentMeetings, setCurrentMeetings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  // Scheduling form state
  const [meetingTitle, setMeetingTitle] = useState("")
  const [meetingAgenda, setMeetingAgenda] = useState("")
  const [meetingLink, setMeetingLink] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")
  const [selectedMentee, setSelectedMentee] = useState("")
  // For editing meetings
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<any>({})

  // Fetch user info and mentees (keep this as is)
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError("")
      try {
        // Get user profile (to get role, mentees, etc.)
        const resProfile = await fetch("http://localhost:5000/api/auth/profile", {
          credentials: "include",
        })
        const dataProfile = await resProfile.json()
        if (!resProfile.ok) throw new Error(dataProfile.message || "Failed to fetch profile")
        setUserRole(dataProfile.user.role)
        setUserName(dataProfile.user.name)
        setUserEmail(dataProfile.user.email)
      } catch (err: any) {
        setError(err.message || "Failed to load user data")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // After user info is loaded, set default tab
  useEffect(() => {
    if (userRole) {
      setActiveTab("upcoming")
    }
  }, [userRole])

  // Fetch meetings when activeTab changes
  useEffect(() => {
    if (!activeTab) return
    const fetchMeetings = async () => {
      setLoading(true)
      setError("")
      try {
        let url = ""
        if (activeTab === "current") url = "http://localhost:5000/api/meetings/current"
        else if (activeTab === "upcoming") url = "http://localhost:5000/api/meetings/upcoming"
        else if (activeTab === "past") url = "http://localhost:5000/api/meetings/past"
        else return

        const res = await fetch(url, { credentials: "include" })
        const data = await res.json()
        if (!res.ok) throw new Error(data.message || "Failed to fetch meetings")
        if (activeTab === "current") setCurrentMeetings(data)
        else if (activeTab === "upcoming") setMeetings(data)
        else if (activeTab === "past") setPastMeetings(data)
      } catch (err: any) {
        setError(err.message || "Failed to fetch meetings")
      } finally {
        setLoading(false)
      }
    }
    // Only fetch if not on "schedule" tab
    if (["current", "upcoming", "past"].includes(activeTab)) {
      fetchMeetings()
    }
  }, [activeTab])

  const searchParams = useSearchParams();
  useEffect(() => {
    const menteesParam = searchParams.get("mentees");
    if (menteesParam) {
      try {
        const menteeList = JSON.parse(decodeURIComponent(menteesParam));
        setMentees(menteeList);
      } catch (e) {
        // fallback: keep mentees empty or fetch as before
      }
    }
    // ...rest of your useEffect logic (fetch user, meetings, etc)...
  }, []);

  // Schedule a new meeting (mentor only)
  const handleScheduleMeeting = async () => {
    setError("")
    setSuccess("")
    try {
      const res = await fetch("http://localhost:5000/api/meetings/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          mentee_id: selectedMentee,
          title: meetingTitle,
          description: meetingAgenda,
          meeting_link: meetingLink,
          start_time: startTime,
          end_time: endTime,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.message || "Failed to schedule meeting")
      setSuccess("Meeting scheduled successfully!")
      setMeetingTitle("")
      setMeetingAgenda("")
      setMeetingLink("")
      setStartTime("")
      setEndTime("")
      setSelectedMentee("")
      // Refresh meetings
      const resUpcoming = await fetch("http://localhost:5000/api/meetings/upcoming", { credentials: "include" })
      setMeetings(resUpcoming.ok ? await resUpcoming.json() : [])
      setActiveTab("upcoming")
    } catch (err: any) {
      setError(err.message || "Failed to schedule meeting")
    }
  }

  // Edit meeting (mentor only)
  const handleEditMeeting = (meeting: any) => {
    setEditingId(meeting.meeting_id)
    setEditForm({
      title: meeting.title,
      description: meeting.description,
      meeting_link: meeting.meeting_link,
      start_time: meeting.start_time.slice(0, 16), // for input type="datetime-local"
      end_time: meeting.end_time.slice(0, 16),
    })
  }
  const handleSaveEdit = async (meetingId: string) => {
    setError("")
    setSuccess("")
    try {
      const res = await fetch(`http://localhost:5000/api/meetings/${meetingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          ...editForm,
          start_time: new Date(editForm.start_time).toISOString(),
          end_time: new Date(editForm.end_time).toISOString(),
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.message || "Failed to update meeting")
      setSuccess("Meeting updated successfully!")
      setEditingId(null)
      // Refresh meetings
      const resUpcoming = await fetch("http://localhost:5000/api/meetings/upcoming", { credentials: "include" })
      setMeetings(resUpcoming.ok ? await resUpcoming.json() : [])
    } catch (err: any) {
      setError(err.message || "Failed to update meeting")
    }
  }

  // Cancel meeting (mentor only)
  const handleCancelMeeting = async (meetingId: string) => {
    setError("")
    setSuccess("")
    try {
      const res = await fetch(`http://localhost:5000/api/meetings/${meetingId}`, {
        method: "DELETE",
        credentials: "include",
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.message || "Failed to cancel meeting")
      setSuccess("Meeting cancelled successfully!")
      // Refresh meetings
      const resUpcoming = await fetch("http://localhost:5000/api/meetings/upcoming", { credentials: "include" })
      setMeetings(resUpcoming.ok ? await resUpcoming.json() : [])
    } catch (err: any) {
      setError(err.message || "Failed to cancel meeting")
    }
  }

  useEffect(() => {
    const fetchMentees = async () => {
      // Only run if the user is a mentor
      if (userRole === "mentor") {
        try {
          setLoading(true);
          const res = await fetch("http://localhost:5000/api/users/mentees", {
            credentials: "include",
          });
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.message || "Failed to fetch mentees");
          }
          setMentees(data);
        } catch (err: any) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      }
    };

    // We only want to run this after the user role has been determined.
    if (userRole) {
      fetchMentees();
    }
  }, [userRole]); // Dependency array ensures this runs when userRole changes

  // Helper to check if join is enabled for upcoming meetings
  const canJoin = (startTime: string) => {
    const now = new Date()
    const start = new Date(startTime)
    // Enable if within 5 minutes before start
    return now >= new Date(start.getTime() - 5 * 60 * 1000)
  }

  return (
    <DashboardLayout userRole={userRole} userName={userName} userEmail={userEmail}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Schedule Meetings</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Book time with your mentor or mentees</p>
        </div>
        {error && <div className="text-red-500">{error}</div>}
        {success && <div className="text-green-600">{success}</div>}

        {/* Only render Tabs if activeTab is set */}
        {activeTab && (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="current">Current</TabsTrigger>
              <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
              <TabsTrigger value="past">Past</TabsTrigger>
              {userRole === "mentor" && <TabsTrigger value="schedule">Schedule New</TabsTrigger>}
            </TabsList>

            {/* Current Meetings */}
            <TabsContent value="current" className="space-y-4">
              {currentMeetings.length > 0 ? (
                currentMeetings.map((meeting) => (
                  <Card key={meeting.meeting_id}>
                    <CardHeader>
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div>
                          <CardTitle>{meeting.title}</CardTitle>
                          <CardDescription>
                            with {meeting.with?.name} ({meeting.with?.role})
                          </CardDescription>
                        </div>
                        <Badge className="mt-2 md:mt-0 bg-blue-600 self-start md:self-auto">
                          Ongoing
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
                        <div className="flex items-center">
                          <CalendarIcon className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>{new Date(meeting.start_time).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>
                            {new Date(meeting.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{" "}
                            {new Date(meeting.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <Video className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <Button
                            asChild
                            className="bg-purple-600 hover:bg-purple-700"
                            size="sm"
                          >
                            <a href={meeting.meeting_link} target="_blank" rel="noopener noreferrer">
                              Join Now
                            </a>
                          </Button>
                        </div>
                      </div>
                      <div className="mt-2 text-gray-700 dark:text-gray-300">{meeting.description}</div>
                    </CardContent>
                    <CardFooter className="flex flex-col md:flex-row md:justify-between space-y-2 md:space-y-0">
                      {userRole === "mentor" && (
                        <div className="flex space-x-2">
                          {editingId === meeting.meeting_id ? (
                            <>
                              <Button size="sm" onClick={() => handleSaveEdit(meeting.meeting_id)}>
                                <Save className="h-4 w-4 mr-1" /> Save
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>
                                Cancel
                              </Button>
                            </>
                          ) : (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleEditMeeting(meeting)}>
                                <Edit className="h-4 w-4 mr-1" /> Edit
                              </Button>
                              <Button size="sm" variant="destructive" onClick={() => handleCancelMeeting(meeting.meeting_id)}>
                                <Trash2 className="h-4 w-4 mr-1" /> Cancel
                              </Button>
                            </>
                          )}
                        </div>
                      )}
                    </CardFooter>
                    {editingId === meeting.meeting_id && (
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label>Title</Label>
                            <Input
                              value={editForm.title}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, title: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>Meeting Link</Label>
                            <Input
                              value={editForm.meeting_link}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, meeting_link: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>Start Time</Label>
                            <Input
                              type="datetime-local"
                              value={editForm.start_time}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, start_time: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>End Time</Label>
                            <Input
                              type="datetime-local"
                              value={editForm.end_time}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, end_time: e.target.value }))}
                            />
                          </div>
                          <div className="col-span-2">
                            <Label>Description</Label>
                            <Textarea
                              value={editForm.description}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, description: e.target.value }))}
                            />
                          </div>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                ))
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>No Ongoing Meetings</CardTitle>
                    <CardDescription>You don't have any meetings happening right now</CardDescription>
                  </CardHeader>
                </Card>
              )}
            </TabsContent>

            {/* Upcoming Meetings */}
            <TabsContent value="upcoming" className="space-y-4">
              {meetings.length > 0 ? (
                meetings.map((meeting) => (
                  <Card key={meeting.meeting_id}>
                    <CardHeader>
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div>
                          <CardTitle>{meeting.title}</CardTitle>
                          <CardDescription>
                            with {meeting.with?.name} ({meeting.with?.role})
                          </CardDescription>
                        </div>
                        <Badge className="mt-2 md:mt-0 bg-green-600 self-start md:self-auto">
                          {meeting.status === "scheduled" ? "Confirmed" : meeting.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
                        <div className="flex items-center">
                          <CalendarIcon className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>{new Date(meeting.start_time).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>
                            {new Date(meeting.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{" "}
                            {new Date(meeting.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <Video className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <Button
                            asChild
                            className="bg-purple-600 hover:bg-purple-700"
                            size="sm"
                            disabled={!canJoin(meeting.start_time)}
                          >
                            <a href={meeting.meeting_link} target="_blank" rel="noopener noreferrer">
                              Join Now
                            </a>
                          </Button>
                        </div>
                      </div>
                      <div className="mt-2 text-gray-700 dark:text-gray-300">{meeting.description}</div>
                    </CardContent>
                    <CardFooter className="flex flex-col md:flex-row md:justify-between space-y-2 md:space-y-0">
                      {userRole === "mentor" && (
                        <div className="flex space-x-2">
                          {editingId === meeting.meeting_id ? (
                            <>
                              <Button size="sm" onClick={() => handleSaveEdit(meeting.meeting_id)}>
                                <Save className="h-4 w-4 mr-1" /> Save
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>
                                Cancel
                              </Button>
                            </>
                          ) : (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleEditMeeting(meeting)}>
                                <Edit className="h-4 w-4 mr-1" /> Edit
                              </Button>
                              <Button size="sm" variant="destructive" onClick={() => handleCancelMeeting(meeting.meeting_id)}>
                                <Trash2 className="h-4 w-4 mr-1" /> Cancel
                              </Button>
                            </>
                          )}
                        </div>
                      )}
                    </CardFooter>
                    {editingId === meeting.meeting_id && (
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label>Title</Label>
                            <Input
                              value={editForm.title}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, title: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>Meeting Link</Label>
                            <Input
                              value={editForm.meeting_link}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, meeting_link: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>Start Time</Label>
                            <Input
                              type="datetime-local"
                              value={editForm.start_time}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, start_time: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>End Time</Label>
                            <Input
                              type="datetime-local"
                              value={editForm.end_time}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, end_time: e.target.value }))}
                            />
                          </div>
                          <div className="col-span-2">
                            <Label>Description</Label>
                            <Textarea
                              value={editForm.description}
                              onChange={(e) => setEditForm((f: any) => ({ ...f, description: e.target.value }))}
                            />
                          </div>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                ))
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>No Upcoming Meetings</CardTitle>
                    <CardDescription>You don't have any scheduled meetings</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-center text-gray-500 dark:text-gray-400 py-8">Schedule a meeting to get started!</p>
                  </CardContent>
                  <CardFooter>
                    {userRole === "mentor" && (
                      <Button className="w-full bg-purple-600 hover:bg-purple-700" onClick={() => setActiveTab("schedule")}>
                        Schedule Meeting
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              )}
            </TabsContent>

            {/* Past Meetings */}
            <TabsContent value="past" className="space-y-4">
              {pastMeetings.length > 0 ? (
                pastMeetings.map((meeting) => (
                  <Card key={meeting.meeting_id}>
                    <CardHeader>
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div>
                          <CardTitle>{meeting.title}</CardTitle>
                          <CardDescription>
                            with {meeting.with?.name} ({meeting.with?.role})
                          </CardDescription>
                        </div>
                        <Badge variant="outline" className="mt-2 md:mt-0 self-start md:self-auto">
                          {meeting.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
                        <div className="flex items-center">
                          <CalendarIcon className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>{new Date(meeting.start_time).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                          <span>
                            {new Date(meeting.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{" "}
                            {new Date(meeting.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2 text-gray-700 dark:text-gray-300">{meeting.description}</div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>No Past Meetings</CardTitle>
                    <CardDescription>You haven't had any meetings yet</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-center text-gray-500 dark:text-gray-400 py-8">Once you've had meetings, they'll appear here</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Schedule New Meeting (Mentor Only) */}
            {userRole === "mentor" && (
              <TabsContent value="schedule" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Schedule a New Meeting</CardTitle>
                    <CardDescription>Book time with your mentee</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                      <div className="md:w-1/2 space-y-4">
                        <div>
                          <Label htmlFor="mentee">Select Mentee</Label>
                          <select
                            id="mentee"
                            className="w-full border rounded-md p-2"
                            value={selectedMentee}
                            onChange={(e) => setSelectedMentee(e.target.value)}
                          >
                            <option value="">Select a mentee</option>
                            {mentees.map((mentee) => (
                              <option key={mentee.id} value={mentee.id}>
                                {mentee.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <Label htmlFor="meeting-title">Meeting Title</Label>
                          <Input
                            id="meeting-title"
                            placeholder="e.g. Weekly Check-in"
                            value={meetingTitle}
                            onChange={(e) => setMeetingTitle(e.target.value)}
                          />
                        </div>
                        <div>
                          <Label htmlFor="meeting-link">Meeting Link</Label>
                          <Input
                            id="meeting-link"
                            placeholder="e.g. https://meet.google.com/..."
                            value={meetingLink}
                            onChange={(e) => setMeetingLink(e.target.value)}
                          />
                        </div>
                        <div>
                          <Label htmlFor="meeting-agenda">Agenda (Optional)</Label>
                          <Textarea
                            id="meeting-agenda"
                            placeholder="What would you like to discuss?"
                            value={meetingAgenda}
                            onChange={(e) => setMeetingAgenda(e.target.value)}
                            rows={4}
                          />
                        </div>
                      </div>
                      <div className="md:w-1/2 space-y-4">
                        <div>
                          <Label htmlFor="start-time">Start Time</Label>
                          <Input
                            id="start-time"
                            type="datetime-local"
                            value={startTime}
                            onChange={(e) => setStartTime(e.target.value)}
                          />
                        </div>
                        <div>
                          <Label htmlFor="end-time">End Time</Label>
                          <Input
                            id="end-time"
                            type="datetime-local"
                            value={endTime}
                            onChange={(e) => setEndTime(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" onClick={() => setActiveTab("upcoming")}>
                      Cancel
                    </Button>
                    <Button
                      className="bg-purple-600 hover:bg-purple-700"
                      disabled={!selectedMentee || !meetingTitle || !meetingLink || !startTime || !endTime}
                      onClick={handleScheduleMeeting}
                    >
                      Schedule Meeting
                    </Button>
                  </CardFooter>
                </Card>
              </TabsContent>
            )}
          </Tabs>
        )}
      </div>
    </DashboardLayout>
  )
}
