from investment_analyzer.providers.provider_consensus import ProviderConsensus

def test_consensus_allows_small_difference():
    r=ProviderConsensus().evaluate("price",[("yahoo",100),("provider_b",101)],critical=True)
    assert r.vote_allowed is True
    assert r.status == "CONSENSUS"
    assert r.accepted_value is not None

def test_conflict_blocks_critical_value():
    r=ProviderConsensus().evaluate("ffo",[("yahoo",.45),("provider_b",.60)],critical=True)
    assert r.vote_allowed is False
    assert r.status == "CONFLICT"
    assert r.accepted_value is None

def test_single_provider_blocks_critical_but_can_pass_context():
    engine=ProviderConsensus()
    critical=engine.evaluate("market_cap",[("yahoo",1_000)],critical=True)
    context=engine.evaluate("market_cap",[("yahoo",1_000)],critical=False)
    assert critical.vote_allowed is False
    assert context.vote_allowed is True
