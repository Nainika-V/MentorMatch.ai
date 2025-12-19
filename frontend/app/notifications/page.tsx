"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Bell, AlertTriangle, CalendarPlus, BookCheck } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { api } from "@/lib/api"
import { format } from 'date-fns'

// Matches the backend notification structure
interface Notification {
  _id: string
  type: string
  from_username: string
  roadmap_id?: string
  module_index?: number
  score?: number
  message?: string // Generic message field for display
  created_at: string
  read: boolean
}

// Helper to render notification content based on type
const NotificationItem = ({ notification }: { notification: Notification }) => {
  let title = "New Notification"
  let message = notification.message || "You have a new update."
  let icon = <Bell className="h-5 w-5 mr-4 text-gray-500" />
  let link = "#"

  switch (notification.type) {
    case "assessment_failed":
      title = "Assessment Failed"
      message = notification.message || `${notification.from_username} failed an assessment.`
      icon = <AlertTriangle className="h-5 w-5 mr-4 text-red-500" />
      link = `/roadmap/${notification.roadmap_id}`
      break
    case "assessment_passed":
        title = "Assessment Passed"
        message = notification.message || `${notification.from_username} passed an assessment.`
        icon = <BookCheck className="h-5 w-5 mr-4 text-green-500" />
        link = `/roadmap/${notification.roadmap_id}`
        break
    case "milestone_reached_meeting_suggestion":
      title = "Milestone Reached"
      message = notification.message || `${notification.from_username} has reached a major milestone.`
      icon = <CalendarPlus className="h-5 w-5 mr-4 text-blue-500" />
      link = `/schedule`
      break
    case "roadmap_updated":
        title = "Roadmap Updated"
        message = notification.message || `Your roadmap has been updated.`
        icon = <BookCheck className="h-5 w-5 mr-4 text-blue-500" />
        link = `/roadmap/${notification.roadmap_id}`
        break
    default:
      title = notification.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      break;
  }

  return (
    <Link href={link} passHref>
      <div className={`flex items-start p-4 border-b ${!notification.read ? 'bg-purple-50 dark:bg-gray-800/50' : ''}`}>
        {icon}
        <div className="flex-1">
          <div className="flex justify-between items-center">
            <p className="font-medium">{title}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {format(new Date(notification.created_at), 'PPpp')}
            </p>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{message}</p>
        </div>
        {!notification.read && <div className="h-2.5 w-2.5 bg-purple-600 rounded-full ml-4 mt-1"></div>}
      </div>
    </Link>
  )
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true)
        const fetchedNotifications = await api.get("/notifications/");
        setNotifications(fetchedNotifications);
      } catch (error) {
        console.error("Failed to fetch notifications:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchNotifications()
  }, [])

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>All Notifications</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">You have no notifications.</div>
          ) : (
            <div>
              {notifications.map((notification) => (
                <NotificationItem key={notification._id} notification={notification} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
