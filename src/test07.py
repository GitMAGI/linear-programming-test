from pulp import * 
from time import strftime

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
                    new_datum['OFFMAR'] = datum['OFFMAR']
                else:
                    new_datum['OFFID'] += [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['OFFID']]
                    new_datum['OFFList'] += datum['OFFList']
                    new_datum['OFFPrices'] += datum['OFFPrices']
                    new_datum['OFFZones'] += datum['OFFZones']
                    new_datum['OFFMAR'] += datum['OFFMAR']

                if not 'BIDID' in new_datum.keys():
                    new_datum['BIDID'] = [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['BIDID']]
                    new_datum['BIDList'] = datum['BIDList']
                    new_datum['BIDPrices'] = datum['BIDPrices']
                    new_datum['BIDZones'] = datum['BIDZones']
                    new_datum['BIDMAR'] = datum['BIDMAR']
                else:
                    new_datum['BIDID'] += [f'{x}' if mtu_mult_factor == 1 else f'{x}({i})' for x in datum['BIDID']]
                    new_datum['BIDList'] += datum['BIDList']
                    new_datum['BIDPrices'] += datum['BIDPrices']
                    new_datum['BIDZones'] += datum['BIDZones']
                    new_datum['BIDMAR'] += datum['BIDMAR']

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
    in_file_name = 'fully_accepted_2.json'
    #in_file_name = 'partially_accepted_3.json'

    data_dict = {}
    with open(os.path.join(input_path, in_file_name), 'r') as f:
        data_dict = json.load(f)

    data_pt15 = data_dict["data_pt15"] if "data_pt15" in data_dict.keys() else []
    data_pt30 = data_dict["data_pt30"] if "data_pt30" in data_dict.keys() else []
    data_pt60 = data_dict["data_pt60"] if "data_pt60" in data_dict.keys() else []

    data = normalize_data_dict({"pt15": data_pt15, "pt30": data_pt30, "pt60": data_pt60})

    m_rgx_ptn = f'^(\w+)(\(\d+\))$'

    prob = LpProblem("Euphemia_problem", LpMaximize)
    sub_probs = []
    
    m_bin_bv = []
    m_bin_ov = []

    for datum in data:
        p = datum['period'] 

        off_ids = datum['OFFID']
        off_lists = datum['OFFList']
        off_prices = datum['OFFPrices']
        off_zones = datum['OFFZones']
        off_mars = datum['OFFMAR']
        bid_ids = datum['BIDID']
        bid_lists = datum['BIDList']
        bid_prices = datum['BIDPrices']
        bid_zones = datum['BIDZones']
        bid_mars = datum['BIDMAR']
        zone_ids = datum['Zones']

        bv = [ LpVariable (
                f"bid_{bid_ids[j]}_{p}",
                lowBound=0,
                upBound=bid_lists[j],
                cat='Continuous'
            ) for j in range(0, len(bid_lists)) 
            if not re.match(m_rgx_ptn, bid_ids[j])
        ]
        ov = [ LpVariable (
            f"off_{off_ids[j]}_{p}",
            lowBound=0,
            upBound=off_lists[j],
            cat='Continuous'
            ) for j in range(0, len(off_lists)) 
            if not re.match(m_rgx_ptn, off_ids[j])
        ]

        m_bv = []
        m_aux_bv = []
        m_prices_bv = []
        m_zones_bv = []
        for vname, local_i, vqt, vpr, vzn, mar in [
            (re.search(m_rgx_ptn, bid_ids[j]).group(1), re.search(m_rgx_ptn, bid_ids[j]).group(2), bid_lists[j], bid_prices[j], bid_zones[j], bid_mars[j]) 
            for j in range(0, len(bid_lists)) 
            if re.match(m_rgx_ptn, bid_ids[j])
        ]:
            m_bvar = LpVariable (
                f"bid_{vname}{local_i}_{p}",
                lowBound=0,
                upBound=vqt,
                cat='Continuous'
            )
            m_aux_bvar = LpVariable (
                f"aux_bid_{vname}{local_i}_{p}",
                lowBound=0,
                upBound=vqt,
                cat='Continuous'
            )
            m_bv.append(m_bvar)
            m_aux_bv.append(m_aux_bvar)
            m_prices_bv.append(vpr)
            m_zones_bv.append(vzn)
            if f"bin_bid_{vname}" not in [x.name for x in m_bin_bv]:
                m_bin_bvar = LpVariable (
                    f"bin_bid_{vname}",
                    lowBound=0,
                    upBound=1,
                    cat='Binary'
                    )
                m_bin_bv.append(m_bin_bvar)
            else:
                m_bin_bvar = next(iter(filter(lambda x: x.name == f"bin_bid_{vname}", m_bin_bv)), None)

            # Vincolo di quantità massima per l'offerta composita
            prob += m_bvar <= vqt * m_bin_bvar, f"max_composite_offer_{vname}{local_i}_bid_{p}"
            # Vincolo di quota minima per ciascuna unità di tempo
            prob += m_bvar >= mar * vqt * m_bin_bvar, f"min_composite_offer_{vname}{local_i}_bid_{p}"

            # Vincoli di linearizzazione per x_b_p_aux = x_b_p * y_b
            prob += m_aux_bvar <= m_bvar, f"linearization_1_{vname}{local_i}_bid_{p}"
            prob += m_aux_bvar <= vqt * m_bin_bvar, f"linearization_2_{vname}{local_i}_bid_{p}"
            prob += m_aux_bvar >= m_bvar - vqt * (1 - m_bin_bvar), f"linearization_3_{vname}{local_i}_bid_{p}"

        m_ov = []
        m_aux_ov = []
        m_prices_ov = []
        m_zones_ov = []
        for vname, local_i, vqt, vpr, vzn, mar in [
            (re.search(m_rgx_ptn, off_ids[j]).group(1), re.search(m_rgx_ptn, off_ids[j]).group(2), off_lists[j], off_prices[j], off_zones[j], off_mars[j]) 
            for j in range(0, len(off_lists)) 
            if re.match(m_rgx_ptn, off_ids[j])
        ]:
            m_ovar = LpVariable (
                f"off_{vname}{local_i}_{p}",
                lowBound=0,
                upBound=vqt,
                cat='Continuous'
            )
            m_ov.append(m_ovar)
            m_aux_ovar = LpVariable (
                f"aux_off_{vname}{local_i}_{p}",
                lowBound=0,
                upBound=vqt,
                cat='Continuous'
            )
            m_aux_ov.append(m_aux_ovar)
            m_prices_ov.append(vpr)
            m_zones_ov.append(vzn)
            if f"bin_off_{vname}" not in [x.name for x in m_bin_ov]:
                m_bin_ovar = LpVariable (
                    f"bin_off_{vname}",
                    lowBound=0,
                    upBound=1,
                    cat='Binary'
                    )
                m_bin_ov.append(m_bin_ovar)
            else:
                m_bin_ovar = next(iter(filter(lambda x: x.name == f"bin_off_{vname}", m_bin_ov)), None)

            # Vincolo di quantità massima per l'offerta composita
            prob += m_ovar <= vqt * m_bin_ovar, f"max_composite_offer_{vname}{local_i}_off_{p}"
            # Vincolo di quota minima per ciascuna unità di tempo
            prob += m_ovar >= mar * vqt * m_bin_ovar, f"min_composite_offer_{vname}{local_i}_off_{p}"

            # Vincoli di linearizzazione per x_b_p_aux = x_b_p * y_b
            prob += m_aux_ovar <= m_ovar, f"linearization_1_{vname}{local_i}_off_{p}"
            prob += m_aux_ovar <= vqt * m_bin_ovar, f"linearization_2_{vname}{local_i}_off_{p}"
            prob += m_aux_ovar >= m_ovar - vqt * (1 - m_bin_ovar), f"linearization_3_{vname}{local_i}_off_{p}"

        # Sub Objective: Welfare for current period
        #sub_probs.append(
        #    lpSum([bv[j]*bid_prices[j] for j in range(0, len(bid_lists))]) - lpSum([ov[j]*off_prices[j] for j in range(0, len(off_lists))])
        #)

        sub_probs.append(
            lpSum(lpDot(bv, bid_prices) + lpDot(m_aux_bv, m_prices_bv) - lpDot(ov, off_prices) - lpDot(m_aux_ov, m_prices_ov))
        )

        # Constarint 1
        prob += lpSum(bv) + lpSum(m_aux_bv) - lpSum(ov) - lpSum(m_aux_ov) == 0, f"balance_bids_offs_{p}"

        for z in zone_ids:
            # Constraint 2
            prob += lpSum(
                    [ v for i,v in enumerate(bv) if bid_zones[i] == z ]
                ) + lpSum(
                    [ v for i,v in enumerate(m_aux_bv) if m_zones_bv[i] == z ]
                ) - lpSum(
                    [ v for i,v in enumerate(ov) if off_zones[i] == z ]
                ) - lpSum(
                    [ v for i,v in enumerate(m_aux_ov) if m_zones_ov[i] == z ]
                ) == 0, f"zone_balance_{z}_{p}"
            
    # Objective function to maximize
    prob += lpSum(sub_probs), f'maximize_daily_social_wellnes_for_{len(data)}_periods'

    problem_name = 'test07'
    log_path = os.path.join('logs')
    fname_cmp = strftime('%Y%m%d-%H%M%S')

    os.makedirs(log_path, exist_ok=True) 
    prob.writeLP(os.path.join(log_path, f"{problem_name}_{fname_cmp}.lp"))
    solve_return = prob.solve(PULP_CBC_CMD(msg=True)) 
    prob.writeMPS(os.path.join(log_path, f"{problem_name}_{fname_cmp}.mps"))
    if solve_return != 1:
        raise Exception(f"Problem resolution failed. Status: {LpStatus[prob.status]}")

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
    print(f"balance_zone_prices_results: {balance_zone_prices_results}")

    print("Completed")
    return 1

if __name__ == '__main__':
    main()