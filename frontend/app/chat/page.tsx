"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Textarea } from "@/components/ui/textarea";
import {
  PaperclipIcon,
  Send,
  Loader2,
  CheckCircle,
  Sparkles,
} from "lucide-react";
import { MeetingRequestCard } from "@/components/ui/meeting-request-card";
import DashboardLayout from "@/components/dashboard-layout";

interface User {
  id: string;
  name: string;
  username: string;
  role: string;
}

interface Message {
  _id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  timestamp: string;
  type?: string;
  meta?: any;
}

export default function ChatPage() {
  // State variables
  const [userEmail, setUserEmail] = useState<string>("");
  const [userRole, setUserRole] = useState<"mentor" | "mentee">("mentee");
  const [userId, setUserId] = useState<string>("");
  const [userName, setUserName] = useState<string>("");
  const [mentees, setMentees] = useState<User[]>([]);
  const [mentor, setMentor] = useState<User | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMounted, setHasMounted] = useState(false);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const [isGeneratingRoadmap, setIsGeneratingRoadmap] = useState(false);
  const [roadmapGenerated, setRoadmapGenerated] = useState(false);
  const [showAIMention, setShowAIMention] = useState(false);
  const [mentionIndex, setMentionIndex] = useState(0);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Prevent hydration mismatch
  useEffect(() => {
    setHasMounted(true);
  }, []);

  // Fetcch user profile and initialize chat
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch("http://localhost:5000/api/auth/profile", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch profile");
        }

        const data = await response.json();
        const user = data.user;

        setUserId(user.id);
        setUserName(user.name);
        setUserEmail(user.email);
        setUserRole(user.role);

        if (user.role === "mentor" && user.mentees && user.mentees.length > 0) {
          // Fetch mentees with their names using the API
          try {
            const menteesResponse = await fetch(
              "http://localhost:5000/api/users/mentees",
              {
                credentials: "include",
              }
            );

            if (menteesResponse.ok) {
              const menteesData = await menteesResponse.json();
              setMentees(menteesData);

              if (menteesData.length > 0) {
                setSelectedUser(menteesData[0]);
              }
            } else {
              // Fallback to using IDs from profile if API fails
              const menteeUsers = user.mentees.map((menteeId: string) => ({
                id: menteeId,
                name: `Mentee ${menteeId.slice(-4)}`,
                username: `mentee_${menteeId.slice(-4)}`,
                role: "mentee",
              }));
              setMentees(menteeUsers);
              setSelectedUser(menteeUsers[0]);
            }
          } catch (error) {
            console.error("Error fetching mentees:", error);
            // Fallback to using IDs from profile
            const menteeUsers = user.mentees.map((menteeId: string) => ({
              id: menteeId,
              name: `Mentee ${menteeId.slice(-4)}`,
              username: `mentee_${menteeId.slice(-4)}`,
              role: "mentee",
            }));
            setMentees(menteeUsers);
            setSelectedUser(menteeUsers[0]);
          }
        } else if (
          user.role === "mentee" &&
          user.mentors &&
          user.mentors.length > 0
        ) {
          // Fetch mentor with their name using the API
          try {
            const mentorResponse = await fetch(
              "http://localhost:5000/api/users/mymentor",
              {
                credentials: "include",
              }
            );

            if (mentorResponse.ok) {
              const mentorData = await mentorResponse.json();
              setMentor(mentorData);
              setSelectedUser(mentorData);
            } else {
              // Fallback to using ID from profile if API fails
              const mentorId = user.mentors[0];
              const mentorUser = {
                id: mentorId,
                name: `Mentor ${mentorId.slice(-4)}`,
                username: `mentor_${mentorId.slice(-4)}`,
                role: "mentor",
              };
              setMentor(mentorUser);
              setSelectedUser(mentorUser);
            }
          } catch (error) {
            console.error("Error fetching mentor:", error);
            // Fallback to using ID from profile
            const mentorId = user.mentors[0];
            const mentorUser = {
              id: mentorId,
              name: `Mentor ${mentorId.slice(-4)}`,
              username: `mentor_${mentorId.slice(-4)}`,
              role: "mentor",
            };
            setMentor(mentorUser);
            setSelectedUser(mentorUser);
          }
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
        setError("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    if (hasMounted) {
      fetchProfile();
    }
  }, [hasMounted]);

  // Fetch messages function
  const fetchMessages = useCallback(
    async (otherId: string, pageNum: number, reset: boolean = false) => {
      if (!otherId) return;

      try {
        const response = await fetch(
          `http://localhost:5000/api/chat/get/${otherId}/${pageNum}`,
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch messages");
        }

        const data = await response.json();
        setHasMore(!data.isLastPage);

        if (reset) {
          setMessages(data.messages || []);
          setPage(1);
        } else {
          setMessages((prev) => [...(data.messages || []), ...prev]);
          setPage(pageNum);
        }
      } catch (error) {
        console.error("Error fetching messages:", error);
        setError("Failed to load messages");
      } finally {
        setIsFetchingMore(false);
      }
    },
    []
  );

  // Load messages when selectedUser changes
  useEffect(() => {
    if (!selectedUser?.id || !hasMounted) return;

    setMessages([]);
    setPage(1);
    setHasMore(true);
    fetchMessages(selectedUser.id, 1, true);

    // Scroll to bottom after a short delay
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
    }, 100);
  }, [selectedUser, fetchMessages, hasMounted]);

  // Polling for new messages every 15 seconds
  useEffect(() => {
    if (!selectedUser?.id || !hasMounted) return;

    // Clear existing polling
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    pollingRef.current = setInterval(() => {
      fetchMessages(selectedUser.id, 1, true);
    }, 1000);

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [selectedUser, fetchMessages, hasMounted]);

  // Infinite scroll for loading older messages
  useEffect(() => {
    if (!hasMounted) return;

    const handleScroll = () => {
      if (
        !chatContainerRef.current ||
        !selectedUser?.id ||
        !hasMore ||
        isFetchingMore
      )
        return;

      if (chatContainerRef.current.scrollTop === 0) {
        setIsFetchingMore(true);
        fetchMessages(selectedUser.id, page + 1, false);
      }
    };

    const container = chatContainerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
      return () => container.removeEventListener("scroll", handleScroll);
    }
  }, [selectedUser, page, hasMore, isFetchingMore, fetchMessages, hasMounted]);

  // Send message function with AI Assistant detection
  const handleSendMessage = async () => {
    if (!message.trim() || !selectedUser?.id) return;

    const messageContent = message.trim();

    // Check if this is an AI Assistant request from a mentor
    const isAIRequest =
      messageContent.includes("@AI Assistant") && userRole === "mentor";

    setMessage("");

    // Optimistic update
    const tempMessage: Message = {
      _id: `temp-${Date.now()}`,
      sender_id: userId,
      receiver_id: selectedUser.id,
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempMessage]);

    // Scroll to bottom
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);

    try {
      const response = await fetch("http://localhost:5000/api/chat/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          receiver_id: selectedUser.id,
          content: messageContent,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      // Refresh messages to get the actual message with correct timestamp
      await fetchMessages(selectedUser.id, 1, true);

      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);

      // If this is an AI Assistant request, trigger roadmap generation
      if (isAIRequest) {
        await handleAIRoadmapGeneration();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setError("Failed to send message");
      // Remove the temporary message on error
      setMessages((prev) => prev.filter((msg) => msg._id !== tempMessage._id));
      setMessage(messageContent); // Restore the message
    }
  };

  // Handle AI roadmap generation
  const handleAIRoadmapGeneration = async () => {
    if (!selectedUser?.id || userRole !== "mentor") return;

    setIsGeneratingRoadmap(true);
    setRoadmapGenerated(false);
    setError(null);

    try {
      console.log("Fetching chat history for mentee:", selectedUser.id);

      // Test basic connectivity first
      try {
        const testResponse = await fetch(
          "http://localhost:5000/api/auth/profile",
          {
            credentials: "include",
          }
        );
        console.log("Backend connectivity test:", testResponse.status);
      } catch (connectError) {
        console.error("Backend connection failed:", connectError);
        throw new Error(
          "Cannot connect to backend server. Please check if the server is running on port 5000."
        );
      }

      // First, get the chat history
      const historyResponse = await fetch(
        `http://localhost:5000/api/chat/history/${selectedUser.id}`,
        {
          credentials: "include",
        }
      );

      console.log("History response status:", historyResponse.status);

      if (!historyResponse.ok) {
        const errorText = await historyResponse.text();
        console.error("Chat history error:", errorText);
        throw new Error(
          `Failed to fetch chat history: ${historyResponse.status} - ${errorText}`
        );
      }

      const chatHistory = await historyResponse.json();
      console.log("Chat history fetched:", chatHistory);

      // Validate the format before sending
      if (!chatHistory.mentee_id || !Array.isArray(chatHistory.conversation)) {
        console.error("Invalid chat history format:", chatHistory);
        throw new Error("Invalid chat history format received");
      }

      console.log("Sending to AI roadmap generation...");

      // Then, send it to the AI roadmap generation endpoint
      const roadmapResponse = await fetch(
        "http://localhost:5000/api/ai/roadmap",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(chatHistory),
        }
      );

      console.log("Roadmap response status:", roadmapResponse.status);

      if (!roadmapResponse.ok) {
        const errorText = await roadmapResponse.text();
        console.error("Roadmap generation error:", errorText);
        throw new Error(
          `Roadmap generation failed: ${roadmapResponse.status} - ${errorText}`
        );
      }

      const result = await roadmapResponse.json();
      console.log("Roadmap generation successful:", result);

      // Success
      setRoadmapGenerated(true);
    } catch (error) {
      if (error instanceof Error) {
        setError(`Failed to generate roadmap: ${error.message}`);
      } else {
        setError("Failed to generate roadmap due to an unknown error");
      }
    }
  };

  const respondToMeetingRequest = async (
    requestId: string,
    action: string,
    slot?: any
  ) => {
    await fetch("http://localhost:5000/api/scheduling/respond", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        request_id: requestId,
        action,
        slot,
      }),
    });

    if (selectedUser) {
      await fetchMessages(selectedUser.id, 1, true);
    }
  };

  // Add this function after handleAIRoadmapGeneration
  const handleCloseSuccessModal = () => {
    setIsGeneratingRoadmap(false);
    setRoadmapGenerated(false);
  };

  // Handle mention trigger
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setMessage(val);
    // Show mention if last char is '@' and not already present
    if (val.endsWith("@") && !val.includes("@AI Assistant")) {
      setShowAIMention(true);
    } else {
      setShowAIMention(false);
    }
  };

  // Handle mention selection with keyboard
  const handleMentionKeyDown = (e: React.KeyboardEvent) => {
    if (showAIMention) {
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        insertAIAssistantMention();
      } else if (e.key === "Escape") {
        setShowAIMention(false);
      }
    } else {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    }
  };

  // Insert @AI Assistant at cursor
  const insertAIAssistantMention = () => {
    if (!textareaRef.current) return;
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = message;
    // Replace last '@' with '@AI Assistant'
    const atIdx = value.lastIndexOf("@");
    const newValue =
      value.substring(0, atIdx) + "@AI Assistant " + value.substring(end);
    setMessage(newValue);
    setShowAIMention(false);
    // Move cursor after inserted mention
    setTimeout(() => {
      textarea.focus();
      textarea.selectionStart = textarea.selectionEnd =
        atIdx + "@AI Assistant ".length;
    }, 0);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Don't render anything until mounted to prevent hydration mismatch
  if (!hasMounted) {
    return null;
  }

  return (
    <DashboardLayout
      userRole={userRole}
      userName={userName}
      userEmail={userEmail}
    >
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chat</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {userRole === "mentor"
              ? "Select a mentee to chat with. Use @AI Assistant to generate roadmaps!"
              : "Chat with your mentor"}
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* AI Roadmap Generation Modal/Overlay */}
        {isGeneratingRoadmap && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl text-center flex items-center justify-center gap-2">
                  <Sparkles className="h-6 w-6 text-purple-500" />
                  AI Roadmap Generation
                </CardTitle>
                <CardDescription className="text-center">
                  {roadmapGenerated
                    ? "Roadmap generated successfully!"
                    : "Creating a personalized roadmap based on your conversation..."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!roadmapGenerated ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <div className="relative flex items-center justify-center mb-4">
                      {/* Cool animated loader */}
                      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500"></div>
                      <Sparkles className="absolute h-8 w-8 text-purple-700 animate-pulse" />
                    </div>
                    <p className="text-lg font-medium text-purple-700 animate-pulse">
                      Analyzing conversation...
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      This may take 3-4 minutes. Please wait.
                    </p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8">
                    <CheckCircle className="h-16 w-16 text-green-500 mb-4 animate-bounce" />
                    <h2 className="text-xl font-bold text-green-700 mb-2">
                      Roadmap Generated Successfully!
                    </h2>
                    <p className="text-center text-gray-600 mb-6">
                      The personalized roadmap has been created and updated
                      based on your conversation with {selectedUser?.name}.
                    </p>
                    <div className="flex gap-3 w-full">
                      <Button
                        onClick={handleCloseSuccessModal}
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white"
                      >
                        Return to Chat
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Conversations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {userRole === "mentor" ? (
                mentees.length > 0 ? (
                  mentees.map((mentee) => (
                    <div
                      key={mentee.id}
                      className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transition-colors ${
                        selectedUser?.id === mentee.id
                          ? "bg-purple-100 dark:bg-purple-900"
                          : "hover:bg-gray-100 dark:hover:bg-gray-800"
                      } ${
                        isGeneratingRoadmap
                          ? "pointer-events-none opacity-50"
                          : ""
                      }`}
                      onClick={() =>
                        !isGeneratingRoadmap && setSelectedUser(mentee)
                      }
                    >
                      <Avatar>
                        <AvatarFallback>
                          {mentee.name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{mentee.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          @{mentee.username}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-4">
                    No mentees found
                  </div>
                )
              ) : mentor ? (
                <div className="flex items-center space-x-3 p-2 rounded-lg bg-purple-100 dark:bg-purple-900">
                  <Avatar>
                    <AvatarFallback>
                      {mentor.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{mentor.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      @{mentor.username}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-4">
                  No mentor assigned
                </div>
              )}
            </CardContent>
          </Card>

          {/* Chat Area */}
          <Card className="lg:col-span-3 flex flex-col h-[calc(100vh-13rem)]">
            <CardHeader className="border-b">
              <div className="flex items-center space-x-3">
                <Avatar>
                  <AvatarFallback>
                    {selectedUser?.name?.charAt(0).toUpperCase() || "?"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle>
                    {selectedUser?.name || "Select a conversation"}
                  </CardTitle>
                  <CardDescription>
                    {selectedUser ? `@${selectedUser.username}` : ""}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent
              className={`flex-1 overflow-y-auto p-4 space-y-4 ${
                isGeneratingRoadmap ? "pointer-events-none opacity-50" : ""
              }`}
              ref={chatContainerRef}
            >
              {!selectedUser ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-400">
                    Select a conversation to start chatting
                  </div>
                </div>
              ) : (
                <>
                  {isFetchingMore && (
                    <div className="text-center text-gray-400 py-2">
                      Loading older messages...
                    </div>
                  )}

                  {messages.map((msg) => {
                    const isMe = msg.sender_id === userId;
                    const isMeetingRequest =
                      msg.meta?.kind === "meeting_request";
                    const containsAIAssistant =
                      msg.content.includes("@AI Assistant");

                    return (
                      <div
                        key={msg._id}
                        className={`flex ${
                          isMe ? "justify-end" : "justify-start"
                        }`}
                      >
                        <div
                          className={`max-w-[70%] p-3 rounded-2xl ${
                            isMe
                              ? containsAIAssistant
                                ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-br-md border-2 border-purple-300"
                                : "bg-[#9290C3] text-white rounded-br-md"
                              : "bg-[#1B1A55] text-white rounded-bl-md"
                          }`}
                        >
                          {isMeetingRequest ? (
                            <MeetingRequestCard
                              request={msg.meta}
                              userRole={userRole}
                              onRespond={(action, slot) =>
                                respondToMeetingRequest(
                                  msg.meta.request_id,
                                  action,
                                  slot
                                )
                              }
                            />
                          ) : (
                            <p className="text-sm whitespace-pre-wrap">
                              {containsAIAssistant && isMe ? (
                                <>
                                  {msg.content
                                    .split("@AI Assistant")
                                    .map((part, index, array) => (
                                      <span key={index}>
                                        {part}
                                        {index < array.length - 1 && (
                                          <span className="inline-flex items-center gap-1 bg-white/20 px-2 py-1 rounded text-xs font-semibold">
                                            <Sparkles className="h-3 w-3" />
                                            AI Assistant
                                          </span>
                                        )}
                                      </span>
                                    ))}
                                </>
                              ) : (
                                msg.content
                              )}
                            </p>
                          )}
                          <p className="text-xs text-white/70 mt-1">
                            {new Date(msg.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                      </div>
                    );
                  })}

                  <div ref={messagesEndRef} />
                </>
              )}
            </CardContent>

            <div
              className={`border-t p-4 ${
                isGeneratingRoadmap ? "pointer-events-none opacity-50" : ""
              }`}
            >
              <div className="flex items-end w-full space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  className="shrink-0"
                  disabled={isGeneratingRoadmap}
                >
                  <PaperclipIcon className="h-4 w-4" />
                </Button>

                <div className="relative flex-1">
                  <Textarea
                    ref={textareaRef}
                    placeholder={
                      selectedUser
                        ? `Message ${selectedUser.name}...`
                        : "Select a user to start chatting"
                    }
                    value={message}
                    onChange={handleInputChange}
                    onKeyDown={handleMentionKeyDown}
                    className="min-h-10 flex-1 resize-none"
                    rows={1}
                    disabled={!selectedUser}
                  />
                  {showAIMention && (
                    <div className="absolute left-2 bottom-12 z-50 bg-white dark:bg-gray-900 border rounded shadow p-2 w-48">
                      <div
                        className="flex items-center gap-2 cursor-pointer hover:bg-purple-100 dark:hover:bg-purple-900 rounded px-2 py-1"
                        onMouseDown={(e) => {
                          e.preventDefault();
                          insertAIAssistantMention();
                        }}
                      >
                        <Sparkles className="h-4 w-4 text-purple-500" />
                        <span className="font-semibold">@AI Assistant</span>
                        <span className="ml-auto text-xs text-gray-400">↵</span>
                      </div>
                    </div>
                  )}
                </div>

                <Button
                  className="bg-[#9290C3] hover:bg-[#7B68EE] shrink-0"
                  onClick={handleSendMessage}
                  disabled={message.trim() === "" || !selectedUser}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
