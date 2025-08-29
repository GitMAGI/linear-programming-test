from pulp import * 
from time import strftime

def normalize_data_dict(data_dict):
    """
    Costruisce un array di oggetti 'new_data'. L'oridnamento dei periodi segue l'indicizzazione di 'new_data'. 
    """
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
                    new_datum['OFFID'] = [f'{x}_{pt.lower()}' for x in datum['OFFID']]
                    new_datum['OFFList'] = datum['OFFList']
                    new_datum['OFFPrices'] = datum['OFFPrices']
                    new_datum['OFFZones'] = datum['OFFZones']
                    #new_datum['OFFMAR'] = datum['OFFMAR']
                else:
                    new_datum['OFFID'] += [f'{x}_{pt.lower()}' for x in datum['OFFID']]
                    new_datum['OFFList'] += datum['OFFList']
                    new_datum['OFFPrices'] += datum['OFFPrices']
                    new_datum['OFFZones'] += datum['OFFZones']
                    #new_datum['OFFMAR'] += datum['OFFMAR']

                if not 'BIDID' in new_datum.keys():
                    new_datum['BIDID'] = [f'{x}_{pt.lower()}' for x in datum['BIDID']]
                    new_datum['BIDList'] = datum['BIDList']
                    new_datum['BIDPrices'] = datum['BIDPrices']
                    new_datum['BIDZones'] = datum['BIDZones']
                    #new_datum['BIDMAR'] = datum['BIDMAR']
                else:
                    new_datum['BIDID'] += [f'{x}_{pt.lower()}' for x in datum['BIDID']]
                    new_datum['BIDList'] += datum['BIDList']
                    new_datum['BIDPrices'] += datum['BIDPrices']
                    new_datum['BIDZones'] += datum['BIDZones']
                    #new_datum['BIDMAR'] += datum['BIDMAR']

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

    input_path = 'inputs'
    #in_file_name = 'fully_accepted_1.json'
    #in_file_name = 'fully_accepted_2.json'
    #in_file_name = 'partially_accepted_3.json'
    #in_file_name = 'partially_accepted_4.json'
    in_file_name = 'paradoxally_rejected_5.json'

    data_dict = {}
    with open(os.path.join(input_path, in_file_name), 'r') as f:
        data_dict = json.load(f)

    data_pt15 = data_dict["data_pt15"] if "data_pt15" in data_dict.keys() else []
    data_pt30 = data_dict["data_pt30"] if "data_pt30" in data_dict.keys() else []
    data_pt60 = data_dict["data_pt60"] if "data_pt60" in data_dict.keys() else []

    data = normalize_data_dict({"pt15": data_pt15, "pt30": data_pt30, "pt60": data_pt60})
    
    m_rgx_ptn = '^(\w+)_pt(\d{2})$'

    prob = LpProblem("Euphemia_problem", LpMaximize)
    sub_probs = []

    for datum in data:
        pt15_p = datum['period']

        off_ids = datum['OFFID']
        off_lists = datum['OFFList']
        off_prices = datum['OFFPrices']
        off_zones = datum['OFFZones']
        bid_ids = datum['BIDID']
        bid_lists = datum['BIDList']
        bid_prices = datum['BIDPrices']
        bid_zones = datum['BIDZones']
        zone_ids = datum['Zones']

        ovs = []
        for j in range(0, len(off_ids)):
            if not re.match(m_rgx_ptn, off_ids[j]):
                continue

            vname = re.search(m_rgx_ptn, off_ids[j]).group(1)
            mtu = int(re.search(m_rgx_ptn, off_ids[j]).group(2))
            if mtu == 15:
                p = pt15_p
            else:
                mtu_mult_factor = int(mtu/15)
                p = int((pt15_p-1)/mtu_mult_factor)+1

            ov = next(
                (v for v in prob.variables() if v.name == f"off_{vname}_pt{mtu}_{p}"), 
                LpVariable (
                    f"off_{vname}_pt{mtu}_{p}",
                    lowBound=0,
                    upBound=off_lists[j],
                    cat='Continuous'
                )
            )
            ovs.append(ov)

        bvs = []
        for j in range(0, len(bid_ids)):
            if not re.match(m_rgx_ptn, bid_ids[j]):
                continue
            
            vname = re.search(m_rgx_ptn, bid_ids[j]).group(1)
            mtu = int(re.search(m_rgx_ptn, bid_ids[j]).group(2))
            if mtu == 15:
                p = pt15_p
            else:
                mtu_mult_factor = int(mtu/15)
                p = int((pt15_p-1)/mtu_mult_factor)+1

            bv = next(
                (v for v in prob.variables() if v.name == f"bid_{vname}_pt{mtu}_{p}"), 
                LpVariable (
                    f"bid_{vname}_pt{mtu}_{p}",
                    lowBound=0,
                    upBound=bid_lists[j],
                    cat='Continuous'
                )
            )
            bvs.append(bv)

        sub_probs.append(lpSum(lpDot(bvs, bid_prices) - lpDot(ovs, off_prices)))

        # Constarint 1
        prob += lpSum(bvs) - lpSum(ovs) == 0, f"balance_bids_offs_{pt15_p}"

        for z in zone_ids:
            # Constraint 2
            prob += lpSum(
                    [ v for i,v in enumerate(bvs) if bid_zones[i] == z ]
                ) - lpSum(
                    [ v for i,v in enumerate(ovs) if off_zones[i] == z ]
                ) == 0, f"zone_balance_{z}_{pt15_p}"
            
    # Objective function to maximize
    prob += lpSum(sub_probs), f'maximize_daily_social_wellnes_for_{len(data)}_periods'

    problem_name = 'test08'
    log_path = os.path.join('logs')
    fname_cmp = strftime('%Y%m%d-%H%M%S')

    os.makedirs(log_path, exist_ok=True) 
    prob.writeLP(os.path.join(log_path, f"{problem_name}_{fname_cmp}.lp"))
    solve_return = prob.solve(PULP_CBC_CMD(msg=True)) 
    prob.writeMPS(os.path.join(log_path, f"{problem_name}_{fname_cmp}.mps"))
    if solve_return != 1:
        raise Exception(f"Problem resolution failed. Status: {LpStatus[prob.status]}")

    ov_results = []
    bv_results = []
    balance_zone_prices_results = []
    zone_prices_results = []

    for datum in data:
        pt15_p = datum['period']

        off_ids = datum['OFFID']
        bid_ids = datum['BIDID']

        for j in range(0, len(off_ids)):
            vname = re.search(m_rgx_ptn, off_ids[j]).group(1)
            mtu = int(re.search(m_rgx_ptn, off_ids[j]).group(2))
            if mtu == 15:
                p = pt15_p
            else:
                mtu_mult_factor = int(mtu/15)
                p = int((pt15_p-1)/mtu_mult_factor)+1

            ov_rgx_ptn = f'^off_({vname})_pt{mtu}_{p}$'
            ov_result = {re.search(ov_rgx_ptn, v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                        if re.match(ov_rgx_ptn, v.name, re.IGNORECASE)}
            ov_results.append(ov_result)

        for j in range(0, len(bid_ids)):
            vname = re.search(m_rgx_ptn, bid_ids[j]).group(1)
            mtu = int(re.search(m_rgx_ptn, bid_ids[j]).group(2))
            if mtu == 15:
                p = pt15_p
            else:
                mtu_mult_factor = int(mtu/15)
                p = int((pt15_p-1)/mtu_mult_factor)+1
        
            bv_rgx_ptn = f'^bid_({vname})_pt{mtu}_{p}$'
            bv_result = {re.search(bv_rgx_ptn, v.name).group(1): round(v.varValue,4) for v in prob.variables() \
                        if re.match(bv_rgx_ptn, v.name, re.IGNORECASE)}
            bv_results.append(bv_result)

        # Balance Bids/Offs in dual mode (price?)        
        balance_main = next(c.pi for name, c in prob.constraints.items() if name == f"balance_bids_offs_{pt15_p}")
        # Balance Zone in dual mode (shadow proces)
        zone_blanace_contraint_regex = re.compile(f'^zone_balance_(\w+)_{pt15_p}$')
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

    print(f"offs: {ov_results}")
    print(f"bids: {bv_results}")
    print(f"zone_prices_results: {zone_prices_results}")
    print(f"balance_zone_prices_results: {balance_zone_prices_results}")

    print("Completed")
    return 1

if __name__ == '__main__':
    main()