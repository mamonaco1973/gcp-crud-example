import json
import os
import uuid
from datetime import datetime, timezone

from google.cloud import firestore

db = firestore.Client()
COLLECTION = "notes"
OWNER = "global"
CORS_ORIGIN = os.environ.get("CORS_ALLOW_ORIGIN", "*")


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": CORS_ORIGIN,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def _json(data, status=200):
    return (json.dumps(data), status, {**_cors_headers(), "Content-Type": "application/json"})


def notes(request):
    if request.method == "OPTIONS":
        return ("", 204, _cors_headers())

    # Path is "/" for collection endpoints, "/{id}" for item endpoints.
    path = request.path.strip("/")
    note_id = path if path else None

    if request.method == "POST" and note_id is None:
        return _create(request)
    if request.method == "GET" and note_id is None:
        return _list()
    if request.method == "GET" and note_id:
        return _get(note_id)
    if request.method == "PUT" and note_id:
        return _update(request, note_id)
    if request.method == "DELETE" and note_id:
        return _delete(note_id)

    return _json({"error": "Not found"}, 404)


def _create(request):
    try:
        body = request.get_json(silent=True) or {}
        title = body.get("title", "").strip()
        note = body.get("note", "").strip()

        if not title or not note:
            return _json({"error": "title and note are required"}, 400)

        note_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "owner": OWNER,
            "id": note_id,
            "title": title,
            "note": note,
            "created_at": now,
            "updated_at": now,
        }
        db.collection(COLLECTION).document(note_id).set(item)
        return _json({"id": note_id, "title": title, "note": note}, 201)
    except Exception as e:
        return _json({"error": str(e)}, 500)


def _list():
    try:
        docs = db.collection(COLLECTION).where("owner", "==", OWNER).stream()
        items = [doc.to_dict() for doc in docs]
        return _json({"items": items})
    except Exception as e:
        return _json({"error": str(e)}, 500)


def _get(note_id):
    try:
        doc = db.collection(COLLECTION).document(note_id).get()
        if not doc.exists:
            return _json({"error": "Note not found"}, 404)
        return _json(doc.to_dict())
    except Exception as e:
        return _json({"error": str(e)}, 500)


def _update(request, note_id):
    try:
        body = request.get_json(silent=True) or {}
        title = body.get("title", "").strip()
        note = body.get("note", "").strip()

        if not title or not note:
            return _json({"error": "title and note are required"}, 400)

        ref = db.collection(COLLECTION).document(note_id)
        if not ref.get().exists:
            return _json({"error": "Note not found"}, 404)

        now = datetime.now(timezone.utc).isoformat()
        ref.update({"title": title, "note": note, "updated_at": now})
        return _json(ref.get().to_dict())
    except Exception as e:
        return _json({"error": str(e)}, 500)


def _delete(note_id):
    try:
        ref = db.collection(COLLECTION).document(note_id)
        if not ref.get().exists:
            return _json({"error": "Note not found"}, 404)
        ref.delete()
        return _json({"message": "Note deleted"})
    except Exception as e:
        return _json({"error": str(e)}, 500)
