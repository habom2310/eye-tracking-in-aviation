import anova
import scipy
import numpy as np
import pandas as pd

# standardized effect size - cohen's d 
def cohend_ES(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return abs((np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1) ** 2 + (ny-1)*np.std(y, ddof=1) ** 2) / dof))

def hypothesis_test_group(df_features, trial = 1, test="t", es_func = "cohen"):
    exclude_cols = ["index", "pID", "group", "trial", "null_percent"]
    cols = [c for c in list(df_features.columns) if c not in exclude_cols]
    
    print("test between group 1 and group 2 in trial", trial)
    df_trial = df_features[df_features["trial"] == trial]
    df_1 = df_trial[df_trial["group"] == 1]
    df_2 = df_trial[df_trial["group"] == 2]
    
    print("Number of samples in group 1:", len(df_1))
    print("Number of samples in group 2:", len(df_2))
    
    test_function = anova.FPvalue
    if test == "anova":
        test_function = anova.FPvalue
    elif test == "t":
        test_function = scipy.stats.ttest_ind
        if trial == 0:
            test_function = scipy.stats.ttest_rel
        
    if es_func == "eta":
        ES_function = anova.EffectSize
    elif es_func == "cohen":
        ES_function = cohend_ES
    
    ll = []
    lpl = []
    test_val = []
    p_val = []
    ES = []
    for col in cols:
        
        #levene's test
        l, pl = scipy.stats.levene(df_1.loc[:,col], df_2.loc[:,col])
        ll.append(l)
        lpl.append(pl)
        
        test_result = test_function(df_1.loc[:,col], df_2.loc[:,col])
        f = test_result[0]
        p = test_result[1]
        
        e = ES_function(df_1.loc[:,col], df_2.loc[:,col])
        
        test_val.append(f)
        p_val.append(p)
        ES.append(e)
    
    print("test: {}, effect size: {}".format(test, es_func))
    return pd.DataFrame({"ROI": cols,
                        "levene: l-value": ll,
                        "levene: p-value": lpl,
                        f"{test}: t-value": test_val,
                        f"{test}: p-value": p_val,
                        f"ES ({es_func})": ES})


def hypothesis_test_trial(df_features, test = "anova", es_func = "eta"):
    exclude_cols = ["index", "pID", "group", "trial", "null_percent"]
    cols = [c for c in list(df_features.columns) if c not in exclude_cols]
    
    df_trial = df_features
    print("test between trial 1 and trial 2 and trial 3")
    df_1 = df_trial[df_trial["trial"] == 1]
    df_2 = df_trial[df_trial["trial"] == 2]
    df_3 = df_trial[df_trial["trial"] == 3]

    set_pid = set(df_1["pID"]).intersection(set(df_2["pID"])).intersection(set(df_3["pID"]))
    df_1 = df_1[df_1["pID"].isin(list(set_pid))]
    df_2 = df_2[df_2["pID"].isin(list(set_pid))]
    df_3 = df_3[df_3["pID"].isin(list(set_pid))]
    
    print("Number of samples in trial 1:", len(df_1))
    print("Number of samples in trial 2:", len(df_2))
    print("Number of samples in trial 3:", len(df_3))
    
    test_function = anova.FPvalue
    ES_function = anova.EffectSize
    
    ll = []
    lpl = []
    test_val = []
    p_val = []
    ES = []
    for col in cols:
        test_result = test_function(df_1.loc[:,col], df_3.loc[:,col])
        f = test_result[0]
        p = test_result[1]
        
        e = ES_function(df_1.loc[:,col], df_3.loc[:,col])
        
        test_val.append(f)
        p_val.append(p)
        ES.append(e)
    print("test: {}, effect size: {}".format(test, es_func))
    return pd.DataFrame({"ROI": cols,
                        f"{test}: t-value": test_val,
                        f"{test}: p-value": p_val,
                        f"ES ({es_func})": ES})

def eta_squared(aov):
    aov['eta_sq'] = 'NaN'
    aov['eta_sq'] = aov[:-1]['sum_sq']/sum(aov['sum_sq'])
    return aov

def omega_squared(aov):
    mse = aov['sum_sq'][-1]/aov['df'][-1]
    aov['omega_sq'] = 'NaN'
    aov['omega_sq'] = (aov[:-1]['sum_sq']-(aov[:-1]['df']*mse))/(sum(aov['sum_sq'])+mse)
    return aov

def create_anova_df(df_data, cols):
    '''
    cols: names of the columns
    '''
    ls_group = []
    ls_roi_id = []
    ls_val = []
    # cols = ["fix_rate_runway", "fix_rate_asi", "fix_rate_alt", "fix_rate_hsi"]
    # for i in range(len(df_dwell[["group","duration_average_runway", "duration_average_asi", "duration_average_alt", "duration_average_hsi"]])):
    for i in range(len(df_data)):
        x = df_data.iloc[i]
        if x["group"] == 1:
            gr = 0
        else:
            gr = 1
    #     for j,v in enumerate(["duration_average_runway", "duration_average_asi", "duration_average_alt", "duration_average_hsi"]):
        for j,v in enumerate(cols):
            ls_group.append(gr)
            ls_roi_id.append(j)
            ls_val.append(x[v])

    df_anova = pd.DataFrame(zip(ls_group, ls_roi_id, ls_val), columns = ["group", "ROI", "value"])
    return df_anova

def two_way_ANOVA(df_anova):
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    #perform two-way ANOVA
    model = ols('value ~ C(group) + C(ROI) + C(group):C(ROI)', data=df_anova).fit()
    aov_table = sm.stats.anova_lm(model, typ=2)
    return aov_table

def levene_test_twoway_anova(df_anova):
    a1 = df_anova[df_anova["ROI"] == 0]['value']
    a2 = df_anova[df_anova["ROI"] == 1]['value']
    a3 = df_anova[df_anova["ROI"] == 2]['value']
    a4 = df_anova[df_anova["ROI"] == 3]['value']

    a5 = df_anova[df_anova["group"] == 0]['value']
    a6 = df_anova[df_anova["group"] == 1]['value']

    print("levene roi", scipy.stats.levene(a1,a2,a3,a4))
    print("levene group", scipy.stats.levene(a5,a6))
    return scipy.stats.levene(a1,a2,a3,a4), scipy.stats.levene(a5,a6)