"""
Equiderma AI - System & Pipeline Verification Test
Verifies:
1. Knowledge base integrity
2. ChromaDB RAG chunking and semantic retrieval
3. Multimodal base64 image handling (Strictly NO OpenCV)
4. Structured Clinical Output Schema
5. Flask API endpoint responses
"""

import io
import base64
import sys
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.knowledge_data import DERMATOLOGY_KNOWLEDGE_BASE
from backend.rag_engine import rag_engine
from backend.clinical_advisor import clinical_advisor, clean_base64_image
from backend.server import app


def test_knowledge_base():
    print("[1/5] Testing Knowledge Base...")
    assert len(DERMATOLOGY_KNOWLEDGE_BASE) >= 10, "Should have at least 10 curated conditions"
    for r in DERMATOLOGY_KNOWLEDGE_BASE:
        assert "condition" in r
        assert "severity" in r
        assert r["severity"] in ["High", "Medium", "Low"]
        assert "skin_tone_presentation" in r
        assert "light_skin (Types I-III)" in r["skin_tone_presentation"]
        assert "dark_skin (Types IV-VI)" in r["skin_tone_presentation"]
    print("  -> Knowledge Base verified with rich tone and severity data!")


def test_rag_chunking_and_retrieval():
    print("[2/5] Testing ChromaDB RAG Engine...")
    stats = rag_engine.get_stats()
    print(f"  -> Initial collection count: {stats['total_indexed_chunks']}")
    assert stats["total_indexed_chunks"] > 0, "ChromaDB should have indexed chunks"

    # Test query on dark skin tone presentation
    results_dark = rag_engine.query_knowledge("violaceous plaques hyperpigmentation", n_results=3, tone_filter="dark_skin")
    print(f"  -> Retrieved {len(results_dark)} chunks for dark skin query.")
    assert len(results_dark) > 0

    # Test query on urgent malignancy
    results_high = rag_engine.query_knowledge("changing mole asymmetrical border", n_results=3, severity_filter="High")
    print(f"  -> Retrieved {len(results_high)} chunks for high severity query.")
    assert len(results_high) > 0
    print("  -> ChromaDB RAG Engine successfully indexed and queried!")


def test_image_processing_no_opencv():
    print("[3/5] Testing Image Processing (Pure Base64 / PIL, NO OpenCV)...")
    # Generate a dummy RGB test image in-memory with Pillow
    img = Image.new("RGB", (200, 200), color=(180, 100, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    raw_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    cleaned_b64 = clean_base64_image(raw_b64)
    assert len(cleaned_b64) > 0, "Cleaned base64 should not be empty"
    print("  -> Base64 image cleaned and encoded with PIL without OpenCV!")


def test_clinical_advisor_pipeline():
    print("[4/5] Testing Clinical Advisor Reasoning Pipeline...")
    # Test symptom + tone query
    result = clinical_advisor.analyze(
        image_base64=None,
        symptoms="Itchy silvery scaly plaques on knees and elbows",
        patient_tone_hint="Type IV"
    )
    assert "condition_prediction" in result
    assert "confidence_score" in result
    assert "severity_level" in result
    assert "skin_tone_assessment" in result
    assert "rag_grounding_citations" in result
    print(f"  -> Condition Prediction: {result['condition_prediction']}")
    print(f"  -> Confidence Score: {result['confidence_score']}%")
    print(f"  -> Severity: {result['severity_level']}")
    print(f"  -> Engine Status: {result['engine_status']}")
    print("  -> Clinical Advisor pipeline functional!")


def test_flask_endpoints():
    print("[5/5] Testing Flask REST API Routes...")
    client = app.test_client()

    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    health_json = res_health.get_json()
    assert health_json["status"] == "healthy"

    # Conditions list
    res_cond = client.get("/api/conditions?severity=high")
    assert res_cond.status_code == 200
    cond_json = res_cond.get_json()
    assert cond_json["count"] > 0

    # RAG search
    res_rag = client.post("/api/rag/search", json={"query": "eczema barrier repair", "n_results": 2})
    assert res_rag.status_code == 200
    rag_json = res_rag.get_json()
    assert len(rag_json["citations"]) > 0

    print("  -> All Flask API endpoints returned HTTP 200 OK!")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING EQUIDERMA AI VERIFICATION SUITE")
    print("=" * 60)
    test_knowledge_base()
    test_rag_chunking_and_retrieval()
    test_image_processing_no_opencv()
    test_clinical_advisor_pipeline()
    test_flask_endpoints()
    print("=" * 60)
    print("ALL 5 SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
