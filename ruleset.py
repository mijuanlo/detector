#!/usr/bin/env python
from utils.log import log
import re
log.debug("File "+__name__+" loaded")

T_COMMENT='#'
T_MULTIPLE='*'
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
        self.l_ops=[T_EQUAL,T_NOT_EQUAL]
        self.l_template=[T_MULTIPLE,T_REPLACE]
        self.rules=[]
        self.data=None
        self.data_values={}
        pass

    def read_until(self,str,until,invert=False,*args,**kwargs):
        i=-1
        str=str+' '*10
        skip_search=False
        skip_single=False
        for ch in str:
            i+=1
            if skip_single:
                skip_single=False
                continue

            if ch in L_EMPTY:
                continue

            if ch == '\\':
                skip_single=True
                continue

            if ch in L_STR:
                if not skip_search:
                    skip_character=ch
                    skip_search=not skip_search
                else:
                    if ch == skip_character:
                        skip_search=not skip_search
                continue

            if not skip_search:
                match = [u for u in until if str[i:i+len(u)] == u]
                if match:
                    match=True
                else:
                    match=False
                if match != invert:
                    break
        if skip_search:
            raise Exception('Unbalanced quotes')

        return (str[:i].strip(),str[i:].strip())

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
        make_lower_keys = lambda d: map(lambda y : y.lower(), d.keys())
        for f in fact_list:
            if f:
                try:
                    ftmp,vtmp=self.read_until(f,self.l_ops)
                except Exception as e:
                    raise e
                search_on=self.data
                for levelkey in ftmp.split(T_CHILD):
                    lkeys=make_lower_keys(search_on)
                    if T_MULTIPLE in levelkey:
                        searched_keys=[x for x in lkeys if levelkey.replace(T_MULTIPLE,'') in x]
                        if searched_keys:
                            for r in searched_keys:
                                new_fact=f.replace(levelkey,r)
                                new_consequences=consequences.replace(T_REPLACE,r)
                                self.make_rule('{} -> {} '.format(new_fact,new_consequences))
                            return
                        else:
                            raise Exception('Can\'t apply template \'{}\''.format(levelkey))
                    else:
                        if levelkey.lower() not in lkeys:
                            raise Exception('Use of key \'{}\' not possible'.format(levelkey))
                        else:
                            search_on=search_on[levelkey]

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
                if vtmp == '':
                    raise Exception('Wrong value')
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
                print '{}!'.format(c)
            if rule['hints']:
                print ''
                print make_banner('Things that you can do:')
                for suggestion in rule['hints']:
                    print '-{}'.format(suggestion)
                print ''

