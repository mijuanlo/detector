#!/usr/bin/env python
from utils.log import log
import re

T_COMMENT='#'
T_MULTIPLE='*'
T_CAPTURE='()'
T_REPLACE='{}'
T_SEP=','
T_SPLIT='->'
T_HINT='?'
T_CHILD='.'
T_EQUAL='='
T_NOT_EQUAL='!='
T_LIKE='%'
T_GT='<'
T_LT='>'
T_CONTAIN='%'
L_STR=['\'','"']
L_EMPTY=['\t',' ']

class ruleset:
    def __init__(self):
        self.l_spliters=[T_COMMENT,T_SEP,T_SPLIT,T_HINT]
        self.l_ops=[T_EQUAL,T_NOT_EQUAL,T_CAPTURE]
        self.l_template=[T_MULTIPLE,T_REPLACE]
        self.rules=[]
        self.data=None
        self.data_values={}
        pass

    def read_until(self,st,until,invert=False,*args,**kwargs):
        def first_in_until(st,combined):
            idxfirst=[]
            for t in combined:
                i=-1
                try:
                    i=st.index(t,i+1)
                except:
                    pass
                if i == -1:
                    i=9999
                idxfirst.append(i)
            midxfirst=min(idxfirst)
            if combined[idxfirst.index(midxfirst)] in until:
                return True
            return False

        idxs=[]
        start=-1
        if not first_in_until(st,L_STR+until):
            for s in L_STR:
                i=-1
                tmp=-1
                double=True
                try:
                    while True:
                        if double and first_in_until(st[tmp+1:],L_STR+until):
                            idxs.append(i)
                            break
                        tmp=st.index(s,tmp+1)
                        if st[tmp-1]!='\\':
                            double=not double
                            i=tmp
                except Exception as e:
                    if not double:
                        #raise Exception('Unbalanced quotes')
                        i=9999
                    idxs.append(i)

            start=min(idxs)
            if start==-1:
                start=max(idxs)
        idx=[]
        if invert:
            for u in until:
                if start != -1:
                    i=start+1
                else:
                    i=-1
                try:
                    while True:
                        i=st.index(u,i+1)
                except:
                    if i == -1:
                        i=len(st)
                idx.append(i)
        else:
            for u in until:
                if start != -1:
                    i=start+1
                else:
                    i=-1
                try:
                    i=st.index(u,i+1)
                except:
                    if i == -1:
                        i=len(st)
                idx.append(i)
        midx=min(idx)
        if invert:
            midx+=len(until[idx.index(midx)])
        return (st[:midx].strip(),st[midx:].strip())


    def clean_quotes(self,*args,**kwargs):
        v=args[0]
        if isinstance(v,str):
            return v.strip(''.join(L_STR))
        elif isinstance(v,dict):
            for v2 in v:
                v[v2]=self.clean_quotes(v[v2])
            return v

    def make_rule(self,*args,**kwargs):
        clean=lambda x: str(x).replace('\\','').strip()
        line=args[0]
        line=line.split(T_SPLIT)
        rule={'facts':[],'consequences':[],'hints':[]}
        if len(line) < 2:
            raise Exception('No consequences in rule')
        if len(line) > 2:
            raise Exception('Multiple consequences in rule')
        facts=line[0]
        consequences=line[1]
        if consequences.strip() == '':
            raise Exception('Empty consequences')
        if facts.strip() == '':
            raise Exception('Empty facts')
        fact_list=facts.split(T_SEP)
        for f in fact_list:
            if f:
                try:
                    ftmp,vtmp=self.read_until(f,self.l_ops)
                except Exception as e:
                    raise e
                search_on=self.data
                fact_key=[]
                for levelkey in ftmp.split(T_CHILD):
                    for lkey in search_on.keys():
                        if lkey != levelkey and lkey.lower() == levelkey.lower():
                            levelkey=lkey
                    if T_MULTIPLE in levelkey:
                        searched_keys=[x for x in search_on.keys() if levelkey.replace(T_MULTIPLE,'') in x]
                        if searched_keys:
                            for r in searched_keys:
                                new_fact=f.replace(levelkey,r)
                                new_consequences=consequences.replace(T_REPLACE,r)
                                self.make_rule('{} -> {} '.format(new_fact,new_consequences))
                            return
                        else:
                            raise Exception('Can\'t apply template \'{}\''.format(levelkey))
                    else:
                        if levelkey not in search_on.keys():
                            raise Exception('Use of key \'{}\' not possible'.format(levelkey))
                        fact_key.append(levelkey)
                        search_on=search_on[levelkey]
                #True key
                #fact_key='.'.join(fact_key)
                #self.data_values[fact_key]=search_on
                #lower key
                self.data_values[ftmp]=search_on
                try:
                    op,vtmp=self.read_until(vtmp,self.l_ops,True)
                except:
                    raise e
                if op == '':
                    raise Exception('Missing op')
                if op not in self.l_ops:
                    raise Exception('Wrong op')
                vtmp,end=self.read_until(vtmp,self.l_ops+self.l_spliters)
                if vtmp == '' and op != T_CAPTURE:
                    raise Exception('Wrong value')
                if vtmp and op == T_CAPTURE:
                    self.data.setdefault(vtmp,search_on)
                rule['facts'].append({'key':ftmp,'op':op,'value':vtmp})
        try:
            try:
                consequences,hints=self.read_until(consequences,[T_HINT])
            except Exception as e:
                raise e
            lconsequences=[]
            end=True
            while end:
                ctmp,end=self.read_until(consequences,[T_SEP])
                lconsequences.append(clean(ctmp))

            for c in lconsequences:
                if c[0] != c[-1] and c[0] not in L_STR:
                    raise Exception('Consequences mus\'t be enclosed with quotes')
            rule['consequences']=lconsequences
            hints=hints[1:]
            try:
                lhints=[clean(h) for h in hints.split(T_SEP)]
                for h in lhints:
                    if h[0] != h[-1] and h[0] not in L_STR:
                        raise Exception('Hints mus\'t be enclosed with quotes')
                rule['hints']=lhints
            except:
                pass #hints are optional
            for k in ['facts','consequences','hints']:
                for i in range(len(rule[k])):
                    rule[k][i] = self.clean_quotes(rule[k][i])
        except Exception as e:
            raise e

        self.rules.append(rule)

    def load_ruleset(self,*args,**kwargs):
        fileruleset=kwargs.get('fileruleset',None)
        if not fileruleset:
            raise Exception('No fileruleset in kwargs')
        self.data=kwargs.get('data',None)
        if not self.data:
            raise Exception('Empty data')
        try:
            with open(fileruleset,'r') as f:
                l=0
                for line in f:
                    l+=1
                    try:
                        if not line.strip().startswith('#'):
                            self.make_rule(line)
                    except Exception as e:
                        log.error('Rule: \'{}\' : {}'.format(line,e))
                log.info('{} lines processed, {} rules loaded'.format(l,len(self.rules)))
        except:
            raise Exception('Wrong file for ruleset')

    def make_tree(self,*args,**kwargs):
        lfacts=[fact for lfacts in [rule['facts'] for rule in self.rules] for fact in lfacts]
        count_facts={}
        for fact in lfacts:
            count_facts.setdefault(fact['key'],0)
            count_facts[fact['key']]+=1
        self.keys_ordered=sorted(count_facts,key=count_facts.get,reverse=True)


    def apply_operation(self,fact):
        clean=lambda x: str(x).replace(' ','').strip()
        value=clean(fact.get('value')).lower()
        key=clean(fact.get('key'))
        op=clean(fact.get('op'))
        data_value=clean(self.data_values[key]).lower()
        ret=False
        if op == T_EQUAL:
            if value == data_value:
                ret=True
        elif op == T_NOT_EQUAL:
            if value != data_value:
                ret=True
        elif op == T_LIKE:
            if value in data_value:
                ret=True
        elif op == T_CAPTURE:
            if data_value:
                return True
        return ret


    def make_suggestion(self,*args,**kwargs):
        def make_banner(st):
            return '{}\n{}'.format(st,'-'*len(st))

        rules_match=[]
        for key in self.keys_ordered:
            for rule in self.rules:
                for fact in rule['facts']:
                    if fact.get('key') == key:
                        #print '{}'.format(fact)
                        if self.apply_operation(fact):
                            #print '{} False'.format(fact)
                            rules_match.append(rule)
                        #else:
                            #print '{} True'.format(fact)
        if rules_match:
            print make_banner('Detected:')
        for rule in rules_match:
            for c in rule['consequences']:
                key=rule['facts'][0].get('key','None')
                keyval=self.data_values.get(key,None)
                if keyval:
                    if T_REPLACE in c:
                        try:
                            for li in keyval:
                                c=c.replace(T_REPLACE,str(li))
                                print '{}!'.format(c)
                        except:
                            c=c.replace(T_REPLACE,keyval)
                            print '{}!'.format(c)
                    else:
                        print '{}!'.format(c)
            if rule['hints']:
                print ''
                print make_banner('Things that you can do:')
                for suggestion in rule['hints']:
                    print '-{}'.format(suggestion)
                print ''

