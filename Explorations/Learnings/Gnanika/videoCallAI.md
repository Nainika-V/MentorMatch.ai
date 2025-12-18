# Plan for AI-Powered Video Call Analysis

This document outlines the plan to integrate Jitsi video calls into the MentorMatch.ai platform and run an AI system on the calls to provide valuable insights for mentors and mentees, including a new "technical points" feature to automatically update user roadmaps.

## 1. Jitsi Video Call Integration

The first step is to replace the current system of using external meeting links with a fully integrated Jitsi-based video call solution.

### 1.1. Backend Integration

- **Refactor Google Meet Service:** Rename `backend/services/google_meet_service.py` to `backend/services/video_conference_service.py`. The existing logic will be replaced with functions to generate unique Jitsi room names.
- **Update Meeting Routes:** Modify `backend/routes/meeting_routes.py` to:
    - Use the new `video_conference_service.py` to generate a `room_name` for each meeting.
    - Remove the expectation of a `meeting_link` from the request body.
- **Update Data Model:** The meeting data model, currently implicit in the routes, will be updated to use a `room_name` field instead of `meeting_link`.

### 1.2. Frontend Integration

- **Install Jitsi React SDK:** The `@jitsi/react-sdk` library will be installed in the `frontend` directory.
- **Create a `JitsiMeet` component:** A new React component will be created in `frontend/components/` to encapsulate the Jitsi meeting functionality.
- **Update the Schedule Page:** The existing `frontend/app/schedule/page.tsx` will be modified to:
    - Remove the input field for the meeting link.
    - The "Join Now" button will launch the `JitsiMeet` component within the MentorMatch.ai platform, using the generated room name.

## 2. AI-Powered Meeting Analysis & "Technical Points"

Once Jitsi is integrated, we will implement an AI system to analyze the meeting audio and provide insights.

### 2.1. Audio Capturing and Transcription

- **Research Audio Capturing:** We will investigate methods to capture the audio from the Jitsi meeting. Client-side audio capture appears to be the most direct approach.
- **Enhance Speech Service:** A new function will be added to `backend/services/speech_service.py` to handle the transcription of the captured audio, complete with timestamps.

### 2.2. "Technical Points" Extraction and Roadmap Update

- **Create `extract_technical_points` function:** A new function will be added to `backend/services/ai_service.py`. This function will:
    - Analyze the meeting transcript to identify key technical topics discussed.
    - Assess the mentee's grasp of these topics, noting areas of difficulty or misunderstanding. These will be the "technical points".
- **Automate Roadmap Updates:** The extracted "technical points" will be passed as instructions to the existing `edit_roadmap` function in `backend/utils/roadmap_utils.py`, which will automatically update the mentee's learning roadmap.

### 2.3. Meeting Summary and Behavioral Analysis

- **Generate Summaries:** The `extract_technical_points` function in `backend/services/ai_service.py` will also generate a summary of the meeting for both the mentor and the mentee.
- **Behavioral Analysis:** The system will analyze the mentee's participation in the conversation (e.g., speaking time) to provide feedback to the mentor.

### 2.4. Database and API

- **Create `meeting_analysis` collection:** A new table/collection will be added to the database to store the meeting transcript, "technical points", summaries, and behavioral analysis.
- **Create New API Endpoint:** A new endpoint will be created, likely in `backend/routes/meeting_routes.py`, to initiate the post-meeting analysis.

### 2.5. Frontend Updates

- **Dynamic Roadmap Display:** The `frontend/app/roadmap/page.tsx` component will be updated to dynamically display the modified roadmap after a meeting analysis is complete.
- **Display Meeting Insights:** The meeting summary will be made available to both mentor and mentee. The behavioral analysis will be displayed privately to the mentor. This could be on a new meeting details page or integrated into the existing dashboard.