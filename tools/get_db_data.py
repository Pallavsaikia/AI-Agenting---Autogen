from database import SQLFunctions

def get_all_user_survey_data_from_database(survey_name:str,category_name:str):
    fn=SQLFunctions()
    if not category_name:
        data=fn.fetch_query_data(f'''
                            Select network_survey.name as survey_name,
        network_category.name as category,
        [user].id as user_id,
        [user].fullname as [user_name],
        opm_calculation.closeness_centrality
        from opm_calculation
        left join [user] on opm_calculation.user_id=[user].id
        left join network_survey on opm_calculation.survey_id=network_survey.id
        left join network_category on opm_calculation.category_id=network_category.id
        where network_survey.name like '{survey_name}'
        ''')
    else:
        data=fn.fetch_query_data(f'''
                            Select network_survey.name as survey_name,
        network_category.name as category,
        [user].id as user_id,
        [user].fullname as [user_name],
        opm_calculation.closeness_centrality
        from opm_calculation
        left join [user] on opm_calculation.user_id=[user].id
        left join network_survey on opm_calculation.survey_id=network_survey.id
        left join network_category on opm_calculation.category_id=network_category.id
        where network_survey.name like '{survey_name}' and network_category.name='{category_name}'
        ''')
    return data.to_json()

