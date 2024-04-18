# Calls the Cashless_Reimbursement_Overlap API and integrates the result into a collection of API's to be called by the main API to display the result on SFDC.

import pandas as pd
from fastapi import APIRouter
from util.util import fetch_mongo_data
from util.util import gpt_data
from util.API import cashless_reimbursement_overlap_api
import os
import traceback

cashless_reimbursement_overlap_router = APIRouter()
@cashless_reimbursement_overlap_router.post('/Cashless_Reimbursement_Overlap')
def cashless_reimbursement_overlap(body: dict):
    case_number = body.get('CaseNumber', '')
    res_flags = {
        'doctor' : '',
        'provider' : '',
        'HAN' : '',
        'Bill Amount' : '',
        'API' : {},
        'Result' : 'Pass'
        }

    required_fields = ['CaseNumber','invoice','Mobile','HAN__c','Bill_Amount__c','CreatedDate','Date_of_Consultation__c','BH_Attribute_Name__c']
    case = fetch_mongo_data(case_number,required_fields )

    res_flags['HAN'] = case['HAN__c']
    res_flags['Bill Amount'] = case['Bill_Amount__c']
    try:
        doctors = gpt_data(case['invoice'], 'doctor')
        doctor = list(set([i for i in doctors if i not in ['not found', 'Not Found', 'Not found', 'MISSING', 'missing', '']]))
        res_flags['doctor'] = doctor[0] if len(doctor)>0 else ''
        providers = gpt_data(case['invoice'], 'provider')
        provider = list(set([i for i in providers if i not in ['not found', 'Not Found', 'Not found', 'MISSING', 'missing', '']]))
        res_flags['provider'] = provider[0] if len(provider)>0 else ''

    except Exception as e:
        #print(e)
        pass

    try:
        res_flags['API'] = cashless_reimbursement_overlap_api(case, res_flags['doctor'], res_flags['doctor'])
        api_results = res_flags.get('API', [])
        max_result_dict = max(api_results, key=lambda x: len(str(x.get('result', '')))).get('result', '')
        res_flags['API'] = {'result': max_result_dict}

        if res_flags['API']['result'] == 'No Match':
            res_flags['Result'] = 'Pass'
        else:
            for appointment_id in list(res_flags['API']['result'].keys()):
                temp = {
                    'AppointmentDate' : res_flags['API']['result'][appointment_id]['AppointmentDate'],
                    'Overlap' : res_flags['API']['result'][appointment_id]['Overlap'],
                    'Matches' : res_flags['API']['result'][appointment_id]['Matches'],
                    'claimid' : res_flags['API']['result'][appointment_id]['ClaimID'],
                    'DoctorProviderName' : res_flags['API']['result'][appointment_id]['DoctorProviderName'],
                    'Matches' : res_flags["API"]['result'][appointment_id]['Matches'],
                    'Amount' : res_flags["API"]['result'][appointment_id]['PaidAmount'],
                    'Dateplus30' : res_flags["API"]['result'][appointment_id]['AppointmentDatePlus30'],
                    'ProviderName' : res_flags["API"]['result'][appointment_id]['ProviderName']
                }
                if res_flags['API']['result'][appointment_id]['Overlap'] == True:
                    res_flags['Result'] = 'Fail'
                res_flags['API']['result'][appointment_id] = temp
    except Exception as e:
        #print(e)
        print(traceback.print_exc())
        res_flags['Result'] = 'MISSING'
    return log_cashless_reimbursement_overlap(res_flags)


def log_cashless_reimbursement_overlap(flags):
    res = {
        'Agent_String': 'No Overlapping Cashless Claim Found',
        'Standard_String': 'No Cashless Claims Found',
        'Details': flags.copy(),
        'Result': 'False'
    }
    res['Details'].pop('Result')
    if flags['Result'].lower() == 'missing':
        res['Standard_String'] = 'Function Did not Run'
    elif flags['Result'] == 'Fail':
        for appointment_id, appointment_data in flags['API']['result'].items():
            if appointment_data['Overlap']:
                if appointment_data['Matches'] == 'Overlap on Dates': 
                    tooltip_content = f"Match on Appointment date &#013 Doctor: {appointment_data['DoctorProviderName']}&#013 Provider:{appointment_data['ProviderName']}&#013 Amount: {appointment_data['Amount']}&#013 Matched Date: {appointment_data['AppointmentDate']}&#013"
                elif appointment_data['Matches'] == 'Overlap on Amount':
                    tooltip_content = f"Match on amount &#013 Doctor: {appointment_data['DoctorProviderName']}&#013 Provider:{appointment_data['ProviderName']}&#013 Matched Amount: {appointment_data['Amount']}&#013 Date: {appointment_data['AppointmentDate']}&#013"
                elif appointment_data['Matches'] == 'Overlap on both Amount and Dates':
                    tooltip_content = f"Match on amount and date &#013 Doctor: {appointment_data['DoctorProviderName']}&#013 Provider:{appointment_data['ProviderName']}&#013 Matched Amount: {appointment_data['Amount']}&#013 Matched Date: {appointment_data['AppointmentDate']}&#013"
                elif appointment_data['Matches'] == 'Overlap on Plus 30 Days':
                    tooltip_content = f"Match on Appointment date within 30 days &#013 Doctor: {appointment_data['DoctorProviderName']}&#013 Provider:{appointment_data['ProviderName']}&#013 Amount: {appointment_data['Amount']}&#013 Matched Date: {appointment_data['Dateplus30']}&#013"
                elif appointment_data['Matches'] == 'Overlap on Amount and Plus 30 Days':
                    tooltip_content = f"Match on amount and appointment date within 30 days &#013 Doctor: {appointment_data['DoctorProviderName']}&#013 Provider:{appointment_data['ProviderName']}&#013 Matched Amount: {appointment_data['Amount']}&#013 Matched Date: {appointment_data['Dateplus30']}&#013"

                res['Agent_String'] = f"Overlapping Cashless Claim Found for Appointment ID: <a href='https://healthrx.lightning.force.com/lightning/r/vlocity_ins__ClaimLineItem__c/{appointment_data['claimid']}/view' target='_blank' title='{tooltip_content}'>{appointment_id}</a>"
                res['Standard_String'] = "Overlapping Cashless Claims Found"
                res['Result'] = 'True' 
                break
    return res