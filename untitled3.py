# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 13:58:41 2021

@author: jkuhnsman
"""

import falcon, json

class CompaniesResource(object):
  companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]
  def on_get(self, req, resp):
    resp.body = json.dumps(self.companies)

api = falcon.API()
companies_endpoint = CompaniesResource()
api.add_route('/companies', companies_endpoint)