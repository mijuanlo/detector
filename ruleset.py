#!/usr/bin/env python
from utils.log import log
import re
log.debug("File "+__name__+" loaded")

T_COMMENT='#'
T_SEP=','
T_SPLIT='->'
T_HINT='?'
T_CHILD='.'
T_EQUAL='='
T_NOT='!'
T_GT='<'
T_LT='>'
T_CONTAIN='%'
L_STR=['\'','"']
L_EMPTY=['\t',' ']

class ruleset:
    def __init__(self):
        self.l_spliters=[T_COMMENT,T_SEP,T_SPLIT,T_HINT]
        self.l_ops=[T_EQUAL,T_NOT]
        self.rules=[]
        self.data=None
        pass

    def read_until(self,str,until,invert=False,*args,**kwargs):
        i=0
        ret=''
        skip_search=False
        skip_single=False
        for ch in str:
            if skip_single:
                skip_single=False
                i+=1
                ret+=ch
                continue

            if ch in L_EMPTY:
                i+=1
                ret+=ch
                continue

            if ch == '\\':
                skip_single=True
                ret+=ch
                i+=1
                continue

            if ch in L_STR:
                if not skip_search:
                    skip_character=ch
                if ch == skip_character:
                    skip_search=not skip_search
                i+=1
                ret+=ch
                continue

            if not skip_search:
                if not invert:
                    if ch not in until:
                        i+=1
                        ret+=ch
                    else:
                        break
                else:
                    if ch in until:
                        i+=1
                        ret+=ch
                    else:
                        break
            else:
                i+=1
                ret+=ch
        if skip_search:
            raise Exception('Unbalanced quotes')
        return (ret.strip(),str[i:].strip())

    def clean_quotes(self,*args,**kwargs):
        v=args[0]
        if isinstance(v,str):
            return v.strip(''.join(L_STR))
        elif isinstance(v,dict):
            for v2 in v:
                v[v2]=self.clean_quotes(v[v2])
            return v

    def make_rule(self,*args,**kwargs):
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
                    if levelkey.lower() not in make_lower_keys(search_on):
                        raise Exception('Use of key \'{}\' not possible',format(levelkey))
                    else:
                        search_on=search_on[levelkey]
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
                lconsequences.append(ctmp)

            for c in lconsequences:
                if c[0] != c[-1] and c[0] not in L_STR:
                    raise Exception('Consequences mus\'t be enclosed with quotes')
            rule['consequences']=lconsequences
            hints=hints[1:]
            try:
                lhints=hints.split(T_SEP)
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

    def make_suggestion(self,*args,**kwargs):
        print 'this is a suggestion'