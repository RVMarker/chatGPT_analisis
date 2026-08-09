"""V12.88 end-to-end multi-asset investment pipeline with operational trade plan."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from investment_analyzer.providers.asset_classifier import AssetClassifier
from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry
from investment_analyzer.providers.provider_consensus import ProviderConsensus
from investment_analyzer.providers.data_router import DataAcquisitionRouter
from investment_analyzer.providers.acquisition_engine import MultiProviderAcquisitionEngine
from investment_analyzer.analysis.etf_analyzer import ETFAnalyzer
from investment_analyzer.analysis.etf_scoring import ETFDecisionScorer
from investment_analyzer.analysis.decision_integration import SpecializedDecisionIntegrator
from investment_analyzer.analysis.reit_fibra_integration import REITFibraAnalyzer
from investment_analyzer.analysis.crypto_analyzer import CryptoAnalyzer
from investment_analyzer.analysis.crypto_valuation import CryptoValuation
from investment_analyzer.analysis.bond_analyzer import BondAnalyzer
from investment_analyzer.analysis.bond_valuation import BondValuation
from investment_analyzer.analysis.risk_trade_plan import RiskTradePlan
from investment_analyzer.analysis.position_sizing import PositionSizer
from investment_analyzer.analysis.decision_quality_gate import DecisionQualityGate

@dataclass(slots=True)
class PipelineResult:
    identity:dict[str,Any]; classification:dict[str,Any]; route:dict[str,Any]; acquisition:dict[str,Any]; specialized_analysis:dict[str,Any]; consensus:dict[str,dict[str,Any]]; analysis:dict[str,Any]; decision:dict[str,Any]; quality:dict[str,Any]; warnings:list[str]; position_sizing:dict[str,Any]|None=None
    def as_dict(self): return asdict(self)

class InvestmentPipeline:
    def __init__(self,classifier=None,identity_registry=None,consensus=None,data_router=None,acquisition=None,etf_analyzer=None,etf_scorer=None,decision_integrator=None,reit_fibra_analyzer=None,crypto_analyzer=None,crypto_valuation=None,bond_analyzer=None,bond_valuation=None,risk_trade_plan=None,position_sizer=None,decision_quality_gate=None):
        self.classifier=classifier or AssetClassifier(); self.identity=identity_registry or InstrumentIdentityRegistry(); self.consensus=consensus or ProviderConsensus(); self.router=data_router or DataAcquisitionRouter(); self.acquisition=acquisition or MultiProviderAcquisitionEngine(self.router,identity_registry=self.identity); self.etf_analyzer=etf_analyzer or ETFAnalyzer(); self.etf_scorer=etf_scorer or ETFDecisionScorer(); self.decision_integrator=decision_integrator or SpecializedDecisionIntegrator(); self.reit_fibra_analyzer=reit_fibra_analyzer or REITFibraAnalyzer(); self.crypto_analyzer=crypto_analyzer or CryptoAnalyzer(); self.crypto_valuation=crypto_valuation or CryptoValuation(); self.bond_analyzer=bond_analyzer or BondAnalyzer(); self.bond_valuation=bond_valuation or BondValuation(); self.risk_trade_plan=risk_trade_plan or RiskTradePlan(); self.position_sizer=position_sizer or PositionSizer(); self.decision_quality_gate=decision_quality_gate or DecisionQualityGate()
    @staticmethod
    def _decision(score,coverage,confidence):
        if coverage<60 or confidence<50:return "MANTENER"
        if score>=80:return "COMPRAR"
        if score>=65:return "ACUMULAR"
        if score>=45:return "MANTENER"
        if score>=30:return "REDUCIR"
        return "VENDER"
    @staticmethod
    def _enriched(acquisition): return acquisition.enriched or {}
    @staticmethod
    def _first_value(acquisition, enriched, *keys):
        for key in keys:
            value=enriched.get(key)
            if isinstance(value,(int,float)) and value>0:return float(value)
            rows=acquisition.fields.get(key) or []
            for row in rows:
                value=row.get("value") if isinstance(row,dict) else None
                if isinstance(value,(int,float)) and value>0:return float(value)
        return None
    def run(self,*,symbol,asset_type=None,isin=None,country=None,exchange=None,currency=None,provider_symbols=None,aliases=(),provider_metadata=None,consensus_data=None,analysis=None,strategic_score=None,strategic_coverage=0,tactical_score=None,tactical_coverage=0,data_quality=100.0,fetchers=None,capital=5000.0,risk_pct=0.02,max_position_pct=0.25,lot_size=1):
        md=provider_metadata or {}; classification=self.classifier.classify(symbol,provider_asset_type=asset_type,quote_type=md.get("quote_type"),description=md.get("description"),metadata=md); final_asset=classification.asset_type if asset_type is None else self.identity.normalize_asset_type(asset_type); route=self.router.plan(final_asset,symbol); ident=self.identity.register(asset_type=final_asset,symbol=symbol,isin=isin,country=country,exchange=exchange,currency=currency,provider_symbols=provider_symbols,aliases=aliases,metadata=md); acquisition=self.acquisition.acquire(symbol=symbol,asset_type=final_asset,fetchers=fetchers or {},identity=ident); specialized={}; specialized_warnings=[]; enriched=self._enriched(acquisition)
        if final_asset=="ETF":
            canonical={k:enriched.get(k) for k in ("price","expense_ratio","benchmark","aum","holdings","tracking_difference","tracking_error","trackingDifference","trackingError","category_median_expense_ratio","yield","distribution_yield")}; canonical["price"]=canonical.get("price") or self._first_value(acquisition,enriched,"price"); etf=self.etf_analyzer.analyze(symbol,canonical); etf_dict=etf.as_dict(); score=self.etf_scorer.score(etf_dict,data_quality); etf_dict.update({"score":score.score,"score_components":score.components,"score_coverage":score.coverage,"score_warnings":score.warnings}); specialized={"etf":etf_dict}; specialized_warnings=(etf.warnings or [])+(score.warnings or [])
        elif final_asset in {"REIT","FIBRA"}:
            specialized={"reit_fibra":self.reit_fibra_analyzer.analyze(symbol,enriched)}; specialized_warnings=(enriched.get("warnings") or [])+(specialized["reit_fibra"].get("warnings") or [])
        elif final_asset=="CRYPTO":
            crypto=self.crypto_analyzer.analyze(symbol,enriched); specialized={"crypto":crypto}; valuation_input=dict(crypto); valuation_input.update({"momentum_score":enriched.get("momentum_score"),"drawdown_score":enriched.get("drawdown_score"),"relative_valuation_score":enriched.get("relative_valuation_score")}); specialized["crypto_decision"]=self.crypto_valuation.analyze(valuation_input); specialized_warnings=crypto.get("warnings",[])
        elif final_asset=="BOND":
            bond=self.bond_analyzer.analyze(symbol,enriched); specialized={"bond":bond}; valuation_input=dict(bond); valuation_input.update({"credit_score":enriched.get("credit_score"),"liquidity_score":enriched.get("liquidity_score")}); specialized["bond_decision"]=self.bond_valuation.analyze(valuation_input); specialized_warnings=bond.get("warnings",[])
        consensus_input=consensus_data or {}
        if not consensus_input: consensus_input={field:[(x["provider"],x["value"]) for x in values] for field,values in acquisition.fields.items()}
        consensus=self.consensus.evaluate_batch(consensus_input,critical_fields=route["required_fields"]); blocked=[f for f,r in consensus.items() if not r.vote_allowed]; missing=acquisition.missing_required; cq=sum(r.quality_score for r in consensus.values())/len(consensus) if consensus else 0.0; completeness=100.0*(1-len(missing)/len(route["required_fields"])) if route["required_fields"] else 100.0; quality=min(float(data_quality),cq,completeness) if consensus else min(float(data_quality),completeness); warnings=[]
        if classification.confidence<70:warnings.append("Clasificación de activo con confianza inferior a 70%")
        if blocked:warnings.append("Datos críticos bloqueados por falta de consenso: "+", ".join(blocked))
        if missing:warnings.append("Datos requeridos ausentes: "+", ".join(missing))
        warnings.extend(specialized_warnings); strategic_conf=quality*(float(strategic_coverage)/100); tactical_conf=quality*(float(tactical_coverage)/100); decision={"strategic":{"score":strategic_score,"coverage":strategic_coverage,"confidence":round(strategic_conf,2),"verdict":self._decision(float(strategic_score if strategic_score is not None else 50),float(strategic_coverage),strategic_conf)},"tactical":{"score":tactical_score,"coverage":tactical_coverage,"confidence":round(tactical_conf,2),"verdict":self._decision(float(tactical_score if tactical_score is not None else 50),float(tactical_coverage),tactical_conf)}}
        if final_asset=="ETF" and "etf" in specialized: decision["strategic"]=self.decision_integrator.integrate(asset_type="ETF",strategic=decision["strategic"],specialized=specialized)
        elif final_asset in {"REIT","FIBRA"} and "reit_fibra" in specialized:
            rf=specialized["reit_fibra"]; decision["strategic"].update({"generic_score":decision["strategic"].get("score"),"score":rf["score"],"coverage":rf["coverage"],"specialized_component":"REIT_FIBRA","specialized_score":rf["score"],"specialized_coverage":rf["coverage"],"decision_basis":"REIT/FIBRA FFO-AFFO-NAV valuation"}); decision["strategic"]["verdict"]=self._decision(float(rf["score"]),float(rf["coverage"]),float(quality)*float(rf["coverage"])/100); decision["strategic"]["confidence"]=round(float(quality)*float(rf["coverage"])/100,2)
        elif final_asset=="CRYPTO" and "crypto_decision" in specialized:
            cd=specialized["crypto_decision"]; decision["strategic"].update({"score":cd.get("strategic_score"),"coverage":cd.get("coverage",0),"verdict":cd.get("strategic_verdict") or "MANTENER","specialized_component":"CRYPTO","decision_basis":"Crypto liquidity/risk/relative valuation"}); decision["tactical"].update({"score":cd.get("tactical_score"),"coverage":cd.get("coverage",0),"verdict":cd.get("tactical_verdict") or "MANTENER","specialized_component":"CRYPTO","decision_basis":"Crypto momentum/liquidity"})
        elif final_asset=="BOND" and "bond_decision" in specialized:
            bd=specialized["bond_decision"]; decision["strategic"].update({"score":bd.get("relative_value_score"),"coverage":bd.get("coverage",0),"verdict":bd.get("strategic_verdict") or "MANTENER","specialized_component":"BOND","decision_basis":"Bond yield/price/duration/credit/liquidity"})
        price=self._first_value(acquisition,enriched,"price","current_price","last_price")
        fair_value=self._first_value(acquisition,enriched,"fair_value_per_share","fair_value","intrinsic_value","target_price")
        support=self._first_value(acquisition,enriched,"technical_support","support","support_1")
        resistance=self._first_value(acquisition,enriched,"technical_resistance","resistance","resistance_1")
        atr=self._first_value(acquisition,enriched,"atr","ATR")
        if fair_value is None:
            for source in (specialized.get("reit_fibra"),specialized.get("crypto_decision"),specialized.get("bond_decision"),specialized.get("etf")):
                if isinstance(source,dict): fair_value=self._first_value(type("A",(),{"fields":{}})(),source,"fair_value_per_share","fair_value","intrinsic_value","target_price") or fair_value
        trade=self.risk_trade_plan.build(price=price,fair_value=fair_value,technical_support=support,technical_resistance=resistance,atr=atr)
        sizing=self.position_sizer.calculate(capital=float(capital),entry=float(price) if price else 0,stop_loss=float(trade.get("stop_loss")) if trade.get("stop_loss") else 0,risk_pct=float(risk_pct),max_position_pct=float(max_position_pct),lot_size=int(lot_size)) if price and trade.get("stop_loss") else {"status":"INSUFFICIENT_DATA","units":0,"risk_budget":float(capital)*float(risk_pct)}
        strategic=decision["strategic"]; tactical=decision["tactical"]; mos=(fair_value/price-1.0) if price and fair_value else None
        gate=self.decision_quality_gate.evaluate(strategic_verdict=strategic.get("verdict"),tactical_verdict=tactical.get("verdict"),score=strategic.get("score"),fair_value=fair_value,price=price,risk_reward=trade.get("risk_reward"),margin_of_safety=mos,data_coverage=quality)
        decision["trade_plan"]=trade; decision["position_sizing"]=sizing; decision["quality_gate"]=gate; decision["operational_verdict"]=gate.get("operation"); decision["entry_price"]=price; decision["fair_value"]=fair_value; decision["stop_loss"]=trade.get("stop_loss"); decision["target_1"]=trade.get("target_1"); decision["target_2"]=trade.get("target_2"); decision["risk_reward"]=trade.get("risk_reward")
        return PipelineResult(ident.as_dict(),classification.as_dict(),route,acquisition.as_dict(),specialized,{k:r.as_dict() for k,r in consensus.items()},analysis or {},decision,{"data_quality":round(quality,2),"consensus_quality":round(cq,2),"completeness":round(completeness,2),"blocked_fields":blocked,"missing_required":missing},warnings,sizing)
