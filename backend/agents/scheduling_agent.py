from database.db import users, meetings, meeting_requests
from services.chat_service import send_message
from services.daily_service import create_daily_room
from bson.objectid import ObjectId
import datetime

INACTIVITY_DAYS = 10
DEFAULT_MEETING_DURATION_MIN = 60

TIME_BUCKETS = {
    "morning": (8, 12),
    "afternoon": (12, 17),
    "evening": (17, 22),
}


class SchedulingAgent:
    def __init__(self):
        pass

    def proactive_from_assessment(self, mentor_id, mentee_id, score):
        print("Proactive From Assessment...")
        if score >= 80:
            return

        reason = f"assessment_low_score:{score}"
        self._create_meeting_request(mentor_id, mentee_id, reason)

    def proactive_from_inactivity(self, mentor_id, mentee_id):
        last_meeting = meetings.find_one(
            {
                "mentor_id": mentor_id,
                "mentee_id": mentee_id,
            },
            sort=[("start_time", -1)],
        )

        if last_meeting:
            delta = datetime.datetime.utcnow() - last_meeting["start_time"]
            if delta.days < INACTIVITY_DAYS:
                return

        reason = "long_inactivity"
        self._create_meeting_request(mentor_id, mentee_id, reason)

    def respond(self, actor_id, request_id, action, slot=None):
        req = meeting_requests.find_one({"_id": ObjectId(request_id)})
        if not req or req["status"] == "scheduled":
            return

        mentor_id = str(req["mentor_id"])
        mentee_id = str(req["mentee_id"])

        # ---- Mentor actions ----
        if req["status"] == "pending_mentor" and actor_id == mentor_id:
            if action == "pick":
                meeting_requests.update_one(
                    {"_id": ObjectId(request_id)},
                    {
                        "$set": {
                            "status": "pending_mentee",
                            "selected_slot": slot,
                            "updated_at": datetime.datetime.utcnow(),
                        }
                    },
                )

                send_message(
                    "system",
                    mentee_id,
                    "SchedulingAgent: Mentor selected a slot. Please confirm.",
                    meta={
                        "kind": "meeting_request",
                        "request_id": request_id,
                        "stage": "mentee_confirm",
                        "slot": slot,
                    },
                    message_type="system",
                    participants_override=[mentor_id, mentee_id],
                )

            elif action == "reject":
                self._reject_request(req)

        # ---- Mentee actions ----
        elif req["status"] == "pending_mentee" and actor_id == mentee_id:
            if action == "accept":
                self._schedule_meeting(req)

            elif action == "reject":
                self._reject_request(req)

    def _create_meeting_request(self, mentor_id, mentee_id, reason):
        # Prevent duplicates
        print("Create Meeting Request")
        existing = meeting_requests.find_one(
            {
                "mentor_id": mentor_id,
                "mentee_id": mentee_id,
                "status": {"$in": ["pending_mentor", "pending_mentee"]},
            }
        )
        if existing:
            return

        mentor = users.find_one({"_id": ObjectId(mentor_id)})
        mentee = users.find_one({"_id": ObjectId(mentee_id)})

        mentor_avail = mentor.get("profile", {}).get("availability", {})
        mentee_avail = mentee.get("profile", {}).get("availability", {})

        slots = self._generate_slots(mentor_avail, mentee_avail)

        if not slots:
            # Send a system message to both mentor and mentee
            send_message(
                "system",
                mentor_id,
                "SchedulingAgent: No common meeting slots found with your mentee. Please update your availability.",
                message_type="system",
                participants_override=[mentor_id, mentee_id],
            )
            send_message(
                "system",
                mentee_id,
                "SchedulingAgent: No common meeting slots found with your mentor. Please update your availability.",
                message_type="system",
                participants_override=[mentor_id, mentee_id],
            )
            return

        req = {
            "mentor_id": mentor_id,
            "mentee_id": mentee_id,
            "status": "pending_mentor",
            "reason": reason,
            "suggested_slots": slots,
            "selected_slot": None,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
        }

        res = meeting_requests.insert_one(req)
        request_id = str(res.inserted_id)

        send_message(
            "system",
            mentor_id,
            "SchedulingAgent: Suggested meeting slots. Please pick one.",
            meta={
                "kind": "meeting_request",
                "request_id": request_id,
                "stage": "mentor_pick",
                "slots": slots,
            },
            message_type="system",
            participants_override=[mentor_id, mentee_id],
        )

    def _schedule_meeting(self, req):
        slot = req["selected_slot"]
        start = datetime.datetime.fromisoformat(slot["start"])
        end = datetime.datetime.fromisoformat(slot["end"])

        # Generate a title for the meeting
        reason = req.get("reason", "Mentorship Meeting")
        if reason.startswith("assessment_low_score:"):
            score = reason.split(":")[1]
            title = f"Follow-up for low assessment score ({score}%)"
        elif reason == "long_inactivity":
            title = "Follow-up for long inactivity"
        else:
            title = "Mentorship Meeting"

        room_info = create_daily_room()

        meeting = {
            "mentor_id": req["mentor_id"],
            "mentee_id": req["mentee_id"],
            "title": title,  # Added title
            "start_time": start,
            "end_time": end,
            "room_url": room_info['url'],
            "room_name": room_info['name'],
            "status": "scheduled",
            "created_at": datetime.datetime.utcnow(),
        }

        meetings.insert_one(meeting)

        meeting_requests.update_one(
            {"_id": req["_id"]},
            {"$set": {"status": "scheduled", "updated_at": datetime.datetime.utcnow()}},
        )

        send_message(
            "system",
            req["mentor_id"],
            "SchedulingAgent: Meeting scheduled successfully.",
            meta={
                "kind": "meeting_request",
                "request_id": str(req["_id"]),
                "stage": "scheduled",
            },
            message_type="system",
            participants_override=[req["mentor_id"], req["mentee_id"]],
        )

    def _reject_request(self, req):
        meeting_requests.update_one(
            {"_id": req["_id"]},
            {"$set": {"status": "rejected", "updated_at": datetime.datetime.utcnow()}},
        )

        message_content = "The previous meeting request was rejected. Please coordinate to schedule a new meeting soon to analyze performance and stay updated."

        send_message(
            "system",
            req["mentor_id"],
            f"SchedulingAgent: {message_content}",
            message_type="system",
            participants_override=[req["mentor_id"], req["mentee_id"]],
        )

    def _generate_slots(self, mentor_avail, mentee_avail):
        slots = []
        now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        def get_buckets_for_day(availability_list, day_name):
            buckets = []
            if not isinstance(availability_list, list):
                return buckets
            for item in availability_list:
                if item.startswith(day_name):
                    try:
                        bucket = item.split(" ")[1].lower()
                        if bucket in TIME_BUCKETS:
                            buckets.append(bucket)
                    except IndexError:
                        continue  # Ignore malformed items
            return buckets

        for day_offset in range(1, 8):
            day = now + datetime.timedelta(days=day_offset)
            weekday = day.strftime("%A")

            mentor_buckets = get_buckets_for_day(mentor_avail, weekday)
            mentee_buckets = get_buckets_for_day(mentee_avail, weekday)

            common = set(mentor_buckets) & set(mentee_buckets)

            for bucket in common:
                start_h, end_h = TIME_BUCKETS[bucket]
                start = day.replace(hour=start_h)
                end = start + \
                    datetime.timedelta(minutes=DEFAULT_MEETING_DURATION_MIN)

                if end.hour <= end_h:
                    slots.append(
                        {
                            "start": start.isoformat(),
                            "end": end.isoformat(),
                        }
                    )

        return slots[:5]


