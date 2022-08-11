# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 15:37:41 2020

@author: Filippo Ciceri
@site: www.financialdatatree.com

"""
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from lxml import etree
import datetime, os, re

def process_files(files, sort=True, names=[]):
    ##########################################
    #files = list of one or more files to convert from XBRLi to XBRL
    #sort = True/False for alphabetical sorting of the results
    #names = list of names for the converted files,
    #        if left empty the name is going to be the same used for hte XBRLI with the
    #        '.xml' extension instead of '.htm'.
    ##########################################
    
    print('Converting iXBRL into XBRL...')
    
    for filename in files:
        if os.path.getsize(filename)>10000000:
            big_file = True
        else:
            big_file = False

        if big_file == True:
            with open(filename,'r') as file_:
                text = file_.read()
                if 'html' in text:
                    text = text.split('<html')[1].split('>')[0]
            text = text.replace('"','').split(' ')
            attribs_html_node = [x.split('=',1) for x in text]
            ns = {x[0]:x[1] for x in attribs_html_node if len(x)!=1}
            non_numerics = []
            non_fractionals = []
            date_line = None
            fiscal_year_focus = None
            context_refs = []
            units = []

            next_line = False
            continuation = None
            
            try:
                for event, element in ET.iterparse(filename,events=('start','end')):
                    pass
                integrity = True
            except:
                integrity = False
                print('Error parsing the file!')
                with open('./temp/temp.xml','w') as f:
                    f.write('')
                return

            if integrity == True:
                for event, element in ET.iterparse(filename,events=('start','end')):
                    if (('nonnumeric' in element.tag.lower()) or \
                        ('nonfraction' in element.tag.lower())) and (event=='end'):
                        if '}' in element.tag:
                            tag = 'ix:' + element.tag.split('}')[1]
                        else:
                            tag = element.tag
                        attributes = ' '.join([k+'="'+v+'"' for k,v in element.attrib.items()])
                        if len([x for x in element.itertext()]) !=0:
                            values = " ".join([x for x in element.itertext()])
                        else:
                            values = ''
                        values = values.rstrip().lstrip().replace('\n',' ').replace('\t',' ')
                        values = re.sub(' +',' ',values)
                        if element.getchildren() != []:
                            if 'divide' in element.getchildren()[0].tag:
                                values = values.replace(' ',"/")
                        string_node = '<' + tag + ' ' + attributes + '>' + values + '</' + tag + '>'
                        string_node = string_node.replace('ns0','ix').replace('\n','').replace('\t','')
                        bs_object = BeautifulSoup(string_node,'lxml').find(tag.lower())
                        if 'name' in element.attrib.keys():
                            if element.attrib['name'] == 'dei:DocumentPeriodEndDate' and date_line == None:
                                date_line = bs_object
                                next_line = True
                        if 'nonnumeric' in element.tag.lower():
                            non_numerics.append(bs_object)
                        if 'nonfraction' in element.tag.lower():
                            non_fractionals.append(bs_object)
                    elif (('context' in element.tag.lower()) or \
                          ('unit' in element.tag.lower())) and (event=='end'):
                        if '}' in element.tag:
                            tag = 'ix:' + element.tag.split('}')[1]
                        else:
                            tag = element.tag

                        string_node = ET.tostring(element, encoding='utf8', method='xml')
                        string_node = string_node.decode().replace('ns0','ix').replace('ns1','ix')
                        string_node = re.sub(' +',' ',string_node)
                        bs_object = BeautifulSoup(string_node,'lxml').find(tag.lower())
                        context_refs.append(bs_object)
                    elif next_line == True:
                        if 'continuation' in element.tag.lower():
                            if '}' in element.tag:
                                tag = 'ix:' + element.tag.split('}')[1]
                            else:
                                tag = element.tag
                            attributes = ' '.join([k+'="'+v+'"' for k,v in element.attrib.items()])
                            if len([x for x in element.itertext()]) !=0:
                                values = " ".join([x for x in element.itertext()])
                            else:
                                values = ''
                            values = values.rstrip().lstrip().replace('\n',' ').replace('\t',' ')
                            values = re.sub(' +',' ',values)
                            string_node = '<' + tag + ' ' + attributes + '>' + values + '</' + tag + '>'
                            string_node = string_node.replace('ns0','ix').replace('\n','').replace('\t','')
                            continuation = BeautifulSoup(string_node,'lxml').find(tag.lower())
                            next_line = False

                    if (('nonnumeric' in element.tag.lower()) or \
                       ('nonfraction' in element.tag.lower()) or \
                       ('unit' in element.tag.lower()) or \
                       ('div' in element.tag.lower())) and (event=='end'):
                        element.clear()
                    
        else:

            with open(filename,'r') as file_:
                if file_.read().startswith('\ufeff'):
                    has_BOM = True
                else:
                    has_BOM = False
            if has_BOM == True:
                with open(filename,'r',encoding='utf-8-sig') as file_:
                    soup = BeautifulSoup(file_, 'lxml')
            else:
                with open(filename,'r',encoding='utf-8') as file_:
                    soup = BeautifulSoup(file_, 'lxml')
            if soup.find('html') == None:
                if has_BOM == True:
                    with open(filename,'r',encoding='utf-8-sig') as file:
                        soup = BeautifulSoup(file_, 'html.parser')
                else:
                    with open(filename,'r',encoding='utf-8') as file:
                        soup = BeautifulSoup(file_, 'html.parser')
            ns = soup.find('html').attrs
            non_numerics = soup.find_all('ix:nonnumeric',recursive=True,text=True)
            non_fractionals = soup.find_all('ix:nonfraction',recursive=True,text=True)
            context_refs = soup.find_all('xbrli:context',text=False)
            if len(context_refs)==0:
                context_refs = soup.find_all('i:context',text=False)
            if len(context_refs)==0:
                context_refs = soup.find_all('context',text=False)
            units = soup.find_all('xbrli:unit',text=False)
            if len(units)==0:
                units = soup.find_all('i:unit',text=False)
            if len(units)==0:
                units = soup.find_all('unit',text=False)
                
            date_line = soup.find(attrs={'name':'dei:DocumentPeriodEndDate'})
            continuation = None
            fiscal_year_focus = soup.find(attrs={'name':'dei:DocumentFiscalYearFocus'})

                    
        lines = []
        date = False
        ns = {k:v.replace('\n','') for (k,v) in ns.items()}

        if 'xmlns:xbrli' not in ns.keys():
            ns['xmlns:xbrli'] = 'http://www.xbrl.org/2003/instance'

        first_line = '<xbrl ' + ' '.join([str(k)+'="'+str(v)+'"' for k,v in ns.items()]) + '>'
   
        for nn in non_numerics:
            name = nn['name']
            #value = nn.text.replace(' ','').replace(',','')
            value = nn.text.replace(',','')
            value = value.lstrip().rstrip()
            value = re.sub('( )+',' ',value)
            value = value.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            if name == 'dei:DocumentPeriodEndDate':
                value = value.replace(' ','')
                date = True
                bad_formats = ['%d','%b','%B','%m','%y','%Y','%b%d','%B%d']
                continue_ = False
                
                corrections = {'febuary':'february',
                               'Febuary':'February'}
                for k,v in corrections.items():
                    value = value.replace(k,v)
                
                for fmt in bad_formats:
                    try:
                        datetime.datetime.strptime(value.replace('\xa0',''),fmt)
                        continue_ = True
                    except ValueError:
                        pass
                
                if re.match('^[a-zA-Z]+[0-9]{4}$',value) != None:
                    continue_ = True

                if continue_ == False:
                    value = value.replace('\xa0',' ').replace(' ','').replace(',','').replace('-','')
                    for fmt in ['%B%d%Y','%b%d%Y','%Y%B%d','%Y%b%d','%m/%d/%Y','%Y/%m/%d','%d%b%Y','%d%B%Y']:
                        try:
                            value = datetime.datetime.strptime(value,fmt).strftime('%Y-%m-%d')
                        except:
                            pass

                to_be_removed = ['For the quarterly period ended:\xa0\xa0\xa0',
                                 'For the quarterly period ended ',
                                 'For the fiscal year ended ',
                                 'For the fiscal year ended: ',
                                 'For the Fiscal Year Ended ',
                                 'For the Quarterly Period Ended ',
                                 'For the quarterly period ended',
                                 '\xa02020','\xa0',
                                 ':',' ','.',',']
               
                if continue_ == True:
                    text = nn.parent.parent.parent.text
                    for substring in to_be_removed:
                        text = text.replace(substring,'')
                    for k,v in corrections.items():
                        text = text.replace(k,v)
                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass
                

                if continue_ == True:
                    text = nn.parent.parent.text
                    for substring in to_be_removed:
                        text = text.replace(substring,'')
                    for k,v in corrections.items():
                        text = text.replace(k,v)
                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass

                if continue_ == True:
                    text = nn.parent.text
                    for substring in to_be_removed:
                        text = text.replace(substring,'')
                    for k,v in corrections.items():
                        text = text.replace(k,v)
                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass

                if continue_ == True and text.isdigit():
                    for nn in non_numerics:
                        if nn['name']=='dei:CurrentFiscalYearEndDate':
                            if nn.text != '':
                                text = nn.text + text
                                break
                    for substring in to_be_removed:
                        text = text.replace(substring,'')
                    for k,v in corrections.items():
                        text = text.replace(k,v)
                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass

                if continue_ == True:
                    if continuation != None:
                        if continuation.text.isdigit() == True:
                            text = text + continuation.text.replace(',','').replace(' ','')
                        else:
                            for nn in non_numerics:
                                if nn['name']=='dei:DocumentFiscalYearFocus':
                                    if nn.text != '':
                                        text = text + nn.text
                                        break
                    elif fiscal_year_focus != None:
                        text = text + fiscal_year_focus.text.replace(',','').replace(' ','')
                    for substring in to_be_removed:
                        text = text.replace(substring,'')
                    for k,v in corrections.items():
                        text = text.replace(k,v)
                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass

                if continue_ == True:
                    if re.match('^[a-zA-Z]+[0-9]{4}$',value) != None:
                        value = re.sub('(?=[0-9]{2}$)','20',value)

                    for fmt in ('%B%d%Y', '%b%d%Y', '%d%B%Y', '%d%b%Y'):
                        try:
                            value = datetime.datetime.strptime(text.replace('\xa0',' ')
                                                                   .replace(' ','')
                                                                   .replace(',',''),fmt).strftime('%Y-%m-%d')
                            continue_ = False
                        except ValueError:
                            pass

            attrs = {}
            for attr in nn.attrs.keys():
                attrs[attr] = nn[attr]
            if 'contextref' not in nn.attrs.keys():
                attrs['contextref'] = None
            if 'sign' in attrs.keys():
                if attrs['sign'] == '-':
                    attrs['sign'] = -1
                else:
                    attrs['sign'] = +1
            line = '<' + name.replace(' ','') + ' '
            line += ' '.join([str(k)+'="'+str(v)+'"' for k,v in attrs.items() if v!=None and \
                                                                                 k!='id']) + '>'
            line += value
            line += '</' + name.replace(' ','') + '>'
            lines.append(line.replace('contextref','contextRef')
                             .replace('unitref','unitRef'))
        
        for nf in non_fractionals:
            name = nf['name']
            value = nf.text.replace(',','')
            if value.replace('.','').isdigit():
                if '..' in value:
                    value = value.replace('..','.')
                if re.match("([0-9]+)\.([0-9]+)\.([0-9]+)", value):
                    value = value.replace(".","")
                value = float(value)
            else:
                continue
            attrs = {}
            if 'scale' not in nf.attrs.keys():
                multiplier = 0
            elif nf['scale'] == 'no':
                multiplier = 0
            else:
                multiplier = int(nf['scale'])
            for attr in nf.attrs.keys():
                attrs[attr] = nf[attr]
            for x in ['contextref','unitref','sign','format']:
                if x not in nf.attrs.keys():
                    attrs[x] = None
            if 'sign' in attrs.keys():
                if attrs['sign'] == '-':
                    attrs['sign'] = -1
                else:
                    attrs['sign'] = +1
            line = '<' + name.replace(' ','') + ' '
            line += ' '.join([str(k)+'="'+str(v)+'"' for k,v in attrs.items() if v!=None and \
                                                                                 k!='id']) + '>'
            try:
                line += str(attrs['sign']*value*(10**multiplier))
            except:
                import pdb;pdb.set_trace()
            line += '</' + name.replace(' ','') + '>'
            if value != '-' and value != '' and value != '—':
                lines.append(line.replace('contextref','contextRef')
                                 .replace('unitref','unitRef'))
        
        lines = list(set(lines))
        if sort==True:
            lines = sorted(lines)
        
        lines = [first_line] + lines
        
        context_refs_list = []

        for cf in context_refs:
            if 'id' in [x for x in cf.attrs.keys()]:
                context_refs_list.append(cf['id'])
            lines.append(str(cf).replace('startdate','startDate')
                                .replace('enddate','endDate'))

        for unit in units:
            lines.append(str(unit))

        for i in range(0,len(lines)):

            lines[i] = lines[i].replace('<i:','<xbrli:').replace('</i:','</xbrli:')
            lines[i] = lines[i].replace('<ix:','<xbrli:').replace('</ix:','</xbrli:')

            lines[i] = lines[i].replace('<context','<xbrli:context').replace('</context','</xbrli:context')
            lines[i] = lines[i].replace('<entity','<xbrli:entity').replace('</entity','</xbrli:entity')
            lines[i] = lines[i].replace('<segment','<xbrli:segment').replace('</segment','</xbrli:segment')
            lines[i] = lines[i].replace('<period','<xbrli:period').replace('</period','</xbrli:period')
            lines[i] = lines[i].replace('<instant','<xbrli:instant').replace('</instant','</xbrli:instant')
            lines[i] = lines[i].replace('<unit ','<xbrli:unit ').replace('</unit>','</xbrli:unit>')
            lines[i] = lines[i].replace('<startdate','<xbrli:startDate').replace('</startdate','</xbrli:startDate')
            lines[i] = lines[i].replace('<startDate','<xbrli:startDate').replace('</startDate','</xbrli:startDate')
            lines[i] = lines[i].replace('<endDate','<xbrli:endDate').replace('</endDate','</xbrli:endDate')
            lines[i] = lines[i].replace('<enddate','<xbrli:endDate').replace('</enddate','</xbrli:endDate')

            lines[i] = lines[i].replace('unitref=','unitRef=')
            lines[i] = lines[i].replace('startdate','startDate').replace('enddate','endDate')

            lines[i] = re.sub('[a-zA-Z]style=',' style=',lines[i])
            if 'contextRef' not in lines[i]:
                lines[i] = re.sub('(?<=(<br))(?!( ))(?!(c:))',' ',lines[i])
                lines[i] = re.sub('(?<=(<t))(?=( ))','d',lines[i])
                lines[i] = re.sub('(?<=(<su))(?=( ))','p',lines[i])
                lines[i] = re.sub('(?<=(<td))(?!( ))(?!([a-z]{1,2}:))',' ',lines[i])
            lines[i] = re.sub('(?<=(<td))(?!(:))(?!([a-z]{1,2}:))',' ',lines[i])
            lines[i] = re.sub('(?<=(<t))(?=( ([a-z]+)(=")))','d',lines[i])
            lines[i] = re.sub('(?<=(<su))(?=( ([a-z]+)(=")))','p',lines[i])
            lines[i] = lines[i].replace('brclear=','br clear=')
            
            lines[i] = lines[i].replace('<xbrli:explicitmember','<xbrldi:explicitMember').replace('</xbrli:explicitmember','</xbrldi:explicitMember')
            lines[i] = lines[i].replace('<xbrli:explicitMember','<xbrldi:explicitMember').replace('</xbrli:explicitMember','</xbrldi:explicitMember')
            lines[i] = lines[i].replace('<xbrldi:explicitmember','<xbrldi:explicitMember').replace('</xbrldi:explicitmember','</xbrldi:explicitMember')
            lines[i] = lines[i].replace('<explicitmember','<xbrldi:explicitMember').replace('</explicitmember','</xbrldi:explicitMember')
            lines[i] = lines[i].replace('<explicitMember','<xbrldi:explicitMember').replace('</explicitMember','</xbrldi:explicitMember')
            lines[i] = lines[i].replace('<fon ','<font ').replace('<di ','<div ').replace('<tablecell','<table cell')
            lines[i] = re.sub('(?<=")(?<!(="))',' ',lines[i])

            lines[i] = lines[i].replace('<spandata-hint="','')
            lines[i] = lines[i].replace('<br>','')

            if re.search('(?<=\\<)[a-zA-Z]+(?=\\:)',lines[i]) != None:
                tag_text = re.search('(?<=\\<)[a-zA-Z]+(?=\\:)',lines[i]).group(0)
                if tag_text.isupper():
                    lines[i] = re.sub('((?<=(<))|(?<=(/)))[a-zA-Z]+:(?=([a-zA-Z]))',tag_text.lower(),lines[i])

        if date == False:
            name = 'dei:DocumentPeriodEndDate'
            if date_line!=None:
                value = date_line.text.replace('&','_amp_')
                attrs = {}
                for attr in date_line.attrs.keys():
                    attrs[attr] = date_line[attr]
                    if 'contextref' not in nn.attrs.keys():
                        attrs['contextref'] = None
                line = '<' + name + ' '
                line += ' '.join([str(k)+'="'+str(v)+'"' for k,v in attrs.items() if v!=None and k!='id']) + '>'
                line += value
                line += '</' + name + '>'
                lines.append(line.replace('contextref','contextRef').replace('unitref','unitRef'))

        lines.append('</xbrl>')
        
        if names == []:
            new_filename = filename.replace('.htm','.xml').replace('.htm','.xml')
        else:
            new_filename = names[files.index(filename)]
        with open(new_filename, 'w', encoding="utf-8") as output:
            for l in lines:
                search_result = re.search('(?<=(contextRef="))[a-zA-Z0-9_]+(?=(" ))',l)
                if search_result == None:
                    output.write(l + '\n')
                else:
                    context = search_result.group(0)
                    if context in context_refs_list:
                        output.write(l + '\n')
                
if __name__ == "__main__":
    process_files(files, sort=True, names=[])
