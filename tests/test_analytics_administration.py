import pytest

from edith_hermes.analytics_administration import AsyncUsageAdministration


@pytest.mark.asyncio
async def test_native_analytics_keep_measurement_metadata_and_concrete_profile():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            return dict(totals={'total_actual_cost': 0, 'total_estimated_cost': 1}, measuredCostSamples=0, cacheWriteTokens=None, throughputTokensPerSecond=None)

    api = AsyncUsageAdministration(Transport(), profile='family')
    result = await api.usage(7)
    assert result['measuredCostSamples'] == 0 and result['throughputTokensPerSecond'] is None
    assert calls[0] == ('edith.desktop.v1.analytics.usage', {'profile': 'family', 'days': 7})
    with pytest.raises(ValueError):
        await api.usage(366)
    with pytest.raises(ValueError):
        AsyncUsageAdministration(Transport(), profile='all')
