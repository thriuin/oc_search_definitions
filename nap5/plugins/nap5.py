from django.http import HttpRequest
from search.models import Search, Field, Code
from SolrClient import SolrResponse


def plugin_api_version():
    return 1.1


def pre_search_solr_query(context: dict, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    solr_query['group'] = True
    solr_query['group.field'] = 'indicators'
    solr_query['group.limit'] = 1
    solr_query['group.sort'] = 'reporting_period desc'
    solr_query['group.facet'] = True
    solr_query['group.main'] = True
    return context, solr_query


def post_search_solr_query(context: dict, solr_response: SolrResponse, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_ids: str):
    return context, solr_response


def pre_record_solr_query(context: dict, solr_query: dict, request: HttpRequest, search: Search, fields: dict, codes: dict, facets: list, record_id: str):
    id_parts = record_id.split(",")
    if len(id_parts) > 1:
        solr_query['q'] = 'indicators:"{0}"'.format(id_parts[1])
        solr_query['sort'] = 'reporting_period desc'

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

    if solr_record['indicators_en']:
        solr_record['indicators_eng'] = f'{solr_record["indicators"]} - {solr_record["indicators_en"]}'
    if solr_record['indicators_fr']:
        solr_record['indicators_fra'] = f'{solr_record["indicators"]} - {solr_record["indicators_fr"]}'
    solr_record['milestones_eng'] = solr_record['milestones_en'] if solr_record['milestones_en'] else '-'
    solr_record['milestones_fra'] = solr_record['milestones_fr'] if solr_record['milestones_fr'] else '-'
    indicator = csv_record['indicators'].lower()
    if indicator in codes['indicators']:
        if codes['indicators'][indicator].extra_03 == "True":
            solr_record['s4d'] = "y"
            solr_record['s4d_en'] = codes['s4d']['y'].label_en
            solr_record['s4d_fr'] = codes['s4d']['y'].label_fr
        else:
            solr_record['s4d'] = "n"
            solr_record['s4d_en'] = codes['s4d']['n'].label_en
            solr_record['s4d_fr'] = codes['s4d']['n'].label_fr
        solr_record['due_date'] = codes['indicators'][indicator].extra_01
        if solr_record['due_date'] in codes['due_date']:
            solr_record['due_date_en'] = codes['due_date'][solr_record['due_date']].label_en
            solr_record['due_date_fr'] = codes['due_date'][solr_record['due_date']].label_fr
        else:
            solr_record['due_date_en'] = solr_record['due_date']
            solr_record['due_date_fr'] = solr_record['due_date']
        solr_record['deadline_en'] = codes['indicators'][indicator].extra_04_en
        solr_record['deadline_fr'] = codes['indicators'][indicator].extra_04_fr
    return solr_record

# Version 1.1 Methods

def pre_render_search(context: dict, template: str, request: HttpRequest, lang: str, search: Search, fields: dict, codes: dict):
    """
    If required, make changes to the context before rendering the search page or modify the template name
    :param context: the Django view context to be used
    :param template: the default name of the  template to be rendered
    :param request: the HTTP request object
    :param lang: the language of the page being rendered
    :param search: the application search object
    :param fields: the application field objects
    :param codes: the application code objects to be used
    :return: context object, and the template name
    """
    # If there is no search text and no facets, then hide the results message
    context['show_all_results'] = True
    for p in request.GET:
        if p not in ['encoding', 'page']:
            context['show_all_results'] = False
            break
    return context, template

def pre_render_record(context: dict, template: str, request: HttpRequest, lang: str, search: Search, fields: dict, codes: dict):
    """
    If required, make changes to the context before rendering the record page or modify the template name
    :param context: the Django view context to be used
    :param template: the default name of the  template to be rendered
    :param request: the HTTP request object
    :param lang: the language of the page being rendered
    :param search: the application search object
    :param fields: the application field objects
    :param codes: the application code objects to be used
    :return: context object, and the template name
    """
    return context, template
