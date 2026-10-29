
import pytest
from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency,
)


def test_active_hot_tenant():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 50}],
    }]
    assert process_storage_tenants(tenants, 10)["total_billed"] == 2.5


def test_all_storage_tiers():
    tenants = [
        {"account_active": True, "tier": "hot",
         "buckets": [{"size_gb": 100}]},
        {"account_active": True, "tier": "cool",
         "buckets": [{"size_gb": 100}]},
        {"account_active": True, "tier": "archive",
         "buckets": [{"size_gb": 100}]},
    ]
    result = process_storage_tenants(tenants, 0)
    assert result["total_billed"] == 4.5
    assert result["status"] == "BILLED"


def test_large_bucket_and_egress_charge():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 600, "egress_gb": 150}],
    }]
    # 600 * 0.025 * 0.90 + (150 - 100) * 0.08
    assert process_storage_tenants(tenants, 0)["total_billed"] == 17.5


def test_backup_vault_fee():
    tenants = [{
        "account_active": True,
        "tier": "cool",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100}],
    }]
    assert process_storage_tenants(tenants, 10)["total_billed"] == 11.5


def test_inactive_tenant_is_skipped():
    tenants = [{
        "account_active": False,
        "tier": "hot",
        "buckets": [{"size_gb": 100}],
    }]
    result = process_storage_tenants(tenants, 0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_invalid_tenant_list():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 0)


def test_negative_support_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -1)


def test_unknown_tier_is_flagged():
    tenants = [{
        "account_active": True,
        "tier": "unknown",
        "buckets": [],
    }]
    result = process_storage_tenants(tenants, 0)
    assert result["status"] == "ZERO_USAGE"


def test_invalid_bucket_size():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0}],
    }]
    result = process_storage_tenants(tenants, 0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_archive_bucket():
    tenants = [{
        "account_active": True,
        "tier": "archive",
        "buckets": [{"size_gb": 100, "corrupted": True}],
    }]
    assert process_storage_tenants(tenants, 0)["total_billed"] == 0.0


def test_audit_flagged():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
        ],
    }]
    assert process_storage_tenants(tenants, 0)["status"] == "AUDIT_FLAGGED"


def test_replication_latency_no_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_replication_latency_synced():
    assert monitor_replication_latency([[50, 100, 200], [30]]) == "SYNCED"


def test_replication_latency_alert():
    assert monitor_replication_latency([[250, 300]]) == "SYNC_LAG_ALERT"
