#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
# Written by Alan Viars - This software is public domain

import sys
import os
import sys
import string
import json
import csv
import pprint
from datetime import datetime
from pymongo import MongoClient
from collections import OrderedDict
from more_itertools import unique_everseen


MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017


def make_pecos_nppes_fhir_docs(database_name="pecos_nppes"):

    i = 0
    try:

        mc = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        db = mc[database_name]
        fhir_practitioner = db['fhir_practitioner']
        addresses = db['addresses']
        base_pecos = db['base']
        compiled_individuals_collection = db['compiled_individuals']

        for bdoc in nppes_practitioner.find():
            #Counter for display
            try:
                i += 1
        # ----------------------------------------------------
        # INCORPORATE ADDRESSES and other ID's
        # ----------------------------------------------------
                match_bases = base_pecos.find({'NPI': bdoc['identifier'][0]['value']})
                m_addresses = []
                identifiers = []
                for matches in match_bases:
                    match_addresses = addresses.find({'ENRLMT_ID': matches['ENRLMT_ID']})
                    for ma in match_addresses:
                        # Create fhir address from pecos addresses
                        address = OrderedDict()
                        address['use'] = 'work'
                        address['postalCode'] = ma['ZIP_CD']
                        address['city'] = ma['CITY_NAME']
                        address['country'] = 'USA'
                        address['state'] = ma['STATE_CD']
                        # I don't think that text is exactly meant for this purpose, but
                        # we're using it here for now.
                        address['text'] = 'PECOS data practice location'
                        # Append address and remove duplicates
                        if address not in m_addresses:
                            m_addresses.append(address)

                    # Other Identifiers: ENRLMT_ID, PECOS_ASCT_CNTL_ID
                    enrlmt_id = OrderedDict()
                    enrlmt_id['use'] = 'official'
                    enrlmt_id_cc = OrderedDict()
                    enrlmt_id_cc['text'] = 'Enrollment ID in PECOS basic data set'
                    enrlmt_id['type'] = enrlmt_id_cc
                    enrlmt_id['system'] = 'https://data.cms.gov/public-provider-enrollment'
                    enrlmt_id['value'] = matches['ENRLMT_ID']
                    if enrlmt_id not in identifiers:
                        identifiers.append(enrlmt_id)

                    # PECOS_ASCT_CNTL_ID
                    pecosAsctCntlId = OrderedDict()
                    pecosAsctCntlId['use'] = 'official'
                    pecosAsctCntlId_cc = OrderedDict()
                    pecosAsctCntlId_cc['text'] = 'PECOS_ASCT_CNTL_ID in PECOS basic data set'
                    pecosAsctCntlId['type'] = pecosAsctCntlId_cc
                    pecosAsctCntlId['system'] = 'https://data.cms.gov/public-provider-enrollment'
                    pecosAsctCntlId['value'] = matches['PECOS_ASCT_CNTL_ID']
                    if pecosAsctCntlId not in identifiers:
                        identifiers.append(pecosAsctCntlId)
        # --------------------------------------------------------------
        # INCORPORATE AFFILIATIONS
        # --------------------------------------------------------------
                # Match up npi numbers between pecos and nppes
                match_compiled_individuals = compiled_individuals_collection.find(
                    {'NPI': bdoc['identifier'][0]['value']})
                extensions = []
                for mci in match_compiled_individuals:
                    # Create Codings
                    npi_coding = OrderedDict()
                    npi_coding['system'] = 'https://nppes.cms.hhs.gov/NPPES/Welcome.do'
                    npi_coding['code'] = mci['works_for'][0]['NPI']
                    npi_coding['display'] = 'NPI number of affiliation'
                    # Leaving off the 'userSelected' category for now.

                    enrollmentid_coding = OrderedDict()
                    enrollmentid_coding['system'] = 'https://data.cms.gov/public-provider-enrollment'
                    enrollmentid_coding['code'] = mci['works_for'][0]['ENRLMT_ID']
                    enrollmentid_coding['display'] = 'PECOS Enrollment ID of affiliation'

                    # Create Codeable concept
                    value_codeable_concept = OrderedDict()
                    value_codeable_concept['coding'] = [npi_coding, enrollmentid_coding]
                    value_codeable_concept['text'] = mci['works_for'][0]['NAME'] + ', ' + mci['works_for'][0]['DESCRIPTION']

                    # Create fhir affiliation from compiled_individuals
                    affiliation = OrderedDict()
                    affiliation['url'] = 'https://data.cms.gov/public-provider-enrollment'
                    # print(value_codeable_concept['text'])
                    affiliation['valueCodeableConcept'] = value_codeable_concept
                    # wrap in list, and remove duplicates
                    if affiliation not in extensions:
                        extensions.append(affiliation)



                fhir_practitioner.update_one(bdoc, {"$pushAll": {"extension": extensions, "address": m_addresses, "identifier": identifiers}}, upsert=True)
                # if d['resourceType'] == "Organization":
                #     compiled_organizations_collection.insert(d)
                # elif d['resourceType'] == "Practitioner":
                #     compiled_individuals_collection.insert(d)

                # print json.dumps(d, indent =4)
            except:
                print(sys.exc_info)
        # Walk through base

    except:
        print(sys.exc_info())

    print(i, "Processed")


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Usage:")
        print("make_pecos_nppes_fhir_docs.py")
        sys.exit(1)

    # Run it
    make_pecos_nppes_fhir_docs()
