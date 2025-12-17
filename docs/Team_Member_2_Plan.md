# Implementation Plan: Relationship and Communication

This document outlines the implementation plan for the agents responsible for managing the mentor-mentee relationship and communication analysis.

## 🤖 Assigned Agents

### 1. MentorMatchingAgent
*   **Description:** This agent is responsible for finding the best mentor for each new mentee.
*   **Responsibilities:**
    *   Analyzes new mentee profiles, including their skills, goals, and learning preferences.
    *   Scans the pool of available mentors and scores them based on compatibility.
    *   Collaborates with the `LearningPathAgent` to get a preview of a potential roadmap for the top mentor candidates.
    *   Presents the final match recommendation to the mentee.
    *   Continuously re-evaluates existing mentor-mentee pairings for potential optimizations.

### 2. ConversationIntelligenceAgent
*   **Description:** This agent monitors and analyzes the conversations between mentors and mentees.
*   **Responsibilities:**
    *   Performs real-time analysis of chat messages to identify sentiment, key topics, and sentiment.
    *   Detects when a mentee is struggling with a concept or has a question that needs to be addressed.
    *   Identifies learning opportunities and suggests relevant resources or roadmap adjustments to the `LearningPathAgent`.
    *   Monitors the overall health of the conversation and alerts the `RelationshipManagerAgent` if it detects signs of disengagement or conflict.

### 3. RelationshipManagerAgent
*   **Description:** This agent focuses on the health and effectiveness of the mentor-mentee relationship.
*   **Responsibilities:**
    *   Monitors the overall engagement and satisfaction of both the mentor and the mentee.
    *   Acts as a "guidance counselor," providing support and resources to both parties.
    *   Intervenes proactively if it detects a risk of disengagement or conflict, based on input from the `ConversationIntelligenceAgent` and `AnalyticsAgent`.
    *   Orchestrates communication between other agents and the users, ensuring that the AI's actions are transparent and understandable.

---

## 🌊 Relevant Collaboration Flows

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
