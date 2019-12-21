import pandas as pd
import numpy as np
import lightgbm as lgb

dev = pd.concat([pd.read_csv("../Data/train_features_fold_{}.csv".format(i)) for i in range(9)]).reset_index(drop = True)
val = pd.read_csv("../Data/train_features_fold_9.csv")
test = pd.read_csv("../Data/test_features.csv")

indep_vars = list(dev.columns)[3:]

params = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective':'binary',
    'metric': {'auc'},
    'num_leaves': 500,
    'learning_rate': 0.0175,
    'feature_fraction': 0.72,
    'bagging_fraction': 0.75,
    'bagging_freq': 5,
    'verbose': 1,
    'min_data_in_leaf' : 100,
    'max_bin' : 256,
    'lambda_l1' : 0.0025,
    'lambda_l2' : 0.0025,
    'min_gain_to_split' : 0.05,
    'min_sum_hessian_in_leaf': 12.0
}


lgb_dev = lgb.Dataset(dev[indep_vars].values.astype(np.float32), dev['is_chat'] )
lgb_val = lgb.Dataset(val[indep_vars].values.astype(np.float32), val['is_chat'] )

model = lgb.train(params, lgb_dev, num_boost_round = 5000, valid_sets = (lgb_dev, lgb_val),early_stopping_rounds = 200,
             verbose_eval = 10)


pred = model.predict(test[indep_vars].values.astype(np.float32))
test['is_chat'] = pred
test['is_chat'] = test['is_chat']
test[['id', 'is_chat']].to_csv("./submission.csv", index = False)