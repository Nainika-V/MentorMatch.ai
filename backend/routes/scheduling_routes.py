from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required
from agents.scheduling_agent import SchedulingAgent

scheduling_bp = Blueprint("scheduling", __name__)

# Create a single agent instance
scheduling_agent = SchedulingAgent()


@scheduling_bp.route("/respond", methods=["POST"])
@token_required
def respond_to_meeting_request(current_user):
    """
    Mentor / Mentee response to a meeting request
    Body:
    {
        "request_id": "...",
        "action": "pick" | "accept" | "reject",
        "slot": { "start": "...", "end": "..." }   # only for mentor pick
    }
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    request_id = data.get("request_id")
    action = data.get("action")
    slot = data.get("slot")

    if not request_id or not action:
        return jsonify({"error": "request_id and action are required"}), 400

    # actor is the logged-in user
    actor_id = str(current_user["_id"])

    try:
        scheduling_agent.respond(
            actor_id=actor_id,
            request_id=request_id,
            action=action,
            slot=slot,
        )
    except Exception as e:
        print("Scheduling respond error:", e)
        return jsonify({"error": "Failed to process scheduling response"}), 500

    return jsonify({"status": "ok"}), 200
