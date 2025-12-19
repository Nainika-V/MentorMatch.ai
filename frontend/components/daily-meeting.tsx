'use client';

interface DailyMeetingProps {
    roomUrl: string;
}

const DailyMeeting: React.FC<DailyMeetingProps> = ({ roomUrl }) => {
    return (
        <iframe
            src={roomUrl}
            style={{ height: '100vh', width: '100vw', border: '0' }}
            allow="camera; microphone; fullscreen; display-capture"
        ></iframe>
    );
};

export default DailyMeeting;
