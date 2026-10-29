
import pytest
from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency,
)


def test_validation_type_and_fee_conditions():
    with pytest.raises(ValueError):
        process_storage_tenants(None, 0)

    with pytest.raises(ValueError):
        process_storage_tenants([], -1)

    with pytest.raises(ValueError):
        process_storage_tenants("invalid", -1)


def test_empty_list_and_zero_usage():
    assert process_storage_tenants([], 0) == {
        "total_billed": 0.0, "status": "ZERO_USAGE"
    }


def test_missing_optional_fields():
    result = process_storage_tenants([{"account_active": True}], 0)
    assert result["status"] == "ZERO_USAGE"


def test_inactive_and_active_tenants():
    tenants = [
        {"account_active": False, "tier": "hot",
         "buckets": [{"size_gb": 100}]},
        {"account_active": True, "tier": "hot",
         "buckets": [{"size_gb": 100}]},
    ]
    assert process_storage_tenants(tenants, 0)["total_billed"] == 2.5


@pytest.mark.parametrize("tier,expected", [
    ("hot", 2.5),
    ("cool", 1.5),
    ("archive", 0.5),
])
def test_each_tier(tier, expected):
    result = process_storage_tenants([{
        "account_active": True,
        "tier": tier,
        "buckets": [{"size_gb": 100}],
    }], 0)
    assert result["total_billed"] == expected


def test_unknown_tier():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "unknown",
        "buckets": [{"size_gb": 100}],
    }], 0)
    assert result["total_billed"] == 0.0


def test_bucket_size_boundary():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": -1},
            {"size_gb": 500},
            {"size_gb": 501},
        ],
    }], 0)
    assert result["total_billed"] == 23.77
    assert result["status"] == "ZERO_USAGE" if result["total_billed"] == 0 else "BILLED"


def test_egress_boundary():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 100, "egress_gb": 100},
            {"size_gb": 100, "egress_gb": 150},
        ],
    }]
    assert process_storage_tenants(tenants, 0)["total_billed"] == 9.0


def test_corrupted_non_archive_and_archive():
    tenants = [
        {"account_active": True, "tier": "hot",
         "buckets": [{"size_gb": 100, "corrupted": True}]},
        {"account_active": True, "tier": "archive",
         "buckets": [{"size_gb": 100, "corrupted": True},
                     {"size_gb": 100}]},
    ]
    assert process_storage_tenants(tenants, 0)["total_billed"] == 0.0


def test_backup_fee_with_zero_usage():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [],
    }], 10)
    assert result == {"total_billed": 10.0, "status": "BILLED"}


def test_audit_flag_and_billed_status():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0} for _ in range(5)],
    }]
    assert process_storage_tenants(tenants, 0)["status"] == "AUDIT_FLAGGED"

    tenants[0]["buckets"] = [{"size_gb": 100}]
    assert process_storage_tenants(tenants, 0)["status"] == "BILLED"


def test_latency_empty_matrix():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_latency_empty_node_and_reset():
    assert monitor_replication_latency([[], [250, 100, 250]]) == "SYNCED"


def test_latency_threshold():
    assert monitor_replication_latency([[200, 200]]) == "SYNCED"
    assert monitor_replication_latency([[201, 201]]) == "SYNC_LAG_ALERT"


def test_latency_streak_resets_between_nodes():
    assert monitor_replication_latency([[250], [250]]) == "SYNCED"
    assert monitor_replication_latency([[250, 200, 250]]) == "SYNCED"
