"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Badge } from "./badge";

interface MeetingRequestCardProps {
  request: {
    request_id: string;
    stage: "mentor_pick" | "mentee_confirm" | "scheduled" | "rejected";
    slots?: { start: string; end:string }[];
    slot?: { start: string; end: string };
  };
  userRole: "mentor" | "mentee";
  onRespond: (action: string, slot?: { start: string; end: string }) => void;
}

export function MeetingRequestCard({
  request,
  userRole,
  onRespond,
}: MeetingRequestCardProps) {
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);

  const handlePick = () => {
    if (selectedSlot) {
      const slot = request.slots?.find((s) => s.start === selectedSlot);
      if (slot) {
        onRespond("pick", slot);
      }
    }
  };

  const handleAccept = () => {
    onRespond("accept");
  };

  const handleReject = () => {
    onRespond("reject");
  };

  const isMentor = userRole === "mentor";

  const renderContent = () => {
    switch (request.stage) {
      case "mentor_pick":
        return isMentor ? (
          <RadioGroup onValueChange={setSelectedSlot}>
            {request.slots?.map((slot, index) => (
              <div key={index} className="flex items-center space-x-2">
                <RadioGroupItem value={slot.start} id={`slot-${index}`} />
                <Label htmlFor={`slot-${index}`}>
                  {new Date(slot.start).toLocaleString()} -{" "}
                  {new Date(slot.end).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Label>
              </div>
            ))}
          </RadioGroup>
        ) : (
          <p>Waiting for mentor to select a time slot.</p>
        );
      case "mentee_confirm":
        return (
          <div>
            <p>Selected slot:</p>
            <p className="font-semibold">
              {new Date(request.slot!.start).toLocaleString()} -{" "}
              {new Date(request.slot!.end).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
            {!isMentor && (
              <p className="mt-2 text-sm text-gray-500">
                Please confirm or reject the selected time.
              </p>
            )}
             {isMentor && (
              <p className="mt-2 text-sm text-gray-500">
                Waiting for mentee to confirm.
              </p>
            )}
          </div>
        );
      case "scheduled":
        return (
          <p className="text-green-600 font-semibold">
            Meeting scheduled successfully!
          </p>
        );
      case "rejected":
        return (
          <p className="text-red-600 font-semibold">
            Meeting request rejected.
          </p>
        );
      default:
        return null;
    }
  };

  const renderFooter = () => {
    if (request.stage === "mentor_pick" && isMentor) {
      return (
        <>
          <Button onClick={handlePick} disabled={!selectedSlot}>
            Pick Slot
          </Button>
          <Button variant="outline" onClick={handleReject}>
            Reject
          </Button>
        </>
      );
    }
    if (request.stage === "mentee_confirm" && !isMentor) {
      return (
        <>
          <Button onClick={handleAccept}>Accept</Button>
          <Button variant="outline" onClick={handleReject}>
            Reject
          </Button>
        </>
      );
    }
    return null;
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Meeting Request</CardTitle>
        <CardDescription>
          {request.stage === "mentor_pick" && isMentor &&
            "Your mentee needs a meeting. Please pick one of the suggested slots."}
          {request.stage === "mentor_pick" && !isMentor &&
            "Your mentor is selecting a meeting time."}
          {request.stage === "mentee_confirm" && isMentor &&
            "Waiting for your mentee to confirm the meeting time."}
          {request.stage === "mentee_confirm" && !isMentor &&
            "Your mentor has selected a slot. Please confirm or reject."}
          {request.stage === "scheduled" && "Meeting Scheduled"}
          {request.stage === "rejected" && "Meeting Rejected"}
        </CardDescription>
      </CardHeader>
      <CardContent>{renderContent()}</CardContent>
      <CardFooter className="flex justify-end space-x-2">
        {renderFooter()}
      </CardFooter>
    </Card>
  );
}
