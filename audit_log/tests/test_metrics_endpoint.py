def test_metrics_endpoint_is_available(client):
    response = client.get("/metrics/")

    assert response.status_code == 200

    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("text/plain")

    body = response.content.decode("utf-8")

    assert (
        "python_gc_objects_collected_total" in body
        or "python_info" in body
    )
