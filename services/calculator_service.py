# SIP Calculator
def calculate_sip(principal, rate, time_years, frequency=12):
    r = rate / 100 / frequency
    n = time_years * frequency
    amount = principal * (((1 + r) ** n - 1) / r) * (1 + r)
    return round(amount, 2)

# EMI Calculator
def calculate_emi(principal, rate, months):
    r = rate / 12 / 100
    emi = principal * r * ((1 + r) ** months) / (((1 + r) ** months) - 1)
    return round(emi, 2)
