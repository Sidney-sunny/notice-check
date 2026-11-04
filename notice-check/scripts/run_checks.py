from pathlib import Path
import json,sys,copy,hashlib,datetime
S=Path(__file__).resolve().parent.parent;O=S/'resources'
sys.path.insert(0,str(S/'scripts'))
from check_result import validate,render
records=[]
for f in sorted((O/'tests').glob('C*/actual.json')):
 d=json.loads(f.read_text(encoding='utf8'));c=json.loads((f.parent/'criteria.json').read_text(encoding='utf8'));err=validate(d)
 for key,value in c.items():
  field,_,attr=key.partition('_');attr=attr or 'value'
  if not any(x['field']==field and value in x.get(attr,'') for x in d['items']):err.append('不满足核对标准 '+key)
 records.append(dict(case=f.parent.name,ok=not err,errors=err,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
# These are deliberate corruptions of already-authored results, not model failures.
base=json.loads(next((O/'tests').glob('C03*/actual.json')).read_text(encoding='utf8'))
mutations=[]
bad=copy.deepcopy(base);bad['items'][3]['value']+=' 23:59';mutations.append(('擅补截止时刻',bad))
bad=copy.deepcopy(base);bad['items'][0]['evidence'][0]['quote']='不存在的引用';mutations.append(('虚构引文',bad))
bad=copy.deepcopy(base);bad['items'][0]['status']='已核实符合资格';mutations.append(('非法状态',bad))
bad=copy.deepcopy(base);bad['items']=[x for x in bad['items'] if x['field']!='作品入口'];mutations.append(('遗漏独立入口字段',bad))
negative=[]
for label,bad in mutations:
 errors=validate(bad);negative.append(dict(name=label,rejected=bool(errors),errors=errors))
 (O/'tests'/('negative_'+str(len(negative))+'.json')).write_text(json.dumps(bad,ensure_ascii=False,indent=2),encoding='utf8')
report=dict(date='2026-11-04',method='当前会话AI提取8组一次；脚本重验结构和预设关键约束，非独立模型运行或人工评审',cases=records,negative_tests=negative,retest='修正真实截图输出的材料规格引用绑定错误后，重跑全部结构及关键约束；故障注入只测试校验器',all_ok=all(x['ok'] for x in records) and all(x['rejected'] for x in negative))
(O/'tests/checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
if not report['all_ok']:raise SystemExit(1)
