"""Spatial-block CV model fitting and independent temporal backtest."""
import json, joblib, numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,average_precision_score,confusion_matrix
from xgboost import XGBClassifier
from src.utils.paths import path, config
TARGET='became_urban'
def features(df): return [c for c in df if c not in {TARGET,'cell_id','geometry','x','y','block','period'} and pd.api.types.is_numeric_dtype(df[c])]
def score(y,p):
    q=(p>=.5).astype(int)
    return {'accuracy':accuracy_score(y,q),'precision':precision_score(y,q,zero_division=0),'recall':recall_score(y,q,zero_division=0),'f1':f1_score(y,q,zero_division=0),'roc_auc':roc_auc_score(y,p) if len(np.unique(y))>1 else np.nan,'pr_auc':average_precision_score(y,p) if len(np.unique(y))>1 else np.nan,'confusion_matrix':confusion_matrix(y,q).tolist()}
def candidates():
    seed=config()['model']['random_state']; imp=SimpleImputer(strategy='median')
    return {'logistic_regression':Pipeline([('impute',imp),('scale',StandardScaler()),('model',LogisticRegression(max_iter=2000,class_weight='balanced',random_state=seed))]),'random_forest':Pipeline([('impute',imp),('model',RandomForestClassifier(n_estimators=350,min_samples_leaf=3,class_weight='balanced_subsample',n_jobs=-1,random_state=seed))]),'xgboost':Pipeline([('impute',imp),('model',XGBClassifier(n_estimators=300,max_depth=5,learning_rate=.05,subsample=.8,colsample_bytree=.8,scale_pos_weight=5,eval_metric='logloss',random_state=seed))])}
def train(train_csv=None,test_csv=None):
    qc=config().get('quality_control',{})
    if qc.get('ml_paused') or not qc.get('lulc_qc_passed'):
        raise RuntimeError('ML is paused: corrected LULC layers have not passed QC.')
    train=pd.read_csv(train_csv or path('data','processed','train_2015_2020.csv')); test=pd.read_csv(test_csv or path('data','processed','test_2020_2025.csv')); cols=features(train)
    groups=train['block'] if 'block' in train else pd.qcut(train['x'],config()['model']['spatial_blocks'],labels=False,duplicates='drop'); cv=GroupKFold(n_splits=min(config()['model']['spatial_blocks'],groups.nunique())); rows=[]; champion=(-1,None)
    for name,model in candidates().items():
        folds=[]
        for a,b in cv.split(train[cols],train[TARGET],groups):
            model.fit(train.iloc[a][cols],train.iloc[a][TARGET]); folds.append(score(train.iloc[b][TARGET].to_numpy(),model.predict_proba(train.iloc[b][cols])[:,1]))
        mean={k:float(np.nanmean([f[k] for f in folds])) for k in ['accuracy','precision','recall','f1','roc_auc','pr_auc']}; rows.append({'model':name,**mean})
        if mean['pr_auc']>champion[0]: champion=(mean['pr_auc'],name)
    name=champion[1]; model=candidates()[name].fit(train[cols],train[TARGET]); p=model.predict_proba(test[cols])[:,1]; report=score(test[TARGET].to_numpy(),p); observed=test[TARGET].to_numpy().astype(bool); pred=p>=.5; union=(observed|pred).sum(); report.update({'model':name,'iou':float((observed&pred).sum()/union) if union else np.nan})
    pd.DataFrame(rows).to_csv(path('outputs','metrics','spatial_cv_model_comparison.csv'),index=False); path('outputs','metrics','temporal_backtest_2025.json').write_text(json.dumps(report,indent=2)); joblib.dump({'model':model,'features':cols,'selected_model':name},path('models','final_model.joblib')); return name,report
if __name__=='__main__': train()
