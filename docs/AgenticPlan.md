# MentorMatch.ai - Agentic Implementation Plan

This document outlines the agentic architecture for MentorMatch.ai, detailing the specialized agents, their responsibilities, and the collaborative workflows between them.

## 🤖 Core Agents

The agentic system will be composed of the following specialized agents:

1.  **MentorMatchingAgent:** The "Recruiter"
2.  **LearningPathAgent:** The "Curriculum Designer"
3.  **ConversationIntelligenceAgent:** The "Conversation Analyst"
4.  **AssessmentAndInterviewAgent:** The "Examiner"
5.  **SchedulingAgent:** The "Coordinator"
6.  **RelationshipManagerAgent:** The "Guidance Counselor"
7.  **AnalyticsAgent:** The "Data Scientist"

---

## 🎭 Agent Descriptions and Responsibilities

### 1. MentorMatchingAgent
*   **Description:** This agent is responsible for finding the best mentor for each new mentee.
*   **Responsibilities:**
    *   Analyzes new mentee profiles, including their skills, goals, and learning preferences.
    *   Scans the pool of available mentors and scores them based on compatibility.
    *   Collaborates with the `LearningPathAgent` to get a preview of a potential roadmap for the top mentor candidates.
    *   Presents the final match recommendation to the mentee.
    *   Continuously re-evaluates existing mentor-mentee pairings for potential optimizations.

### 2. LearningPathAgent
*   **Description:** This agent designs and manages the personalized learning roadmaps for each mentee.
*   **Responsibilities:**
    *   Generates a personalized learning roadmap when a new mentor-mentee match is made.
    *   Dynamically adjusts the roadmap based on the mentee's performance, feedback from other agents (e.g., `ConversationIntelligenceAgent`, `AssessmentAndInterviewAgent`), and mentor input.
    *   Breaks down the roadmap into modules, each with clear objectives, subtopics, and resources.
    *   Enriches the roadmap with relevant articles, videos, and other learning materials using the Serper API.
    *   Presents the roadmap to the mentor for approval and to the mentee for learning.

### 3. ConversationIntelligenceAgent
*   **Description:** This agent monitors and analyzes the conversations between mentors and mentees.
*   **Responsibilities:**
    *   Performs real-time analysis of chat messages to identify sentiment, key topics, and sentiment.
    *   Detects when a mentee is struggling with a concept or has a question that needs to be addressed.
    *   Identifies learning opportunities and suggests relevant resources or roadmap adjustments to the `LearningPathAgent`.
    *   Monitors the overall health of the conversation and alerts the `RelationshipManagerAgent` if it detects signs of disengagement or conflict.

### 4. AssessmentAndInterviewAgent
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

### 5. SchedulingAgent
*   **Description:** This agent handles all scheduling-related tasks.
*   **Responsibilities:**
    *   Integrates with external calendars (Google Calendar, Outlook, etc.) to access the availability of mentors and mentees.
    *   Proactively suggests meeting times when it detects a need for a session (e.g., after a difficult assessment, or when a major milestone is reached).
    *   Understands natural language requests for scheduling within the chat.
    *   Sends meeting invitations and reminders to both the mentor and the mentee.

### 6. RelationshipManagerAgent
*   **Description:** This agent focuses on the health and effectiveness of the mentor-mentee relationship.
*   **Responsibilities:**
    *   Monitors the overall engagement and satisfaction of both the mentor and the mentee.
    *   Acts as a "guidance counselor," providing support and resources to both parties.
    *   Intervenes proactively if it detects a risk of disengagement or conflict, based on input from the `ConversationIntelligenceAgent` and `AnalyticsAgent`.
    *   Orchestrates communication between other agents and the users, ensuring that the AI's actions are transparent and understandable.

### 7. AnalyticsAgent
*   **Description:** This agent is the "data scientist" of the system, responsible for learning from the platform's data.
*   **Responsibilities:**
    *   Collects and analyzes data from all other agents and user interactions.
    *   Identifies patterns and trends in the data to improve the performance of the other agents.
    *   Builds and maintains machine learning models to predict outcomes, such as the likelihood of a mentee's success or the risk of a mentor's burnout.
    *   Provides insights and reports to the development team to guide the future development of the platform.

---

## 🌊 Agent Collaboration Flows

The agents work together in a coordinated fashion to provide a seamless and intelligent user experience. Here are a few examples of their collaborative workflows:

### Flow 1: New Mentee Onboarding
1.  **User Action:** A new mentee signs up.
2.  **`MentorMatchingAgent`:**
    *   Analyzes the new mentee's profile.
    *   Queries the database for potential mentors.
    *   Sends a request to the `LearningPathAgent` for a "roadmap preview" for the top 3 mentor candidates.
3.  **`LearningPathAgent`:**
    *   Generates a high-level roadmap for each of the top 3 mentors.
    *   Sends the roadmap previews back to the `MentorMatchingAgent`.
4.  **`MentorMatchingAgent`:**
    *   Uses the roadmap previews to make a final match recommendation.
    *   Notifies the `RelationshipManagerAgent` of the new match.
5.  **`RelationshipManagerAgent`:**
    *   Initiates the relationship, sending a welcome message to both the mentor and the mentee.
    *   Requests the `LearningPathAgent` to generate the full, detailed roadmap.
6.  **`LearningPathAgent`:**
    *   Generates the complete roadmap and sends it to the mentor for approval.

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

### Flow 3: Proactive Meeting Scheduling
1.  **`AssessmentAndInterviewAgent`:**
    *   The mentee has just passed a major milestone assessment.
    *   The agent sends a "milestone reached" notification to the `SchedulingAgent`.
2.  **`SchedulingAgent`:**
    *   Receives the notification and decides that this is a good time for a check-in meeting.
    *   Checks the calendars of the mentor and the mentee for mutual availability.
    *   Sends a message to the chat, proposing a few potential meeting times.
3.  **User Action:** The mentor or mentee confirms one of the proposed times in the chat.
4.  **`SchedulingAgent`:**
    *   Detects the confirmation message.
    *   Books the meeting in their calendars and sends an invitation.

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