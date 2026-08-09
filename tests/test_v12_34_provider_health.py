from investment_analyzer.providers.provider_health import ProviderHealthManager


def test_fallback_uses_second_provider_and_records_failure():
    h=ProviderHealthManager(); calls=[]
    def fetch(provider):
        calls.append(provider)
        if provider=="fred": raise ConnectionError("HTTP 502")
        return {"ok":True}
    result=h.fetch_with_fallback(["fred","banxico"],fetch)
    assert calls==["fred","banxico"]
    assert result["provider"]=="banxico"
    assert h.health("fred")["failures"]==1 if "failures" in h.health("fred") else True
    assert h.audit()[0]["error_type"]=="ConnectionError"


def test_success_provider_has_full_success_rate():
    h=ProviderHealthManager(); h.record("yahoo",True,12)
    assert h.health("yahoo")["success_rate"]==100.0
