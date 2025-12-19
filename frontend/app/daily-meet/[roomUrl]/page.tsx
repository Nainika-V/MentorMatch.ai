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

    return (
        <div className="relative h-screen w-screen">
            <DailyMeeting roomUrl={urlWithToken} />
            <div className="absolute top-4 right-4 z-10">
                <Button onClick={() => router.push('/schedule')} variant="destructive">
                    End Meeting
                </Button>
            </div>
        </div>
    );
}
