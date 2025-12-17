# Implementation Plan: Core Learning Experience

This document outlines the implementation plan for the agents responsible for the core learning experience, including roadmap generation and mentee evaluation.

## 🤖 Assigned Agents

### 1. LearningPathAgent
*   **Description:** This agent designs and manages the personalized learning roadmaps for each mentee.
*   **Responsibilities:**
    *   Generates a personalized learning roadmap when a new mentor-mentee match is made.
    *   Dynamically adjusts the roadmap based on the mentee's performance, feedback from other agents (e.g., `ConversationIntelligenceAgent`, `AssessmentAndInterviewAgent`), and mentor input.
    *   Breaks down the roadmap into modules, each with clear objectives, subtopics, and resources.
    *   Enriches the roadmap with relevant articles, videos, and other learning materials using the Serper API.
    *   Presents the roadmap to the mentor for approval and to the mentee for learning.

### 2. AssessmentAndInterviewAgent
*   **Description:** This agent is responsible for evaluating the mentee's progress and understanding, and for conducting autonomous mock interviews.
*   **Responsibilities:**
    *   **Assessments:**
        *   Generates personalized assessments (quizzes, coding challenges, etc.) for each module in the roadmap.
        *   Analyzes the results of assessments to identify the mentee's strengths and weaknesses.
        *   Provides detailed feedback to the mentee and a summary report to the mentor and the `LearningPathAgent`.
    *   **Autonomous Mock Interviews:**
        *   **Before the interview:** Analyzes the mentee's roadmap and weak areas to generate an adaptive question flow.
        *   **During the interview:** Changes the difficulty of questions based on the quality of the mentee's responses. It can also adjust its tone (e.g., supportive vs. challenging) to simulate different interview scenarios.
        *   **After the interview:** Sends a detailed report to the mentor, including a "skill delta" report, a confidence analysis, and communication score trends. This report is also shared with the `LearningPathAgent` for roadmap adjustments.

---

## 🌊 Relevant Collaboration Flows

### Flow 1: New Mentee Onboarding (Contribution)
*   **`LearningPathAgent`:**
    *   Generates a high-level roadmap for each of the top 3 mentors during the matching phase.
    *   Generates the complete, detailed roadmap once a match is confirmed and sends it for mentor approval.

### Flow 2: Adaptive Roadmap Adjustment
1.  **`ConversationIntelligenceAgent`:**
    *   Monitors the chat and detects that the mentee is consistently asking questions about a specific topic not covered in the current module.
    *   Sends a "roadmap update suggestion" to the `LearningPathAgent`.
2.  **`AssessmentAndInterviewAgent`:**
    *   The mentee fails an assessment for the current module.
    *   The agent sends an "assessment failed" notification to the `LearningPathAgent`.
3.  **`LearningPathAgent`:**
    *   Receives the inputs from the other agents.
    *   Decides to add a new remedial module to the roadmap to address the mentee's knowledge gap.
    *   Sends the updated roadmap to the mentor for approval and notifies the `RelationshipManagerAgent`.
4.  **`RelationshipManagerAgent`:**
    *   Notifies the mentee about the roadmap update and explains the reason for the change.

### Flow 3: Proactive Meeting Scheduling (Contribution)
*   **`AssessmentAndInterviewAgent`:**
    *   After a mentee passes a major milestone assessment, it sends a "milestone reached" notification to the `SchedulingAgent` to suggest a check-in meeting.

### Flow 4: Autonomous Mock Interview
1.  **`LearningPathAgent`:**
    *   The mentee reaches a designated interview point in their roadmap (e.g., midpoint or end).
    *   The agent sends a "request for interview" to the `AssessmentAndInterviewAgent`.
2.  **`AssessmentAndInterviewAgent`:**
    *   Receives the request and analyzes the mentee's roadmap and performance data to identify weak areas.
    *   Generates an adaptive question flow for the interview.
    *   Collaborates with the `SchedulingAgent` to find a suitable time for the interview.
3.  **`SchedulingAgent`:**
    *   Finds a time for the interview and schedules it, sending invitations to the mentee.
4.  **`AssessmentAndInterviewAgent`:**
    *   At the scheduled time, the agent initiates the mock interview with the mentee.
    *   During the interview, it adjusts the difficulty and tone of the questions based on the mentee's responses.
5.  **`AssessmentAndInterviewAgent`:**
    *   After the interview, the agent compiles a detailed report with a skill delta, confidence analysis, and communication score trends.
    *   It sends this report to the mentor and the `LearningPathAgent` for review and potential roadmap adjustments.
