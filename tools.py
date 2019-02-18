# -*- coding: utf-8 -*-
import tldextract
import socket
import csv

class tools():


    def extract_domain(self,s,verbose=False,include_suffix=False):

        s = s.replace('http://','')
        s = s.replace('https://','')
        s = s.replace('www.','')

        extracted = tldextract.extract(s)
        extracted_domain = extracted.subdomain+"."+extracted.domain

        if extracted_domain[0] == ".":
          extracted_domain = extracted_domain[1:]

        if include_suffix:
          extracted_domain +="." + extracted.suffix

        return extracted_domain


    def parse_domain(self,s,include_ip=False,include_suffix=False):

        ret = {
          'parsed_domain':"",
          'ip': None,
          'subdomain': "",
          'suffix':"",
          'scheme':"",
          'domain':"",
          'slug': None,
          'url': s
        }
        if 'http://' in s:
          s = s.replace('http://','')
          ret['scheme'] = 'http://'
        elif 'https://' in s:
          s = s.replace('https://','')
          ret['scheme'] = 'https://'

        s = s.replace('www.','')

        extracted = tldextract.extract(s)

        ret['parsed_domain'] = extracted.subdomain+"."+extracted.domain
        ret['subdomain']  = extracted.subdomain
        ret['suffix'] = extracted.suffix
        ret['domain'] = extracted.domain
        slug = s.split(extracted.domain+ "." + extracted.suffix)
        if len(slug) > 1:
          ret['slug'] = slug[1]


        if ret['parsed_domain'][0] == ".":
          ret['parsed_domain']  = ret['parsed_domain'][1:]

        if include_ip:
          try:
            ret['ip'] = socket.gethostbyname(ret['parsed_domain']+ "." + extracted.suffix)
          except:
            ret['ip'] = None

        if include_suffix:
          ret['parsed_domain'] +="." + extracted.suffix

        return ret


    def split_domain(self,s):

      extracted = tldextract.extract(s)


      extracted_domain = extracted.subdomain+"."+extracted.domain + "." + extracted.suffix

      try:
        ip = socket.gethostbyname(extracted_domain)
      except:
        ip = None

      s = s.replace('http://','')
      s = s.replace('https://','')
      s = s.replace('www.','')

      extracted = tldextract.extract(s)
      extracted_domain = extracted.subdomain+"."+extracted.domain
      extracted_slug = s.split(extracted.domain + "." + extracted.suffix)[-1]

      if extracted_domain[0] == ".":
        extracted_domain = extracted_domain[1:]

      return extracted_domain, extracted_slug, ip


    def export_vector_csv(self,filename,vector):
      with open(filename+".csv",'wb') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        for key,value in vector.iteritems():
          wr.writerow([key,value])





