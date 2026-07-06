from fastapi import APIRouter
from pydantic import BaseModel
from services.calculator_service import calculate_sip, calculate_emi

router = APIRouter()

class SIPInput(BaseModel):
    principal: float
    rate: float
    time_years: float
    frequency: int = 12

class EMIInput(BaseModel):
    principal: float
    rate: float
    months: int

@router.post("/sip")
async def sip_calculator(data: SIPInput):
    result = calculate_sip(data.principal, data.rate, data.time_years, data.frequency)
    return {"future_value": result}

@router.post("/emi")
async def emi_calculator(data: EMIInput):
    result = calculate_emi(data.principal, data.rate, data.months)
    return {"emi": result}
