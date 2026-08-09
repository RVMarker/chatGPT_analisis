"""V12.53 unified dispatcher for STOCK, ETF, REIT, FIBRA, CRYPTO and BOND."""
from __future__ import annotations
from typing import Any
from investment_analyzer.analysis.stock_integration import StockAnalyzer
from investment_analyzer.analysis.crypto_integration import CryptoAnalyzer
from investment_analyzer.analysis.bond_integration import BondAnalyzer
from investment_analyzer.analysis.reit_fibra_integration import REITFibraAnalyzer

class SpecializedDispatcher:
    def __init__(self, *, stock=None, etf=None, reit_fibra=None, crypto=None, bond=None):
        self.stock=stock or StockAnalyzer(); self.etf=etf
        self.reit_fibra=reit_fibra or REITFibraAnalyzer(); self.crypto=crypto or CryptoAnalyzer(); self.bond=bond or BondAnalyzer()
    @staticmethod
    def normalize(asset_type:str)->str:
        a=str(asset_type or '').upper().strip().replace('-','_').replace('/','_')
        aliases={'STOCK':'STOCK','EQUITY':'STOCK','SHARE':'STOCK','ETF':'ETF','REIT':'REIT','FIBRA':'FIBRA','REIT_FIBRA':'REIT_FIBRA','CRYPTO':'CRYPTO','CRYPTOCURRENCY':'CRYPTO','TOKEN':'CRYPTO','BOND':'BOND','BONO':'BOND','FIXED_INCOME':'BOND'}
        return aliases.get(a,a)
    def analyze(self,asset_type:str,symbol:str,payload:dict[str,Any]|None=None)->dict[str,Any]:
        a=self.normalize(asset_type); p=payload or {}
        if a=='STOCK': return {'asset_type':a,'analysis':self.stock.analyze(symbol,p)}
        if a in ('REIT','FIBRA','REIT_FIBRA'): return {'asset_type':a,'analysis':self.reit_fibra.analyze(symbol,p)}
        if a=='CRYPTO': return {'asset_type':a,'analysis':self.crypto.analyze(symbol,p)}
        if a=='BOND': return {'asset_type':a,'analysis':self.bond.analyze(symbol,p)}
        if a=='ETF':
            if self.etf is None: return {'asset_type':a,'analysis':{},'warnings':['ETF analyzer no conectado al dispatcher']}
            return {'asset_type':a,'analysis':self.etf.analyze(symbol,p)}
        return {'asset_type':a,'analysis':{},'warnings':[f'Tipo de activo no soportado: {asset_type}']}
