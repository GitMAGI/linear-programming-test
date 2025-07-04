from pulp import * 

def main():
    print("Started")

    prices = [.56, .58, .23, 1.6, 1.2, .67]
    c0 = 0          # initialCharge 
    cm = 32         # fullCharge
    cr  = 4         # chargeRate

    variables = [LpVariable(name=f"x_{i}", cat=LpInteger, lowBound=-1, upBound=1) for i in range(len(prices))]
    model = LpProblem("BestBuySellPrice", LpMinimize)
    model += lpSum(variables) <= int(cm/cr) - int(c0/cr)        # Constarint 1
    model += lpSum(variables) >= -int(c0/cr)                    # Constraint 2
    model += lpDot(prices, variables)                           # Objective function to mimiiza
    
    status = model.solve(PULP_CBC_CMD(msg=True))
    print("price", model.objective.value())
    print("take", *[variables[i].value() for i in range(len(prices))])

    print("Completed")
    return 1

if __name__ == '__main__':
    main()