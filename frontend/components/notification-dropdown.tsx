"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Bell, AlertTriangle, CalendarPlus, BookCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { formatDistanceToNow } from 'date-fns'

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
const NotificationContent = ({ notification }: { notification: Notification }) => {
  let title = "New Notification"
  let message = notification.message || "You have a new update."
  let icon = <Bell className="h-4 w-4 mr-3 text-gray-500" />
  let link = "#"

  switch (notification.type) {
    case "assessment_failed":
      title = "Assessment Failed"
      message = notification.message || `${notification.from_username} failed an assessment.`
      icon = <AlertTriangle className="h-4 w-4 mr-3 text-red-500" />
      link = `/roadmap/${notification.roadmap_id}`
      break
    case "assessment_passed":
        title = "Assessment Passed"
        message = notification.message || `${notification.from_username} passed an assessment.`
        icon = <BookCheck className="h-4 w-4 mr-3 text-green-500" />
        link = `/roadmap/${notification.roadmap_id}`
        break
    case "milestone_reached_meeting_suggestion":
      title = "Milestone Reached"
      message = notification.message || `${notification.from_username} has reached a major milestone.`
      icon = <CalendarPlus className="h-4 w-4 mr-3 text-blue-500" />
      link = `/schedule`
      break
    default:
      title = notification.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      break;
  }

  return (
    <Link href={link} passHref>
      <div className="flex flex-col items-start p-3 w-full cursor-pointer">
        <div className="flex items-center w-full">
          {icon}
          <div className="flex-1">
            <p className="font-medium text-sm">{title}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
            </p>
          </div>
          {!notification.read && <div className="h-2 w-2 bg-purple-600 rounded-full"></div>}
        </div>
        <p className="text-sm mt-1 pl-7">{message}</p>
      </div>
    </Link>
  )
}

export default function NotificationDropdown() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)

  const fetchNotifications = async () => {
    try {
      const fetchedNotifications = await api.get("/notifications/");
      setNotifications(fetchedNotifications);
      
      const unreadData = await api.get("/notifications/count/");
      setUnreadCount(unreadData.count);
    } catch (error) {
      // Silently fail on fetch error to not disrupt user experience
      // console.error("Failed to fetch notifications:", error)
    }
  }

  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, [])

  const markAsRead = async (id: string) => {
    const notification = notifications.find(n => n._id === id);
    if (notification && !notification.read) {
      try {
        await api.post(`/notifications/${id}/read/`, {});
        setNotifications(notifications.map((n) => (n._id === id ? { ...n, read: true } : n)))
        setUnreadCount((prev) => (prev > 0 ? prev - 1 : 0))
      } catch (error) {
        console.error("Failed to mark notification as read:", error)
      }
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.post("/notifications/read-all/", {});
      setNotifications(notifications.map((n) => ({ ...n, read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-purple-600"
              variant="secondary"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-96">
        <DropdownMenuLabel className="flex justify-between items-center">
          <span>Notifications</span>
          {unreadCount > 0 && (
            <Button
              variant="link"
              size="sm"
              className="h-auto p-0 text-xs text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300"
              onClick={markAllAsRead}
            >
              Mark all as read
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400">No notifications</div>
          ) : (
            notifications.map((notification) => (
              <DropdownMenuItem
                key={notification._id}
                className="p-0 data-[highlighted]:bg-gray-100 dark:data-[highlighted]:bg-gray-800"
                onSelect={() => markAsRead(notification._id)}
              >
                <NotificationContent notification={notification} />
              </DropdownMenuItem>
            ))
          )}
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="justify-center text-purple-600 dark:text-purple-400">
          <Link href="/notifications">View all notifications</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}