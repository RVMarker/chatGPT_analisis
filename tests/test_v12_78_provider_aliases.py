"""V12.79 provider-specific symbol regression tests."""
from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry
from investment_analyzer.providers.acquisition_engine import MultiProviderAcquisitionEngine


def test_mexican_provider_aliases():
    registry=InstrumentIdentityRegistry()
    item=registry.register(asset_type='FIBRA',symbol='FMTY14.MX',country='MX')
    assert registry.provider_symbol(item,'yahoo')=='FMTY14.MX'
    assert registry.provider_symbol(item,'fmp')=='FMTY14'
    assert registry.provider_symbol(item,'twelvedata')=='FMTY14'


def test_acquisition_uses_provider_aliases():
    registry=InstrumentIdentityRegistry()
    item=registry.register(asset_type='FIBRA',symbol='FMTY14.MX',country='MX')
    calls=[]
    def fetch(symbol):
        calls.append(symbol)
        return {}
    engine=MultiProviderAcquisitionEngine(identity_registry=registry)
    engine.router.route=lambda asset: type('R',(),{'required_fields':[],'optional_fields':[],'providers':['yahoo','fmp'] ,'asset_type':asset,'as_dict':lambda self:{}})()
    engine.acquire(symbol='FMTY14.MX',asset_type='FIBRA',fetchers={'yahoo':fetch,'fmp':fetch},identity=item)
    assert calls==['FMTY14.MX','FMTY14']
