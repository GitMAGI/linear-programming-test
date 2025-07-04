from pulp import * 

def main():
    print("Started")

    data = [
        {
            'period': 1,
            'OFFID': ['a'],
            'OFFList': [15],
            'OFFPrices': [100],
            'OFFZones': [1],
            'BIDID': ['e1'],
            'BIDList': [15],
            'BIDPrices': [110],
            'BIDZones': [1],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 2,
            'OFFID': ['b'],
            'OFFList': [15],
            'OFFPrices': [120],
            'OFFZones': [1],
            'BIDID': ['e2'],
            'BIDList': [15],
            'BIDPrices': [110],
            'BIDZones': [1],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },{
            'period': 3,
            'OFFID': ['c'],
            'OFFList': [15],
            'OFFPrices': [100],
            'OFFZones': [1],
            'BIDID': ['e3'],
            'BIDList': [15],
            'BIDPrices': [110],
            'BIDZones': [1],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 4,
            'OFFID': ['d'],
            'OFFList': [15],
            'OFFPrices': [120],
            'OFFZones': [1],
            'BIDID': ['e4'],
            'BIDList': [15],
            'BIDPrices': [110],
            'BIDZones': [1],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 5,
            'OFFID': ['f'],
            'OFFList': [18],
            'OFFPrices': [90],
            'OFFZones': [2],
            'BIDID': ['j1'],
            'BIDList': [18],
            'BIDPrices': [100],
            'BIDZones': [2],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },
        {
            'period': 6,
            'OFFID': ['g'],
            'OFFList': [18],
            'OFFPrices': [95],
            'OFFZones': [2],
            'BIDID': ['j2'],
            'BIDList': [18],
            'BIDPrices': [100],
            'BIDZones': [2],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },{
            'period': 7,
            'OFFID': ['h'],
            'OFFList': [18],
            'OFFPrices': [90],
            'OFFZones': [2],
            'BIDID': ['j3'],
            'BIDList': [18],
            'BIDPrices': [100],
            'BIDZones': [2],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },
        {
            'period': 8,
            'OFFID': ['i'],
            'OFFList': [18],
            'OFFPrices': [95],
            'OFFZones': [2],
            'BIDID': ['j4'],
            'BIDList': [18],
            'BIDPrices': [100],
            'BIDZones': [2],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        }
    ]

    prob = LpProblem("Euphemia_problem", LpMaximize)
    sub_probs = []
    for datum in data:
        p = datum['period'] 

        off_ids = datum['OFFID']
        off_lists = datum['OFFList']
        off_prices = datum['OFFPrices']
        off_zones = datum['OFFZones']
        bid_ids = datum['BIDID']
        bid_lists = datum['BIDList']
        bid_prices = datum['BIDPrices']
        bid_zones = datum['BIDZones']
        zone_ids = datum['Zones']

        bv = [ LpVariable (
            f"bid_{bid_ids[j]}_{p}",
            lowBound=0,
            upBound=bid_lists[j],
            cat='Continuous'
            ) for j in range(0, len(bid_lists)) ]
        ov = [ LpVariable (
            f"off_{off_ids[j]}_{p}",
            lowBound=0,
            upBound=off_lists[j],
            cat='Continuous'
            ) for j in range(0, len(off_lists)) ]

        # Sub Objective: Welfare for current period
        #sub_probs.append(
        #    lpSum([bv[j]*bid_prices[j] for j in range(0, len(bid_lists))]) - lpSum([ov[j]*off_prices[j] for j in range(0, len(off_lists))])
        #)

        sub_probs.append(
            lpSum(lpDot(bv, bid_prices) - lpDot(ov, off_prices))
        )

        prob += lpSum(bv) - lpSum(ov) == 0, f"balance_bids_offs_{p}"            # Constarint 1
        for z in zone_ids:
            prob += lpSum([
                v for i,v in enumerate(bv) if bid_zones[i] == z
            ]) - lpSum([
                v for i,v in enumerate(ov) if off_zones[i] == z
            ]) == 0, f"zone_balance_{z}_{p}"                                    # Constraint 2
        
    # Objective function to maximize
    prob += lpSum(sub_probs), f'maximize_daily_social_wellnes_for_{len(data)}_periods'

    status = prob.solve(PULP_CBC_CMD(msg=True))

    bv_results = []
    ov_results = []
    balance_zone_prices_results = []
    zone_prices_results = []
    for datum in data:
        p = datum['period']
        bv_result = {re.search(f'^bid_(\w+)_{p}$', v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                    if re.match(f'^bid_(\w+)_{p}$', v.name, re.IGNORECASE)}
        bv_results.append(bv_result)
        ov_result = {re.search(f'^off_(\w+)_{p}$', v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                    if re.match(f'^off_(\w+)_{p}$', v.name, re.IGNORECASE)}
        ov_results.append(ov_result)

        # Balance Bids/Offs in dual mode (price?)        
        balance_main = next(c.pi for name, c in prob.constraints.items() if name == f"balance_bids_offs_{p}")
        # Balance Zone in dual mode (shadow proces)
        zone_blanace_contraint_regex = re.compile(f'^zone_balance_(\w+)_{p}$')
        balance_zone_prices_result = { 
            int(re.search(zone_blanace_contraint_regex, name).group(1)) : balance_main - round(c.pi,2) 
            for name, c in prob.constraints.items() if zone_blanace_contraint_regex.match(name)
        }
        zone_prices_result = {
            int(re.search(zone_blanace_contraint_regex, name).group(1)) : round(c.pi,2) 
            for name, c in prob.constraints.items() if zone_blanace_contraint_regex.match(name)
        }
        balance_zone_prices_results.append(balance_zone_prices_result)
        zone_prices_results.append(zone_prices_result)

    print(f"bids: {bv_results}")
    print(f"offs: {ov_results}")
    print(f"zone_prices_results: {zone_prices_results}")

    print("Completed")
    return 1

if __name__ == '__main__':
    main()