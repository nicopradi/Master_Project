# Italian transport instance: Stackelberg game
import numpy as np

def getData():
    ''' Construct a dictionary containing all the data_file
        Returns:
            dict          dictionarry containing all the data
    '''
    # Initialize the output dictionary
    dict = {}

    # Number of alternatives in the choice set (without considering opt-out)
    dict['I'] = 4
    dict['I_opt_out'] = 4

    # Number of customers
    dict['N'] = 40

    # Number of draws
    dict['R'] = 50

    #### Parameters of the utility function
    # Alternative specific coefficients
    dict['ASC_CAR'] = 0.0
    dict['ASC_PLANE'] = -5.46
    dict['ASC_ITA'] = -1.48
    dict['ASC_NTV'] = -1.57
    dict['ASC_IC'] = -1.40
    dict['ASC_HSR'] = -1.65
    dict['ASC_AV'] = -0.0781

    # Beta coefficients
    dict['BETA_TTIME'] = -0.00745
    dict['BETA_COST_LOW'] = -0.0306
    dict['BETA_COST_HIGH'] = -0.0219
    dict['BETA_BUSINESS'] = 0.491
    dict['BETA_ORIGIN'] = 0.639

    ## Alternatives' features
    # Travel time in minutes
    dict['TTIME_CAR'] = 407.4
    dict['TTIME_PLANE'] = 70.0
    dict['TTIME_IC'] = 360.0
    dict['TTIME_AV'] = 190.0
    dict['TTIME_NTV'] = 200.0
    # Price of opt-out alternatives
    dict['PRICE_CAR'] = 104.79
    dict['PRICE_PLANE'] = 130.0
    dict['PRICE_IC_1'] = 60.0
    dict['PRICE_IC_2'] = 30.0

    # Customer's socio-economic characteristics
    # Customer id          18  121  291  476  630  860 1061 1265 1550 2043 2192 2504 2840 3174 3339 3470 4017 4287 5073 5500  371  664  801  948 1058 1450 1466 1662 1712 2439 2478 2745 2963 3384 3456 3523 3567 4115 4119 4337
    dict['BUSINESS'] =   [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    dict['ORIGIN'] =     [1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0]
    dict['LOW_INCOME'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # Random term (Gumbel distribution (0,1)) - 8 alternatives x 40 customers x 50 draws
    np.random.seed(1)
    dict['xi'] = np.random.gumbel(size=(8, 40, 50))

    # Costs
    #                                   CAR   PLANE  IC_1   IC_2   AV_1   AV_2   NTV_1  NTV_2
    dict['fixed_cost'] =    np.array([00.00, 00.00, 00.00, 00.00, 150.0, 125.0, 150.0, 125.0]) # Initial cost for each alternative
    dict['customer_cost'] = np.array([00.00, 00.00, 00.00, 00.00, 20.00, 10.00, 20.00, 10.00]) # Additional cost for each new customer

    # Lower and upper bound on prices
    #                                 CAR                PLANE                IC_1                IC_2        AV_1   AV_2   NTV_1  NTV_2
    dict['lb_p'] = np.array([dict['PRICE_CAR'], dict['PRICE_PLANE'], dict['PRICE_IC_1'], dict['PRICE_IC_2'], 00.00 ,00.00 ,00.00 ,00.00])
    dict['ub_p'] = np.array([dict['PRICE_CAR'], dict['PRICE_PLANE'], dict['PRICE_IC_1'], dict['PRICE_IC_2'], 200.0 ,200.0 ,200.0 ,200.0])

    # Choice set of the customers
    dict['choice_set'] = np.full((dict['I'] + dict['I_opt_out'], dict['N']), 1)

    # Mapping between alternatives index and their names
    dict['name_mapping'] = {0: 'Car', 1: 'Plane', 2: 'IC_1', 3: 'IC_2', 4: 'AV_1', 5: 'AV_2', 6: 'NTV_1', 7: 'NTV_2'}
    # Capacities
    #                              CAR   PLANE  IC_1   IC_2   AV_1   AV_2   NTV_1  NTV_2
    #dict['capacity'] = np.array([20.00, 20.00, 20.00, 20.00, 20.00 ,20.00 ,20.00 ,20.00]) # Availability for each alternative (opt-out always available)

    return dict

def preprocess(dict):
    ''' Precomputation on the data in order to create the corresponding
        cplex model.
    '''

    ########## Precomputation ##########
    # Priority list
    priority_list = np.empty([dict['I'] + dict['I_opt_out'], dict['N']])
    for i in range(dict['I'] + dict['I_opt_out']):
        min = 1
        max = dict['N']
        for n in range(dict['N']):
            if dict['choice_set'][i, n] == 1:
                priority_list[i, n] = min
                min += 1
            else:
                priority_list[i, n] = max
                max -= 1
    dict['priority_list'] = priority_list

    # Exogene utility
    exo_utility = np.empty([dict['I'] + dict['I_opt_out'], dict['N']])
    for n in range(dict['N']):
        for i in range(dict['I'] + dict['I_opt_out']):
            if i == 0:
                # CAR
                exo_utility[i, n] = (dict['ASC_CAR'] +
                                     dict['BETA_TTIME'] * dict['TTIME_CAR'] +
                                     dict['BETA_COST_LOW'] * dict['PRICE_CAR'] * dict['LOW_INCOME'][n] +
                                     dict['BETA_COST_HIGH'] * dict['PRICE_CAR'] * (1 - dict['LOW_INCOME'][n]))
            elif i == 1:
                # PLANE
                exo_utility[i, n] = (dict['ASC_PLANE'] +
                                     dict['BETA_TTIME'] * dict['TTIME_PLANE'] +
                                     dict['BETA_COST_LOW'] * dict['PRICE_PLANE'] * dict['LOW_INCOME'][n] +
                                     dict['BETA_COST_HIGH'] * dict['PRICE_PLANE'] * (1 - dict['LOW_INCOME'][n]) +
                                     dict['BETA_BUSINESS'] * dict['BUSINESS'][n])
            elif i == 2:
                # IC_1
                exo_utility[i, n] = (dict['ASC_ITA'] +
                                     dict['ASC_IC'] +
                                     dict['BETA_TTIME'] * dict['TTIME_IC'] +
                                     dict['BETA_COST_LOW'] * dict['PRICE_IC_1'] * dict['LOW_INCOME'][n] +
                                     dict['BETA_COST_HIGH'] * dict['PRICE_IC_1'] * (1 - dict['LOW_INCOME'][n]) +
                                     dict['BETA_BUSINESS'] * dict['BUSINESS'][n])
            elif i == 3:
                # IC_2
                exo_utility[i, n] = (dict['ASC_ITA'] +
                                     dict['ASC_IC'] +
                                     dict['BETA_TTIME'] * dict['TTIME_IC'] +
                                     dict['BETA_COST_LOW'] * dict['PRICE_IC_2'] * dict['LOW_INCOME'][n] +
                                     dict['BETA_COST_HIGH'] * dict['PRICE_IC_2'] * (1 - dict['LOW_INCOME'][n]))
            elif i == 4:
                # AV_1
                exo_utility[i, n] = (dict['ASC_ITA'] +
                                     dict['ASC_HSR'] +
                                     dict['ASC_AV'] +
                                     dict['BETA_TTIME'] * dict['TTIME_AV'] +
                                     dict['BETA_BUSINESS'] * dict['BUSINESS'][n] +
                                     dict['BETA_ORIGIN'] * dict['ORIGIN'][n])
            elif i == 5:
                # AV_2
                exo_utility[i, n] = (dict['ASC_ITA'] +
                                     dict['ASC_HSR'] +
                                     dict['ASC_AV'] +
                                     dict['BETA_TTIME'] * dict['TTIME_AV'] +
                                     dict['BETA_ORIGIN'] * dict['ORIGIN'][n])
            elif i == 6:
                # NTV_1
                exo_utility[i, n] = (dict['ASC_NTV'] +
                                     dict['ASC_HSR'] +
                                     dict['BETA_TTIME'] * dict['TTIME_NTV'] +
                                     dict['BETA_BUSINESS'] * dict['BUSINESS'][n] +
                                     dict['BETA_ORIGIN'] * dict['ORIGIN'][n])
            elif i == 7:
                # NTV_2
                exo_utility[i, n] = (dict['ASC_NTV'] +
                                     dict['ASC_HSR'] +
                                     dict['BETA_TTIME'] * dict['TTIME_NTV'] +
                                     dict['BETA_ORIGIN'] * dict['ORIGIN'][n])


    dict['exo_utility'] = exo_utility

    # Beta coefficient for endogenous variables
    endo_coef = np.full([dict['I'] + dict['I_opt_out'], dict['N']], 0.0)
    for n in range(dict['N']):
        if dict['LOW_INCOME'][n] == 1:
            endo_coef[dict['I_opt_out']:, n] = dict['BETA_COST_LOW']
        else:
            endo_coef[dict['I_opt_out']:, n] = dict['BETA_COST_HIGH']

    dict['endo_coef'] = endo_coef

    # Calculate bounds on the utility
    lb_U = np.empty([dict['I'] + dict['I_opt_out'], dict['N'], dict['R']])
    ub_U = np.empty([dict['I'] + dict['I_opt_out'], dict['N'], dict['R']])
    lb_Umin = np.full((dict['N'], dict['R']), np.inf)
    ub_Umax = np.full((dict['N'], dict['R']), -np.inf)
    M = np.empty([dict['N'], dict['R']])
    for n in range(dict['N']):
        for r in range(dict['R']):
            for i in range(dict['I'] + dict['I_opt_out']):
                    if dict['endo_coef'][i, n] > 0:
                        lb_U[i, n, r] = (dict['endo_coef'][i, n] * dict['lb_p'][i] +
                                        dict['exo_utility'][i, n] + dict['xi'][i, n, r])
                        ub_U[i, n, r] = (dict['endo_coef'][i, n] * dict['ub_p'][i] +
                                        dict['exo_utility'][i, n] + dict['xi'][i, n, r])
                    else:
                        lb_U[i, n, r] = (dict['endo_coef'][i, n] * dict['ub_p'][i] +
                                        dict['exo_utility'][i, n] + dict['xi'][i, n, r])
                        ub_U[i, n, r] = (dict['endo_coef'][i, n] * dict['lb_p'][i] +
                                        dict['exo_utility'][i, n] + dict['xi'][i, n, r])
                    # Bound for each customer, for each draw
                    if lb_U[i, n, r] < lb_Umin[n, r]:
                        lb_Umin[n, r] = lb_U[i, n, r]
                    if ub_U[i, n, r] > ub_Umax[n, r]:
                        ub_Umax[n, r] = ub_U[i, n, r]

            # Calcule the big-M values
            M[n, r] = ub_Umax[n, r] - lb_Umin[n, r]
    dict['lb_U'] = lb_U
    dict['ub_U'] = ub_U
    dict['lb_Umin'] = lb_Umin
    dict['ub_Umax'] = ub_Umax
    dict['M'] = M

if __name__ == '__main__':
    dict = getData()
    preprocess(dict)
