#!/usr/bin/env python3
"""
Insert a Request-Reply XML chunk into Supabase `iflow_components` with embeddings.

Usage (PowerShell examples):
  python scripts/insert_iflow_component.py --file "unique-components/request-reply-chunk.xml"
  python scripts/insert_iflow_component.py --file "unique-components/request-reply-chunk.xml" --component-id "RequestReply_Chunk_001" --package-id "00000000-0000-0000-0000-000000000000"

Requires:
  - Supabase URL/KEY and OpenAI API key in config.py
  - Packages: supabase, langchain-openai
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import config

try:
    from supabase import create_client, Client
except Exception as e:  # pragma: no cover
    print(f"Supabase client import failed: {e}")
    sys.exit(1)

try:
    from langchain_openai import OpenAIEmbeddings
except Exception as e:  # pragma: no cover
    print(f"OpenAI embeddings import failed: {e}")
    sys.exit(1)


def load_xml(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"XML file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


def create_embeddings(texts: Dict[str, str]) -> Dict[str, Any]:
    """Create embeddings for provided fields using OpenAI."""
    embedder = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=getattr(config, "OPENAI_API_KEY", None) or ""
    )

    results: Dict[str, Any] = {}

    # Description
    desc = texts.get("description", "")
    results["description_embedding"] = embedder.embed_query(desc) if desc else None

    # Activity type
    act = texts.get("activity_type", "")
    results["activity_type_embedding"] = embedder.embed_query(act) if act else None

    # Code/XML (use embed_documents for longer text)
    code = texts.get("code", "")
    if code:
        code_vecs = embedder.embed_documents([code])
        results["code_embedding"] = code_vecs[0] if code_vecs else None
    else:
        results["code_embedding"] = None

    return results


def build_record(
    *,
    component_id: str,
    activity_type: str,
    xml_text: str,
    package_id: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the upsert record for iflow_components."""
    generated_desc = description or (
        "Request-Reply ServiceTask (ExternalCall semantics) component XML chunk for reuse."
    )

    # Minimal properties; expand if needed
    properties = {
        "source": "unique-components/request-reply-chunk.xml",
        "created_by": "insert_iflow_component.py",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "schema": "bpmn2.0",
    }

    emb = create_embeddings(
        {
            "description": generated_desc,
            "activity_type": activity_type,
            "code": xml_text,
        }
    )

    record: Dict[str, Any] = {
        "component_id": component_id,
        "package_id": package_id if package_id else None,
        "activity_type": activity_type,
        "description": generated_desc,
        "complete_bpmn_xml": xml_text,
        "properties": properties,
        "related_scripts": [],
        "code_embedding": emb.get("code_embedding"),
        "description_embedding": emb.get("description_embedding"),
        "activity_type_embedding": emb.get("activity_type_embedding"),
    }

    return record


def upsert_iflow_component(client: Client, record: Dict[str, Any]) -> Dict[str, Any]:
    """Upsert by component_id to avoid duplicates."""
    # Try to find existing row by component_id
    existing = client.table("iflow_components").select("id, component_id").eq(
        "component_id", record["component_id"]
    ).execute()

    if existing.data:
        row_id = existing.data[0]["id"]
        updated = client.table("iflow_components").update(record).eq("id", row_id).execute()
        return {"action": "update", "id": row_id, "data": updated.data}

    inserted = client.table("iflow_components").insert(record).execute()
    new_id = inserted.data[0]["id"] if inserted.data else None
    return {"action": "insert", "id": new_id, "data": inserted.data}


def main() -> int:
    parser = argparse.ArgumentParser(description="Insert Request-Reply XML as an iFlow component")
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the XML chunk file (e.g., unique-components/request-reply-chunk.xml)",
    )
    parser.add_argument(
        "--component-id",
        default=None,
        help="Component ID to store. Defaults to generated ID based on timestamp.",
    )
    parser.add_argument(
        "--package-id",
        default=None,
        help="Optional package UUID to link the component to.",
    )
    parser.add_argument(
        "--activity-type",
        default="RequestReply",
        help="Activity type to store (default: RequestReply)",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Optional human-readable description to store.",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    xml_text = load_xml(file_path)

    # Build component_id if not provided
    if args.component_id:
        component_id = args.component_id
    else:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        component_id = f"RequestReply_Chunk_{ts}"

    # Basic validation for package_id if provided
    package_id: Optional[str] = args.package_id
    if package_id:
        try:
            uuid.UUID(package_id)
        except Exception:
            print("Warning: Provided --package-id is not a valid UUID. It will be stored as-is or rejected by DB.")

    record = build_record(
        component_id=component_id,
        activity_type=args.activity_type,
        xml_text=xml_text,
        package_id=package_id,
        description=args.description,
    )

    # Create Supabase client
    sb_url = getattr(config, "SUPABASE_URL", None)
    sb_key = getattr(config, "SUPABASE_KEY", None)
    if not sb_url or not sb_key:
        print("Supabase credentials are missing in config.py (SUPABASE_URL/SUPABASE_KEY)")
        return 2

    client: Client = create_client(sb_url, sb_key)

    result = upsert_iflow_component(client, record)
    action = result.get("action")
    row_id = result.get("id")

    print("✅ Operation completed")
    print(f"Action: {action}")
    print(f"Row ID: {row_id}")
    print(f"Component ID: {component_id}")

    # Optional: print a brief summary JSON
    summary = {
        "action": action,
        "row_id": row_id,
        "component_id": component_id,
        "activity_type": args.activity_type,
        "package_id": package_id,
        "description_len": len(record.get("description") or ""),
        "xml_len": len(record.get("complete_bpmn_xml") or ""),
        "has_embeddings": {
            "code": record.get("code_embedding") is not None,
            "desc": record.get("description_embedding") is not None,
            "activity": record.get("activity_type_embedding") is not None,
        },
    }
    print(json.dumps(summary, indent=2))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())













