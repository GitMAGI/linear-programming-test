from pulp import * 

def normalize_data_dict(data_dict):
    new_data = [] 
    for pt, data_pt in data_dict.items():
        mtu = int(pt.lower().replace("pt", ""))
        mtu_mult_factor = int(mtu/15)
        for datum in data_pt:
            p_start = (datum['period']-1)*mtu_mult_factor+1
            p_end = p_start+mtu_mult_factor
            i = 1
            for period in range(p_start, p_end):
                is_already_here = False
                if len(new_data) > 0:
                    for d_ in new_data:
                        if d_['period'] == period:
                            new_datum = d_
                            is_already_here = True
                            break
                        else:
                            new_datum = {'period': period}       
                else:
                    new_datum = {'period': period}

                if not 'OFFID' in new_datum.keys():
                    new_datum['OFFID'] = [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['OFFID']]
                    new_datum['OFFList'] = datum['OFFList']
                    new_datum['OFFPrices'] = datum['OFFPrices']
                    new_datum['OFFZones'] = datum['OFFZones']
                else:
                    new_datum['OFFID'] += [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['OFFID']]
                    new_datum['OFFList'] += datum['OFFList']
                    new_datum['OFFPrices'] += datum['OFFPrices']
                    new_datum['OFFZones'] += datum['OFFZones']

                if not 'BIDID' in new_datum.keys():
                    new_datum['BIDID'] = [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['BIDID']]
                    new_datum['BIDList'] = datum['BIDList']
                    new_datum['BIDPrices'] = datum['BIDPrices']
                    new_datum['BIDZones'] = datum['BIDZones']
                else:
                    new_datum['BIDID'] += [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['BIDID']]
                    new_datum['BIDList'] += datum['BIDList']
                    new_datum['BIDPrices'] += datum['BIDPrices']
                    new_datum['BIDZones'] += datum['BIDZones']

                if not 'Zones' in new_datum.keys():
                    new_datum['Zones'] = datum['Zones']
                    new_datum['ZoneNames'] = datum['ZoneNames']
                else:
                    #new_datum['Zones'] += datum['Zones']
                    new_datum['Zones'] = list(set(new_datum['Zones']+datum['Zones']))
                    #new_datum['ZoneNames'] += datum['ZoneNames']
                    new_datum['ZoneNames'] = list(set(new_datum['ZoneNames']+datum['ZoneNames']))

                if not is_already_here:
                    new_data.append(new_datum)
                i += 1
    return new_data

def main():
    print("Started")

    data_pt15 = [
        {
            'period': 1,
            'OFFID': ['a'],
            'OFFList': [15],
            'OFFPrices': [100],
            'OFFZones': [1],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 2,
            'OFFID': ['b'],
            'OFFList': [15],
            'OFFPrices': [120],
            'OFFZones': [1],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },{
            'period': 3,
            'OFFID': ['c'],
            'OFFList': [15],
            'OFFPrices': [100],
            'OFFZones': [1],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 4,
            'OFFID': ['d'],
            'OFFList': [15],
            'OFFPrices': [120],
            'OFFZones': [1],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 5,
            'OFFID': ['f'],
            'OFFList': [18],
            'OFFPrices': [90],
            'OFFZones': [2],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },
        {
            'period': 6,
            'OFFID': ['g'],
            'OFFList': [18],
            'OFFPrices': [95],
            'OFFZones': [2],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },{
            'period': 7,
            'OFFID': ['h'],
            'OFFList': [18],
            'OFFPrices': [90],
            'OFFZones': [2],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },
        {
            'period': 8,
            'OFFID': ['i'],
            'OFFList': [18],
            'OFFPrices': [95],
            'OFFZones': [2],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        },
        {
            'period': 9,
            'OFFID': ['k'],
            'OFFList': [7],
            'OFFPrices': [46],
            'OFFZones': [3],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        },
        {
            'period': 10,
            'OFFID': ['l'],
            'OFFList': [7],
            'OFFPrices': [50],
            'OFFZones': [3],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        },{
            'period': 11,
            'OFFID': ['m'],
            'OFFList': [11],
            'OFFPrices': [56],
            'OFFZones': [3],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        },
        {
            'period': 12,
            'OFFID': ['n'],
            'OFFList': [11],
            'OFFPrices': [54],
            'OFFZones': [3],
            'BIDID': [],
            'BIDList': [],
            'BIDPrices': [],
            'BIDZones': [],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        }
    ]
    data_pt30 = [
        {
            'period': 5,
            'OFFID': [],
            'OFFList': [],
            'OFFPrices': [],
            'OFFZones': [],
            'BIDID': ['o'],
            'BIDList': [7],
            'BIDPrices': [48],
            'BIDZones': [3],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        },
        {
            'period': 6,
            'OFFID': [],
            'OFFList': [],
            'OFFPrices': [],
            'OFFZones': [],
            'BIDID': ['p'],
            'BIDList': [11],
            'BIDPrices': [57],
            'BIDZones': [3],
            'Zones': [3],
            'ZoneNames': ['ZON3']
        },
    ]
    data_pt60 = [
        {
            'period': 1,
            'OFFID': [],
            'OFFList': [],
            'OFFPrices': [],
            'OFFZones': [],
            'BIDID': ['e'],
            'BIDList': [15],
            'BIDPrices': [110],
            'BIDZones': [1],
            'Zones': [1],
            'ZoneNames': ['ZON1']
        },
        {
            'period': 2,
            'OFFID': [],
            'OFFList': [],
            'OFFPrices': [],
            'OFFZones': [],
            'BIDID': ['j'],
            'BIDList': [18],
            'BIDPrices': [100],
            'BIDZones': [2],
            'Zones': [2],
            'ZoneNames': ['ZON2']
        }
    ]

    data = normalize_data_dict({"pt15": data_pt15, "pt30": data_pt30, "pt60": data_pt60})

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
            ) for j in range(0, len(bid_lists)) 
        ]
        ov = [ LpVariable (
            f"off_{off_ids[j]}_{p}",
            lowBound=0,
            upBound=off_lists[j],
            cat='Continuous'
            ) for j in range(0, len(off_lists)) 
        ]
                
        # Sub Objective: Welfare for current period
        #sub_probs.append(
        #    lpSum([bv[j]*bid_prices[j] for j in range(0, len(bid_lists))]) - lpSum([ov[j]*off_prices[j] for j in range(0, len(off_lists))])
        #)

        sub_probs.append(
            lpSum(lpDot(bv, bid_prices) - lpDot(ov, off_prices))
        )

        prob += lpSum(bv) - lpSum(ov) == 0, f"balance_bids_offs_{p}"            # Constarint 1
        for z in zone_ids:
            # Constraint 2
            prob += lpSum(
                    [ v for i,v in enumerate(bv) if bid_zones[i] == z ]
                ) - lpSum(
                    [ v for i,v in enumerate(ov) if off_zones[i] == z ]
                ) == 0, f"zone_balance_{z}_{p}"
            
    # Objective function to maximize
    prob += lpSum(sub_probs), f'maximize_daily_social_wellnes_for_{len(data)}_periods'

    status = prob.solve(PULP_CBC_CMD(msg=True))

    bv_results = []
    ov_results = []
    balance_zone_prices_results = []
    zone_prices_results = []
    for datum in data:
        p = datum['period']
        #bv_rgx_ptn = f'^bid_(\w+)_{p}$'
        bv_rgx_ptn = f'^bid_(\w+(\(\d+\))?)_{p}$'
        bv_result = {re.search(bv_rgx_ptn, v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                    if re.match(bv_rgx_ptn, v.name, re.IGNORECASE)}
        bv_results.append(bv_result)
        #ov_rgx_ptn = f'^off_(\w+)_{p}$'
        ov_rgx_ptn = f'^off_(\w+(\(\d+\))?)_{p}$'
        ov_result = {re.search(ov_rgx_ptn, v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                    if re.match(ov_rgx_ptn, v.name, re.IGNORECASE)}
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