from django.http import HttpRequest
from search.models import Search, Field, Code, ChronologicCode
from SolrClient import SolrResponse
from datetime import datetime
import pytz


def plugin_api_version():
    return 1.0


def pre_search_solr_query(context: dict, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    return context, solr_query


def post_search_solr_query(context: dict, solr_response: SolrResponse, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    return context, solr_response


def pre_record_solr_query(context: dict, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    return context, solr_query


def post_record_solr_query(context: dict, solr_response: SolrResponse, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    return context, solr_response


def pre_export_solr_query(solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list):
    return solr_query


def post_export_solr_query(solr_response: SolrResponse, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list):
    return solr_response


def pre_mlt_solr_query(context: dict, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, record_is: str):
    return context, solr_query


def post_mlt_solr_query(context: dict, solr_response: SolrResponse, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, record_ids: str):
    return context, solr_response


def filter_csv_record(csv_record,search: Search, fields: dict, codes: dict, format: str):
    return True,  csv_record


def load_csv_record(csv_record: dict, solr_record: dict, search: Search, fields: dict, codes: dict, format: str):
    local_tz = "US/Eastern"
    start_date = datetime.strptime(csv_record['start_date'], '%Y-%m-%d').replace(tzinfo=pytz.timezone(local_tz))
    solr_record['year'] = start_date.strftime('%Y')
    solr_record['month'] = start_date.strftime('%m')
    field = Field.objects.get(field_id='month', search_id=search.search_id)
    solr_record['month_en'] = Code.objects.get(field_id_id=field.id, code_id=solr_record['month']).label_en
    solr_record['month_fr'] = Code.objects.get(field_id_id=field.id, code_id=solr_record['month']).label_fr
    field = Field.objects.get(field_id='minister', search_id=search.search_id)
    if csv_record['minister']:
        code = Code.objects.get(field_id_id=field.id, code_id=csv_record['minister'])
        ccodes = ChronologicCode.objects.filter(code_id_id__exact=code.id).filter(
            start_date__lte=start_date).filter(end_date__gte=start_date)
        if len(ccodes) > 0:
            ccode: ChronologicCode = ccodes[0]
            solr_record['minister_name_en'] = ccode.label_en
            solr_record['minister_name_fr'] = ccode.label_fr
        else:
            # Try matching by year instead
            start_date = datetime.strptime(csv_record['start_date'], '%Y-%m-%d').replace(month=12, day=31,
                                                                                               tzinfo=pytz.timezone(
                                                                                                   local_tz))
            ccodes = ChronologicCode.objects.filter(code_id_id__exact=code.id).filter(
                start_date__lte=start_date).filter(end_date__gte=start_date)
            if len(ccodes) > 0:
                ccode: ChronologicCode = ccodes[0]
                solr_record['minister_name_en'] = ccode.label_en
                solr_record['minister_name_fr'] = ccode.label_fr
            else:
                # Just take the last minister then
                ccodes = ChronologicCode.objects.filter(code_id_id__exact=code.id)
                if len(ccodes) > 0:
                    ccode: ChronologicCode = ccodes[0]
                    solr_record['minister_name_en'] = ccode.label_en
                    solr_record['minister_name_fr'] = ccode.label_fr
    return solr_record
