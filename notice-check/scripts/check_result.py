"""Check an AI-authored evidence ledger; never extracts notice facts."""
import argparse, json, re
from pathlib import Path
STATES={'原文已明确','已读部分未发现','无法读取或核实','存在冲突'}
REQUIRED={'参赛对象','团队人数','指导教师','报名截止','资格审核','作品提交截止','材料规格','报名入口','作品入口'}
def validate(d):
 errors=[]
 for k in ('summary','sources','items','priorities'):
  if k not in d: errors.append('缺顶层字段 '+k)
 if errors:return errors
 if not isinstance(d['summary'],str) or not isinstance(d['sources'],list) or not isinstance(d['items'],list) or not isinstance(d['priorities'],list):return ['顶层类型错误']
 sources={}
 for s in d['sources']:
  if not isinstance(s,dict) or any(not isinstance(s.get(k),str) for k in ('id','name','publisher','date','locator','coverage','text')):
   errors.append('来源结构错误');continue
  if s['id'] in sources:errors.append('来源编号重复')
  sources[s['id']]=s
 fields=set()
 for x in d['items']:
  if not isinstance(x,dict) or any(not isinstance(x.get(k),str) for k in ('field','value','scope','status')) or not isinstance(x.get('evidence'),list):
   errors.append('项目结构错误');continue
  fields.add(x['field'])
  if x['status'] not in STATES:errors.append('非法状态 '+x['field'])
  if x['status'] in {'原文已明确','存在冲突'} and not x['evidence']:errors.append('明确／冲突项缺依据 '+x['field'])
  quotes=[]
  for e in x['evidence']:
   if not isinstance(e,dict) or not isinstance(e.get('quote'),str) or e.get('source') not in sources:
    errors.append('引用结构或来源错误 '+x['field']);continue
   if not e['quote'] or e['quote'] not in sources[e['source']]['text']:errors.append('引文不在已读文字中 '+x['field'])
   quotes.append(e['quote'])
  if x['field'] in {'报名截止','资格审核','作品提交截止'}:
   evidence=' '.join(quotes)
   for token in re.findall(r'\d{4}年|\d{1,2}:\d{2}',x['value']):
    if token not in evidence:errors.append('日期精度无引用支持 '+x['field']+': '+token)
 if REQUIRED-fields:errors.append('缺核对项目 '+','.join(sorted(REQUIRED-fields)))
 if not d['priorities'] or any(not isinstance(p,str) for p in d['priorities']):errors.append('缺待核实清单或类型错误')
 for c in d.get('changes',[]):
  if not isinstance(c,dict) or any(not isinstance(c.get(k),str) for k in ('field','old','new','source','quote')):errors.append('变更结构错误');continue
  if c['source'] not in sources or not c['quote'] or c['quote'] not in sources.get(c['source'],{}).get('text',''):errors.append('变更依据无效')
  if c['new'] not in c['quote']:errors.append('变更新值不在引文')
 return errors
def render(d):
 def esc(s):return str(s).replace('|','／').replace('\n','；')
 lines=['# 报名事项核对清单','',d['summary'],'','## 材料及实际覆盖','', '|编号|名称／发布单位／日期|来源定位|实际覆盖|','|---|---|---|---|']
 for s in d['sources']:lines.append('|'+ '|'.join(map(esc,[s['id'],s['name']+'／'+s['publisher']+'／'+s['date'],s['locator'],s['coverage']]))+'|')
 lines+=['','## 核对表','','|项目|提取结果|原文依据|适用范围|信息状态|','|---|---|---|---|---|']
 for x in d['items']:
  ev='；'.join(e['source']+'：'+e['quote'] for e in x['evidence']) or '无可读取依据，见材料覆盖'
  lines.append('|'+ '|'.join(map(esc,[x['field'],x['value'],ev,x['scope'],x['status']]))+'|')
 lines+=['','## 分阶段时间安排','']
 for x in d['items']:
  if x['field'] in {'报名截止','资格审核','作品提交截止'}:lines.append('- '+x['field']+'（'+x['scope']+'）：'+x['value']+'；'+x['status'])
 lines+=['','## 材料及入口清单','']
 for x in d['items']:
  if x['field'] in {'材料规格','报名入口','作品入口'}:lines.append('- '+x['field']+'（'+x['scope']+'）：'+x['value']+'；'+x['status'])
 lines+=['','## 变更记录','']
 for c in d.get('changes',[]):lines.append('- '+c['field']+'：'+c['old']+' → '+c['new']+'；'+c['source']+'：'+c['quote'])
 if not d.get('changes'):lines.append('没有可确认的字段替换；冲突值保持并列。')
 lines+=['','## 优先核实事项','']+['- '+p for p in d['priorities']]
 lines+=['','## 复核范围','','已按阶段、范围、日期精度及引用检查；结构脚本不替代发布方确认和独立人工语义复核。']
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--markdown');a=p.parse_args()
 try:d=json.loads(Path(a.input).read_text(encoding='utf-8'));errors=validate(d)
 except (OSError,ValueError,TypeError) as e:errors=[str(e)]
 if errors:print(json.dumps({'ok':False,'errors':errors},ensure_ascii=False));raise SystemExit(1)
 if a.markdown:Path(a.markdown).write_text(render(d),encoding='utf-8')
 print(json.dumps({'ok':True,'items':len(d['items'])},ensure_ascii=False))
