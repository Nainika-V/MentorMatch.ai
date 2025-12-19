'use client';

import { useParams, useRouter } from 'next/navigation';
import DailyMeeting from '@/components/daily-meeting';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';

export default function DailyMeetPage() {
    const params = useParams();
    const router = useRouter();
    const roomUrl = params.roomUrl ? decodeURIComponent(params.roomUrl as string) : '';
    
    const [token, setToken] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [transcript, setTranscript] = useState<any[]>([]);
    const [meetingId, setMeetingId] = useState('');

    useEffect(() => {
        if (!roomUrl) {
            setError("Room URL is missing.");
            setLoading(false);
            return;
        }

        const fetchToken = async () => {
            try {
                // Extract room name from the URL
                const roomName = new URL(roomUrl).pathname.split('/').pop();
                if (!roomName) {
                    throw new Error("Could not determine room name from URL.");
                }

                const tokenRes = await fetch("http://localhost:5000/api/meetings/daily/token", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ room_name: roomName }),
                });

                if (!tokenRes.ok) {
                    const errorData = await tokenRes.json();
                    throw new Error(errorData.message || "Failed to generate meeting token.");
                }
                const { token: meetingToken } = await tokenRes.json();
                setToken(meetingToken);

                // Get meeting ID by room name
                const meetingRes = await fetch(`http://localhost:5000/api/meetings/by-room/${roomName}`, {
                    credentials: 'include'
                });
                if (meetingRes.ok) {
                    const meetingData = await meetingRes.json();
                    setMeetingId(meetingData.meeting_id);
                }

            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchToken();
    }, [roomUrl]);

    if (loading) {
        return <div className="flex items-center justify-center h-screen">Loading meeting...</div>;
    }

    if (error) {
        return <div className="flex items-center justify-center h-screen text-red-500">{error}</div>;
    }

    const urlWithToken = `${roomUrl}?t=${token}`;

    const handleEndMeeting = async () => {
        console.log('BUTTON CLICKED!'); // This should appear first
        console.log('End meeting clicked. Meeting ID:', meetingId, 'Transcript length:', transcript.length);
        
        if (meetingId && transcript.length > 0) {
            try {
                console.log('Sending transcript to backend...');
                const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}/transcript`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ transcript })
                });
                
                if (response.ok) {
                    console.log('Transcript saved successfully');
                } else {
                    console.error('Failed to save transcript:', await response.text());
                }
            } catch (err) {
                console.error('Failed to save transcript:', err);
            }
        } else {
            console.log('No meeting ID or transcript to save');
        }
        router.push('/schedule');
    };

    return (
        <>
            <div className="absolute top-4 right-4 z-[9999] pointer-events-auto">
                <Button 
                    onClick={handleEndMeeting} 
                    variant="destructive" 
                    className="bg-red-600 hover:bg-red-700 text-white font-bold px-6 py-3 text-lg"
                >
                    End Meeting
                </Button>
            </div>
            <div className="relative h-screen w-screen">
                <DailyMeeting 
                    roomUrl={urlWithToken} 
                    onTranscriptUpdate={setTranscript}
                    onMeetingIdUpdate={setMeetingId}
                />
            </div>
        </>
    );
}
