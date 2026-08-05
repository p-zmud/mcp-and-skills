"""Tools: Sharing (shared collections and collaborators).

v1 endpoints:
  POST   /collection/{id}/sharing          invite collaborators {role, emails}  (outbound, confirm)
  GET    /collection/{id}/sharing          list collaborators
  PUT    /collection/{id}/sharing/{userId} change access level {role}
  DELETE /collection/{id}/sharing/{userId} remove a collaborator                (confirm)
  POST   /collection/{id}/join             accept an invitation {token}

role: "member" (write) or "viewer" (read only).
"""
from __future__ import annotations

from .. import config
from ..common import RaindropError, fmt, get_client, mcp, require_confirm


@mcp.tool()
def raindrop_share_collection(
    collection_id: int, emails: list[str], role: str = "member", confirm: bool = False
) -> str:
    """Invites collaborators to a collection (SENDS email). POST /collection/{id}/sharing.

    This reaches outside your account (real invitations to real people), so it
    needs confirm=True.

    Args:
        collection_id: Collection to share.
        emails: Email addresses to invite.
        role: "member" (write) or "viewer" (read only).
        confirm: Must be True - real invitations go out.
    """
    if not emails:
        return "Error: pass a non-empty emails list."
    if role not in {"member", "viewer"}:
        return 'Error: role must be "member" or "viewer".'
    warn = require_confirm(confirm, f"sending invitations to collection {collection_id}: {emails}")
    if warn:
        return warn
    try:
        data = get_client().call(
            "POST", f"/collection/{collection_id}/sharing", json={"role": role, "emails": emails}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_get_collaborators(collection_id: int) -> str:
    """Lists the collaborators on a collection. GET /collection/{id}/sharing."""
    try:
        data = get_client().call("GET", f"/collection/{collection_id}/sharing")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_change_collaborator(collection_id: int, user_id: int, role: str) -> str:
    """Changes a collaborator's access level. PUT /collection/{id}/sharing/{userId}.

    Args:
        collection_id: Collection ID.
        user_id: Collaborator ID (from raindrop_get_collaborators).
        role: "member" (write) or "viewer" (read only).
    """
    if role not in {"member", "viewer"}:
        return 'Error: role must be "member" or "viewer".'
    try:
        data = get_client().call(
            "PUT", f"/collection/{collection_id}/sharing/{user_id}", json={"role": role}
        )
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)


@mcp.tool()
def raindrop_remove_collaborator(collection_id: int, user_id: int, confirm: bool = False) -> str:
    """Removes a collaborator. DELETE /collection/{id}/sharing/{userId}. Needs confirm=True.

    Args:
        collection_id: Collection ID.
        user_id: Collaborator to remove.
        confirm: Must be True.
    """
    warn = require_confirm(
        confirm, f"removing collaborator {user_id} from collection {collection_id}"
    )
    if warn:
        return warn
    try:
        get_client().call("DELETE", f"/collection/{collection_id}/sharing/{user_id}")
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return f"Removed collaborator {user_id} from collection {collection_id}."


@mcp.tool()
def raindrop_accept_invitation(collection_id: int, token: str) -> str:
    """Accepts an invitation to a shared collection. POST /collection/{id}/join {token}.

    Args:
        collection_id: Collection ID from the invitation.
        token: The secret token from the invitation email.
    """
    try:
        data = get_client().call("POST", f"/collection/{collection_id}/join", json={"token": token})
    except (RaindropError, config.ConfigError) as e:
        return f"Error: {e}"
    return fmt(data)
