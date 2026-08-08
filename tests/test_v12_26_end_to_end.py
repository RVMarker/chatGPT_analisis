from investment_analyzer.pipeline.end_to_end import InvestmentPipeline

def test_end_to_end_fibra_pipeline_and_consensus_gate():
    p=InvestmentPipeline().run(symbol="FMTY14.MX",asset_type="FIBRA",isin="MXCFFM010001",country="MX",provider_symbols={"yahoo":"FMTY14.MX","provider_x":"FMTY14"},consensus_data={"ffo":[("yahoo",.45),("provider_x",.46)],"price":[("yahoo",14.29),("provider_x",14.31)]},strategic_score=72,strategic_coverage=100,tactical_score=51,tactical_coverage=100,data_quality=95)
    assert p.identity["canonical_id"]=="FIBRA:ISIN:MXCFFM010001"
    assert p.classification["asset_type"]=="FIBRA"
    assert p.quality["blocked_fields"]==[]
    assert p.decision["strategic"]["verdict"]=="ACUMULAR"

def test_conflict_reduces_confidence_and_blocks_field():
    p=InvestmentPipeline().run(symbol="FMTY14.MX",asset_type="FIBRA",consensus_data={"ffo":[("yahoo",.45),("provider_x",.70)]},strategic_score=80,strategic_coverage=100,tactical_score=80,tactical_coverage=100,data_quality=95)
    assert "ffo" in p.quality["blocked_fields"]
    assert p.decision["strategic"]["confidence"]<50
    assert p.decision["strategic"]["verdict"]=="MANTENER"
