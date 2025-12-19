'use client';

import { useEffect, useRef } from 'react';

interface DailyMeetingProps {
    roomUrl: string;
    onTranscriptUpdate: (transcript: any[]) => void;
    onMeetingIdUpdate: (meetingId: string) => void;
}

const DailyMeeting: React.FC<DailyMeetingProps> = ({ 
    roomUrl, 
    onTranscriptUpdate, 
    onMeetingIdUpdate 
}) => {
    const transcriptRef = useRef<any[]>([]);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        // Extract meeting ID from room URL
        const urlParts = roomUrl.split('/');
        const roomName = urlParts[urlParts.length - 1].split('?')[0];
        onMeetingIdUpdate(roomName);

        // Set up speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = false;
            
            recognitionRef.current.onresult = (event: any) => {
                const result = event.results[event.results.length - 1];
                if (result.isFinal) {
                    const newEntry = {
                        speaker: 'participant',
                        speaker_name: 'Speaker',
                        text: result[0].transcript,
                        timestamp: new Date().toISOString(),
                        duration: 0
                    };
                    
                    transcriptRef.current = [...transcriptRef.current, newEntry];
                    onTranscriptUpdate(transcriptRef.current);
                }
            };
            
            recognitionRef.current.start();
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
                recognitionRef.current = null;
            }
        };
    }, [roomUrl]);

    return (
        <iframe
            src={roomUrl}
            style={{ 
                height: '100vh', 
                width: '100vw', 
                border: '0',
                position: 'fixed',
                top: 0,
                left: 0,
                zIndex: 1
            }}
            allow="camera; microphone; fullscreen; display-capture"
        />
    );
};

export default DailyMeeting;
